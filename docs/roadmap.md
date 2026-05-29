## InterviewGPT Roadmap

### 1. Goals

- Deliver a production‑grade AI career growth platform with:
  - High‑quality mock interviews (text, voice, video)
  - ATS‑aware resume support
  - Structured feedback and improvement tracking
  - A personalized study plan and readiness indicator
- Maintain a clean architecture, strong security posture, and an extensible foundation for adding new AI agents and experiences.

Roadmap phases below assume iterative delivery with continuous user feedback.

### 2. Phase 0 – Foundations (Infra, Auth, Skeletons)

**Objectives**

- Stand up the core infrastructure for local and staging environments.
- Establish project structure, CI/CD, and basic observability.
- Implement secure authentication and core user profile flows.
- Align team on domain model and clean architecture boundaries.

**Scope**

- Repository setup, code quality tooling, and docs:
  - Monorepo structure (`apps/web`, `services/api`, `services/worker`, `docs`).
  - TypeScript/ESLint/Prettier, Python formatting and linting.
  - Base documentation (architecture, database, API – this folder).
- Local infra via Docker Compose:
  - Postgres, Redis, ChromaDB, Nginx reverse proxy.
- Backend scaffolding:
  - FastAPI app with layered modules, health checks, and a minimal `/me` endpoint.
  - SQLAlchemy models for core identity tables.
  - Alembic migrations pipeline.
- Frontend scaffolding:
  - Next.js 15 app with Tailwind and shadcn/ui configured.
  - Basic layout, auth pages shell (login/register).

**Exit Criteria**

- Developers can spin up the full stack locally with a single command.
- User registration, login, logout, and profile retrieval work end‑to‑end.
- Basic logs/metrics visible in staging; error tracking wired to a provider.

---

### 3. Phase 1 – Resume & ATS Experience

**Objectives**

- Deliver a compelling, high‑leverage resume experience:
  - Upload, parse, and store resumes.
  - Provide ATS‑style analysis and initial AI review.

**Scope**

- Resume domain:
  - `resumes`, `resume_sections`, `ats_reports`, `resume_reviews` tables and repositories.
  - File upload to object storage (or local in dev).
- ATS analysis pipeline:
  - Worker job to parse resumes into structured sections.
  - AI‑driven ATS analysis using Gemini (keyword matching, formatting guidance).
- Resume review agent:
  - Agent prompts and evaluation rubrics for resume quality.
  - API endpoints to request and retrieve reviews.
- Frontend:
  - Resume upload and history view.
  - ATS and review result UI with clear actions.

**Exit Criteria**

- Users can upload multiple resumes and see ATS scores and AI review within seconds/minutes.
- At least one iteration of user testing on ATS/review quality with feedback incorporated.

---

### 4. Phase 2 – Mock Interview (Text) & Evaluation

**Objectives**

- Launch text‑based mock interviews with AI interviewer and structured scoring.

**Scope**

- Interview domain:
  - `interview_templates`, `interview_sessions`, `interview_questions`, `interview_answers`, `rubrics`, `evaluations`, `feedback_reports`.
  - Session state machine (created → in_progress → completed).
- Question generation agent:
  - Templates for behavioral, system design, and generic coding questions.
  - Company and role conditioning via RAG.
- Evaluation and feedback agents:
  - Rubric definitions and agent prompts for answer evaluation.
  - Feedback synthesis (summary, strengths, weaknesses, next steps).
- API:
  - Start session, get next question, submit answer, fetch evaluation and feedback.
- Frontend:
  - Mock interview screen (text chat style) with question flow and feedback panel.

**Exit Criteria**

- Users can complete at least one high‑quality mock interview in text mode.
- Evaluations are stable and consistent across repeated sessions.

---

### 5. Phase 3 – Voice & Basic Video (Confidence Signals)

**Objectives**

- Add voice interviews with transcription and basic webcam‑based confidence signals.

**Scope**

- Voice:
  - Integrate Whisper for transcription via worker jobs.
  - Integrate ElevenLabs for AI interviewer voice playback and optional feedback narration.
  - WebSocket or chunked upload flow for audio.
- Video:
  - Client capture of frames or low‑rate video stream (MVP).
  - Backend analysis with OpenCV/MediaPipe:
    - Gaze/head pose stability.
    - Simple engagement proxies (e.g., looking away, large movements).
  - `confidence_signals` table and metrics.
- UI:
  - Voice mode toggle in interview screen.
  - Visualizations for confidence metrics (charts in post‑interview view).

**Exit Criteria**

- Users can choose a voice interview mode and receive accurate transcripts.
- Confidence metrics are computed and visualized in the session results.

---

### 6. Phase 4 – Coding Round Simulator & AI Coding Evaluator

**Objectives**

- Provide a coding interview environment with AI‑assisted evaluation.

**Scope**

- Domain:
  - Coding session entities, problem catalog (initially static), submission results.
  - Extensions to existing interview templates for coding rounds.
- Backend:
  - APIs to start coding sessions, submit solutions, and retrieve results.
  - Sandbox integration for running tests (isolated environment, later hardened).
  - AI evaluator for style, complexity, and edge‑case reasoning using Gemini.
- Frontend:
  - Coding IDE‑like experience (editor, input/output, timer).
  - Results and feedback visualization.

**Exit Criteria**

- Users can complete at least one coding round and see code run against tests with AI feedback.
- No uncontained code execution or sandbox escape paths in initial implementation.

---

### 7. Phase 5 – RAG Knowledge Base & Company‑Specific Interviews

**Objectives**

- Build robust RAG pipelines backing:
  - Company‑specific interviews.
  - Career advisor answers.
  - Study resources recommendations.

**Scope**

- RAG ingestion:
  - Pipelines to ingest company handbooks, job descriptions, and curated resources.
  - Chunking and embedding into ChromaDB with namespaces.
- Retrieval:
  - Tools for agents to query company/user/global namespaces.
  - Guardrails against prompt injection via retrieved content.
- Company‑specific interviews:
  - Templates and agent prompts tuned per company/role.
  - Query company namespace for up‑to‑date patterns.

**Exit Criteria**

- Users can select a target company and experience noticeable company‑specific tailoring in questions and feedback.
- RAG reliability validated with evaluation datasets.

---

### 8. Phase 6 – Improvement Tracking, Readiness Predictor, and Study Planner

**Objectives**

- Close the loop from sessions to measurable progress and actionable plans.

**Scope**

- Improvement tracking:
  - Populate `session_events`, `improvement_metrics`, and `readiness_snapshots`.
  - Trend computation jobs (e.g., rolling averages).
- Readiness predictor:
  - Initial rule‑based predictor using evaluation scores and recency/frequency features.
  - API and UI cards for “placement readiness”.
- Study planner:
  - Study plan and task models and APIs.
  - Planner agent to generate and adjust plans from gaps and user constraints.
  - Dashboard integrating tasks, progress, and readiness.

**Exit Criteria**

- Users see clear trend lines for key skills and an overall readiness score.
- Study plans update sensibly as users complete tasks and perform new interviews.

---

### 9. Phase 7 – Admin Dashboard, Analytics, and Hardening

**Objectives**

- Support operations, monitoring, and continuous improvement.

**Scope**

- Admin dashboard:
  - User overview, feature usage, and error hotspots.
  - Audit log viewer and simple feature flag management.
- Analytics:
  - User KPIs (sessions per week, improvement deltas).
  - System metrics dashboards (API P95, model cost, job latencies).
- Hardening:
  - Security review and penetration tests.
  - Data retention policies finalized and implemented.
  - Rate limits and abuse detection tuned.

**Exit Criteria**

- Admins can safely manage the platform and monitor health.
- The system withstands typical scale and attack patterns for a modern SaaS.

---

### 10. Continuous Improvements

- Iterative tuning of prompts, rubrics, and agents based on user outcomes.
- A/B testing of interview formats and feedback styles.
- Evolving the modular monolith into service boundaries as scale demands (media, RAG, analytics).

This roadmap gives a pragmatic, phased path from foundational infrastructure to a rich, AI‑powered interview and career growth platform while preserving architectural integrity and room to evolve.

