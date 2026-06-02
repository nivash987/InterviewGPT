import { NextResponse, type NextRequest } from "next/server";

import { env } from "@/config/env";
import { AUTH_ROUTES, PROTECTED_ROUTE_PREFIXES, ROUTES } from "@/constants/routes";

function isProtectedPath(pathname: string): boolean {
  return PROTECTED_ROUTE_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

function isAuthPage(pathname: string): boolean {
  return AUTH_ROUTES.some((route) => pathname === route);
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get(env.accessTokenCookie)?.value;

  if (isProtectedPath(pathname) && !accessToken) {
    const loginUrl = new URL(ROUTES.login, request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isAuthPage(pathname) && accessToken) {
    return NextResponse.redirect(new URL(ROUTES.dashboard, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/resumes",
    "/resumes/:path*",
    "/ats",
    "/ats/:path*",
    "/interviews",
    "/interviews/:path*",
    "/jobs",
    "/jobs/:path*",
    "/career-coach",
    "/career-coach/:path*",
    "/roadmap",
    "/roadmap/:path*",
    "/readiness",
    "/readiness/:path*",
    "/login",
    "/register",
    "/verify-email",
    "/check-email",
  ],
};
