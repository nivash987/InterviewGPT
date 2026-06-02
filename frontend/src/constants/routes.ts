export const ROUTES = {
  home: "/",
  login: "/login",
  register: "/register",
  verifyEmail: "/verify-email",
  checkEmail: "/check-email",
  dashboard: "/dashboard",
  resumes: "/resumes",
  ats: "/ats",
  interviews: "/interviews",
  jobs: "/jobs",
  careerCoach: "/career-coach",
  roadmap: "/roadmap",
  readiness: "/readiness",
} as const;

export const AUTH_ROUTES = [ROUTES.login, ROUTES.register, ROUTES.verifyEmail, ROUTES.checkEmail] as const;

export const PROTECTED_ROUTE_PREFIXES = [
  "/dashboard",
  "/resumes",
  "/ats",
  "/interviews",
  "/jobs",
  "/career-coach",
  "/roadmap",
  "/readiness",
] as const;

export const PUBLIC_ONLY_WHEN_AUTHENTICATED = AUTH_ROUTES;
