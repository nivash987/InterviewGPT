import axios, {
  AxiosHeaders,
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

import { env } from "@/config/env";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "@/lib/auth/tokens";
import { parseApiError } from "@/lib/errors";
import type { ApiResponse } from "@/types/api";
import type { TokenPair } from "@/types/auth";

type RetryableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearTokens();
    return null;
  }

  try {
    const { data } = await axios.post<ApiResponse<TokenPair>>(
      `${env.apiUrl}/auth/refresh`,
      { refresh_token: refreshToken },
      { headers: { "Content-Type": "application/json" } },
    );

    if (!data.ok) {
      clearTokens();
      return null;
    }

    setTokens(data.data);
    return data.data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

function getRefreshPromise(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

function ensureAxiosHeaders(config: InternalAxiosRequestConfig): AxiosHeaders {
  if (config.headers instanceof AxiosHeaders) {
    return config.headers;
  }
  const headers = AxiosHeaders.from(config.headers ?? {});
  config.headers = headers;
  return headers;
}

function applyAccessToken(config: InternalAxiosRequestConfig, token: string): void {
  ensureAxiosHeaders(config).set("Authorization", `Bearer ${token}`);
}

export function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: env.apiUrl,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    timeout: 30_000,
  });

  client.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
      applyAccessToken(config, token);
    }

    if (typeof FormData !== "undefined" && config.data instanceof FormData) {
      ensureAxiosHeaders(config).delete("Content-Type");
    }

    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError<ApiResponse<unknown>>) => {
      const original = error.config as RetryableConfig | undefined;
      const status = error.response?.status;

      if (
        status === 401 &&
        original &&
        !original._retry &&
        !original.url?.includes("/auth/login") &&
        !original.url?.includes("/auth/register") &&
        !original.url?.includes("/auth/refresh")
      ) {
        original._retry = true;
        const newToken = await getRefreshPromise();

        if (newToken) {
          applyAccessToken(original, newToken);
          return client.request(original);
        }
      }

      return Promise.reject(parseApiError(error));
    },
  );

  return client;
}

export const apiClient = createApiClient();
