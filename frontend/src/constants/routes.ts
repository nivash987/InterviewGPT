export const ROUTES = {
  home: "/",
  login: "/login",
  register: "/register",
  dashboard: "/dashboard",
  resumes: "/resumes",
  ats: "/ats",
} as const;

export const AUTH_ROUTES = [ROUTES.login, ROUTES.register] as const;

export const PROTECTED_ROUTE_PREFIXES = ["/dashboard", "/resumes", "/ats"] as const;

export const PUBLIC_ONLY_WHEN_AUTHENTICATED = AUTH_ROUTES;
