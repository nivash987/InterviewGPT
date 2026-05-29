import type { AxiosError } from "axios";

import { isApiError, type ApiErrorResponse, type ApiResponse } from "@/types/api";

export class ApiClientError extends Error {
  readonly code: string;
  readonly status?: number;
  readonly field?: string | null;

  constructor(
    message: string,
    options: { code?: string; status?: number; field?: string | null } = {},
  ) {
    super(message);
    this.name = "ApiClientError";
    this.code = options.code ?? "unknown_error";
    this.status = options.status;
    this.field = options.field;
  }
}

export function getErrorMessage(error: unknown, fallback = "Something went wrong"): string {
  if (error instanceof ApiClientError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallback;
}

export function parseApiError(
  error: AxiosError<ApiResponse<unknown>>,
): ApiClientError {
  const status = error.response?.status;
  const body = error.response?.data;

  if (body && isApiError(body)) {
    return new ApiClientError(body.error.message, {
      code: body.error.code,
      status,
      field: body.error.field,
    });
  }

  if (error.message === "Network Error") {
    return new ApiClientError("Unable to reach the server. Check your connection.", {
      code: "network_error",
      status,
    });
  }

  return new ApiClientError(error.message || "Request failed", {
    code: "request_failed",
    status,
  });
}

export function assertApiSuccess<T>(
  response: ApiResponse<T>,
): asserts response is { ok: true; data: T } {
  if (isApiError(response)) {
    throw new ApiClientError(response.error.message, {
      code: response.error.code,
      field: response.error.field,
    });
  }
}

export type { ApiErrorResponse };
