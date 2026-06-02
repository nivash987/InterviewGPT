import { assertApiSuccess } from "@/lib/errors";
import type { ApiResponse } from "@/types/api";
import type {
  LoginCredentials,
  RegisterCredentials,
  RegisterResponse,
  TokenPair,
} from "@/types/auth";

import { apiClient } from "./client";

export const authService = {
  async login(credentials: LoginCredentials): Promise<TokenPair> {
    const { data } = await apiClient.post<ApiResponse<TokenPair>>(
      "/auth/login",
      credentials,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async register(credentials: RegisterCredentials): Promise<RegisterResponse> {
    const { data } = await apiClient.post<ApiResponse<RegisterResponse>>(
      "/auth/register",
      {
        email: credentials.email,
        password: credentials.password,
        full_name: credentials.full_name || null,
      },
    );
    assertApiSuccess(data);
    return data.data;
  },

  async refresh(refreshToken: string): Promise<TokenPair> {
    const { data } = await apiClient.post<ApiResponse<TokenPair>>(
      "/auth/refresh",
      { refresh_token: refreshToken },
    );
    assertApiSuccess(data);
    return data.data;
  },

  async logout(refreshToken?: string | null): Promise<void> {
    const { data } = await apiClient.post<ApiResponse<{ message: string }>>(
      "/auth/logout",
      { refresh_token: refreshToken ?? null },
    );
    assertApiSuccess(data);
  },

  async verifyEmail(token: string): Promise<{ message: string }> {
    const { data } = await apiClient.post<ApiResponse<{ message: string }>>(
      "/auth/verify-email",
      { token },
    );
    assertApiSuccess(data);
    return data.data;
  },

  async resendVerification(email: string): Promise<{ message: string }> {
    const { data } = await apiClient.post<ApiResponse<{ message: string }>>(
      "/auth/resend-verification",
      { email },
    );
    assertApiSuccess(data);
    return data.data;
  },
};
