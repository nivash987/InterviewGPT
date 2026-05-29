# InterviewGPT Frontend

Next.js 15 application shell with JWT authentication, protected routes, and a dashboard layout.

## Stack

- Next.js 15 (App Router)
- React 19 + TypeScript
- Tailwind CSS + shadcn/ui (New York style)
- Axios API client with token refresh
- React Hook Form + Zod validation

## Getting started

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` to your FastAPI base (default `http://localhost:8000/api`).

Ensure the backend allows the frontend origin in `APP_ALLOWED_ORIGINS` (e.g. `http://localhost:3000`).

## Folder structure

```
frontend/
├── src/
│   ├── app/                    # App Router pages & layouts
│   │   ├── (auth)/             # Login, register
│   │   ├── (dashboard)/        # Protected dashboard
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Landing page
│   │   └── globals.css
│   ├── components/
│   │   ├── auth/               # Login/register forms
│   │   ├── common/             # Logo, spinner, page header
│   │   ├── layout/             # Site header, auth layout, dashboard shell
│   │   └── ui/                 # shadcn primitives
│   ├── config/                 # Environment helpers
│   ├── constants/              # Route constants
│   ├── hooks/                  # useAuth
│   ├── lib/
│   │   ├── auth/               # JWT cookie helpers
│   │   └── validations/        # Zod schemas
│   ├── middleware.ts           # Protected route guard
│   ├── providers/              # AuthProvider
│   ├── services/api/           # Axios client + auth/users services
│   └── types/                  # API & auth TypeScript types
├── components.json             # shadcn CLI config
├── tailwind.config.ts
└── package.json
```

## Authentication flow

1. **Login / register** → `authService` calls `/auth/login` or `/auth/register`.
2. **Tokens** stored in cookies (`igpt_access_token`, `igpt_refresh_token`) via `js-cookie`.
3. **Axios** attaches `Authorization: Bearer <access_token>`; on 401, refreshes via `/auth/refresh`.
4. **Middleware** blocks `/dashboard/*` without an access-token cookie; redirects authenticated users away from `/login` and `/register`.
5. **AuthProvider** loads `/users/me` on bootstrap for client-side user state.

## Scripts

| Command       | Description        |
|---------------|--------------------|
| `npm run dev` | Development server |
| `npm run build` | Production build |
| `npm run start` | Production server |
| `npm run lint` | ESLint |

## Out of scope (this foundation)

- Resume upload
- ATS analysis
- Interview sessions / WebSockets

These will extend the dashboard and `services/api` layer when implemented.
