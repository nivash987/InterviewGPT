import Cookies from "js-cookie";

import { env } from "@/config/env";
import type { TokenPair } from "@/types/auth";

const COOKIE_OPTIONS = {
  sameSite: "lax" as const,
  secure: process.env.NODE_ENV === "production",
  path: "/",
};

export function getAccessToken(): string | undefined {
  return Cookies.get(env.accessTokenCookie);
}

export function getRefreshToken(): string | undefined {
  return Cookies.get(env.refreshTokenCookie);
}

export function setTokens(tokens: TokenPair): void {
  Cookies.set(env.accessTokenCookie, tokens.access_token, COOKIE_OPTIONS);
  Cookies.set(env.refreshTokenCookie, tokens.refresh_token, COOKIE_OPTIONS);
}

export function clearTokens(): void {
  Cookies.remove(env.accessTokenCookie, { path: "/" });
  Cookies.remove(env.refreshTokenCookie, { path: "/" });
}

export function hasAccessToken(): boolean {
  return Boolean(getAccessToken());
}
