const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export const env = {
  apiUrl: apiUrl.replace(/\/$/, ""),
  accessTokenCookie:
    process.env.NEXT_PUBLIC_ACCESS_TOKEN_COOKIE ?? "igpt_access_token",
  refreshTokenCookie:
    process.env.NEXT_PUBLIC_REFRESH_TOKEN_COOKIE ?? "igpt_refresh_token",
  isDev: process.env.NODE_ENV === "development",
} as const;
