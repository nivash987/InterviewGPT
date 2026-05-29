export interface ApiErrorDetail {
  code: string;
  message: string;
  field?: string | null;
  meta?: Record<string, unknown> | null;
}

export interface ApiSuccessResponse<T> {
  ok: true;
  data: T;
  request_id?: string | null;
  ts?: string;
}

export interface ApiErrorResponse {
  ok: false;
  error: ApiErrorDetail;
  request_id?: string | null;
  ts?: string;
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

export function isApiError(response: ApiResponse<unknown>): response is ApiErrorResponse {
  return response.ok === false;
}
