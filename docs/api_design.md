## InterviewGPT API Design

### 1. Principles

- **HTTP/JSON REST** APIs for core operations, with **WebSockets** for realtime interview experiences.
- **Versioned** endpoints (`/api/v1/...`) and structured response envelopes.
- **Clean separation** of transport (FastAPI routers) from application use‑cases and domain models.
- **Idempotent, side‑effect‑safe** operations where possible; explicit job resources for long‑running tasks.
- **Consistent error model** and pagination patterns.

The public API consumed by the Next.js frontend is intentionally coarse‑grained around use‑cases (start interview, submit answer, generate plan) rather than low‑level CRUD.

### 2. Conventions

- Base URL (example): `/api/v1`
- Authentication: Bearer JWT in `Authorization` header, or secure HttpOnly cookie for browser clients.
- Standard response envelope:
  - Success: `{ "data": <payload>, "meta": { ... } }`
  - Error: `{ "error": { "code": "string", "message": "string", "details": { ... } } }`
- Pagination:
  - Query params: `page`, `page_size` or `cursor`, `limit`
  - Response: `meta` includes `page`, `page_size`, `total` or `next_cursor`.
- Long‑running tasks:
  - Immediate `202 Accepted` with `{ "job_id": "..." }`
  - `GET /jobs/{job_id}` returns `status` (pending, running, completed, failed) and `result` when available.

### 3. Authentication & User Management

**Endpoints**

- `POST /auth/register`
  - Body: `email`, `password`, optional profile fields.
  - Response: user summary + tokens (or verification flow).

- `POST /auth/login`
  - Body: `email`, `password`
  - Response: access token, refresh token (or cookies).

- `POST /auth/refresh`
  - Body: refresh token (if not cookie‑based).
  - Response: new access token (+ refreshed refresh token).

- `POST /auth/logout`
  - Invalidates the current session/refresh token.

- `GET /me`
  - Returns current user profile and key flags (e.g., onboarding status, primary resume id).

### 4. Resume & ATS APIs

- `POST /resumes/upload`
  - Multipart upload (`file` + optional `title`).
  - Response: `{ "data": { "resume_id": "...", "job_id": "..." } }`
  - Triggers async parsing + ATS analysis.

- `GET /resumes`
  - List user resumes.

- `GET /resumes/{resume_id}`
  - Returns metadata, latest ATS scores, and last review summary.

- `POST /resumes/{resume_id}/ats-analysis`
  - Body: optional `job_description` or `job_description_file`.
  - Response: `202` with `job_id`.

- `POST /resumes/{resume_id}/review`
  - Body: parameters like `target_role`, `target_level`.
  - Response: `202` with `job_id`.

- `GET /resumes/{resume_id}/ats-reports`
  - Lists past ATS reports.

- `GET /resumes/{resume_id}/reviews`
  - Lists past AI resume reviews.

### 5. RAG & Knowledge Base APIs

- `POST /kb/documents`
  - Multipart upload or URL.
  - Body: `namespace` (global, company:{id}, user), metadata.
  - Response: `job_id` for ingestion (parse → chunk → embed → index).

- `GET /kb/documents`
  - Query by namespace, tags, etc.

- `GET /kb/search`
  - Query params: `namespace`, `q`, optional filters.
  - Response: list of chunks with `text`, `score`, `source`.

These APIs are primarily used by internal tools and admin features, but some user‑visible features (e.g., personal notes) can use the `user` namespace.

### 6. Interview & Question APIs

#### 6.1 Session Management

- `POST /interviews/sessions`
  - Body:
    - `template_id` or `type` (behavioral, system_design, coding, mixed)
    - optional `company_id`, `target_role`, `target_level`, `mode` (text, voice, video)
  - Response: new session with initial state.

- `POST /interviews/sessions/{session_id}/start`
  - Transitions from `created` to `in_progress`.
  - Can pre‑generate first question(s).

- `GET /interviews/sessions`
  - List sessions for the current user, with filters (status, type, date range).

- `GET /interviews/sessions/{session_id}`
  - Detailed view including questions, answers, evaluations, and feedback (subject to access rules).

#### 6.2 Question Flow

- `POST /interviews/sessions/{session_id}/next-question`
  - Body: optional context such as `previous_answer_id`, `feedback_preference`.
  - Response: `{ question: { ... } }`
  - Uses Question Generator Agent with RAG and session context.

- `GET /interviews/sessions/{session_id}/questions`
  - Returns ordered list of questions and minimal metadata.

#### 6.3 Answer Submission

- `POST /interviews/sessions/{session_id}/answers`
  - For text answers:
    - Body: `{ "question_id": "...", "answer_text": "..." }`
  - For voice/video:
    - Multipart with `question_id` and `audio`/`video` file.
  - Response: created answer entry and `job_id` for follow‑up evaluation if enabled.

- `GET /interviews/sessions/{session_id}/answers`
  - List answers with basic evaluation summaries (if completed).

### 7. Evaluation & Feedback APIs

- `POST /evaluations/answers/{answer_id}`
  - Triggers explicit re‑evaluation of a specific answer.
  - Body: optional `rubric_id` or `agent_version`.
  - Response: `job_id`.

- `GET /evaluations/answers/{answer_id}`
  - Returns all evaluations for the answer (with rubric details).

- `GET /evaluations/sessions/{session_id}`
  - Returns aggregated session‑level evaluation (overall score, per‑dimension scores).

- `GET /feedback/sessions/{session_id}`
  - Returns detailed feedback report with:
    - Summary
    - Strengths
    - Weaknesses
    - Recommended next steps

These endpoints are backed by AI agents but expose stable, typed outputs to the frontend.

### 8. Coding Round & AI Coding Evaluator APIs

- `POST /coding/sessions`
  - Body: `difficulty`, `topic`, `language`, `time_limit`, optional `company_id`.
  - Response: coding session with initial problem statement and constraints.

- `GET /coding/sessions/{session_id}`
  - Returns problem, examples, status, and prior attempts.

- `POST /coding/sessions/{session_id}/submit`
  - Body:
    - `code`
    - `language`
  - Server runs:
    - Static checks (language‑specific)
    - Test execution in sandbox (future)
    - AI coding evaluation (correctness, complexity, style)
  - Response: `job_id` for evaluation.

- `GET /coding/sessions/{session_id}/results`
  - Returns execution results, AI evaluation, and suggestions.

### 9. Career Advisor, Planner, and Readiness APIs

- `POST /advisor/session`
  - Body: `target_company`, `target_role`, `time_horizon`, current experience summary.
  - Response: advisor session id and initial recommendations.

- `GET /advisor/session/{id}`
  - Returns structured advice, typical paths, and curated resources.

- `POST /planner/generate`
  - Body:
    - `goal`
    - `target_role`, `target_level`
    - optional constraints (hours per week, deadline)
  - Uses Study Planner Agent with evaluations and RAG.
  - Response: generated `study_plan` object.

- `GET /planner/current`
  - Get active study plan and tasks for the current user.

- `PATCH /planner/tasks/{task_id}`
  - Update task status (e.g., mark complete).

- `GET /readiness/predict`
  - Computes or returns cached readiness snapshot:
    - `score` (0–100)
    - `factors` (skills, recent improvements, coverage)

### 10. Voice & Video APIs

- `POST /media/transcribe`
  - Multipart with `audio` file or streaming counterpart via WebSocket.
  - Body: `language`, `mode` (interview_answer, note).
  - Response: transcription text or `job_id` for large files.

- `POST /media/tts`
  - Body: `text`, `voice_profile`, `speed`.
  - Response: audio file/URL.

- `POST /vision/analyze`
  - Multipart with `video` or image sequence.
  - Response: confidence and engagement metrics for charting.

### 11. Realtime Interview APIs (WebSocket)

WebSocket endpoint(s), e.g.:

- `WS /interviews/sessions/{session_id}/stream`
  - Client → Server events:
    - `join`, `leave`
    - `answer_started`, `answer_partial`, `answer_completed`
    - `audio_chunk`, `ping`
  - Server → Client events:
    - `question_updated`
    - `feedback_partial`, `feedback_final`
    - `timer_update`
    - `system_message` (e.g., connectivity issues)

Messages use a small envelope like:

```json
{ "type": "event_type", "payload": { ... } }
```

Redis is used to maintain session/connection state across API instances if horizontally scaled.

### 12. Analytics & Admin APIs

- `GET /analytics/overview`
  - High‑level metrics for the current user (practice volume, improvement trends).

- `GET /analytics/sessions`
  - Filtered analytics for a user’s sessions.

- `GET /admin/users`
  - Paginated user list with filters; admin‑only.

- `GET /admin/audit-logs`
  - Paginated audit logs with filters; admin‑only.

- `GET /admin/feature-flags`
  - List of flags and current states.

- `POST /admin/feature-flags`
  - Create/update feature flags.

### 13. Error Handling & Security

- **Error responses** always include:
  - `code` (stable, machine‑friendly)
  - `message` (user‑readable, safe)
  - optional `details` (field errors, debug hints for non‑prod)

- **Security**
  - All state‑changing endpoints require authentication.
  - RBAC enforced in application layer; routers are thin.
  - Rate limiting enforced at gateway and in app (via Redis).
  - Input validation via Pydantic and additional domain‑level checks.

This API surface is intentionally high‑level and oriented around InterviewGPT’s main user journeys, while mapping cleanly to application use‑cases in the backend.

