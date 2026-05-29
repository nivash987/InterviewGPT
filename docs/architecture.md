## InterviewGPT Architecture

### 1. Overview

InterviewGPT is an AI‑driven career growth and interview preparation platform. The system is designed as a modular monolith (initially) with clear boundaries that can evolve into microservices over time, following clean architecture principles.

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI (Python 3.12), SQLAlchemy, Alembic
- **Datastores**: PostgreSQL (OLTP), ChromaDB (vector store), Redis (cache + ephemeral state)
- **AI & Media**: Gemini API via LangChain, Whisper, ElevenLabs, OpenCV, MediaPipe
- **Deployment**: Docker + Docker Compose (Kubernetes‑ready later)

The primary concerns of the architecture are: separation of concerns, scalability, resilience, observability, and security.

### 2. Clean Architecture Layers

The backend services follow a layered, ports‑and‑adapters style architecture:

- **Domain layer**
  - Pure business concepts: entities (User, Resume, InterviewSession, Question, Answer, Evaluation, StudyPlan, etc.), value objects, domain services, and invariants.
  - No dependency on web frameworks, databases, or AI providers.
- **Application layer**
  - Use‑cases / interactors implementing workflows (e.g., `StartMockInterview`, `GenerateInterviewQuestions`, `EvaluateAnswer`, `GenerateStudyPlan`, `PredictReadiness`).
  - Orchestrates domain objects and calls into ports for persistence, messaging, cache, vector store, and AI tools.
  - Contains DTOs and mappers between domain and interface representations.
- **Infrastructure layer**
  - Adapters for external systems:
    - PostgreSQL via SQLAlchemy repositories
    - Redis cache, rate‑limit and job metadata stores
    - ChromaDB client for vector storage and retrieval
    - Gemini / LangChain agents and tools
    - Whisper, ElevenLabs, OpenCV, MediaPipe integrations
  - Implements interfaces defined in the application/domain layers.
- **Interfaces layer**
  - FastAPI routers/controllers (REST + WebSocket)
  - Request/response schemas (Pydantic models)
  - Serialization, authentication, and validation at the boundary.

This separation allows independent evolution of UI, business rules, and infrastructure, and provides a clear path to extract microservices around stable boundaries.

### 3. High‑Level Component Diagram

Main runtime components:

- **Web App (Next.js 15)**
  - User and admin UIs for:
    - Account management and onboarding
    - Resume upload and analysis
    - Mock interviews (text, voice, video)
    - Coding round simulator
    - Dashboards, feedback, and study planner
  - Communicates with the backend via REST and WebSockets.

- **API Service (FastAPI)**
  - Single entrypoint for client applications.
  - Hosts HTTP REST endpoints and WebSocket endpoints for realtime interview sessions.
  - Contains application and domain logic for:
    - Authentication and authorization
    - Resume management and ATS analysis orchestration
    - Interview session lifecycle (creation, question flow, answer capture)
    - Evaluation and feedback orchestration
    - Career advising and study planning
    - Analytics and admin features
  - Delegates long‑running or compute‑heavy tasks to worker processes.

- **Worker Service**
  - Runs background jobs:
    - Resume parsing and ATS scoring
    - Text embedding and ChromaDB indexing
    - Document ingestion for RAG
    - Audio transcription via Whisper
    - TTS via ElevenLabs
    - Video stream analysis with OpenCV/MediaPipe
    - Batch evaluations and analytics calculations
  - Communicates with API service through shared database, Redis, and (optionally) a job queue abstraction on top of Redis.

- **PostgreSQL**
  - Primary system of record for:
    - Users, auth, roles, permissions
    - Resumes, ATS reports, resume reviews
    - Interview templates, sessions, questions, answers
    - Evaluations, feedback, rubrics
    - Study plans and improvement metrics
    - Analytics events and audit logs

- **Redis**
  - Short‑lived cache for:
    - Access tokens / session metadata (if using server‑side sessions)
    - Rate limiting and abuse protection counters
    - Ephemeral interview state and WebSocket session mappings
    - Background job metadata and progress tracking

- **ChromaDB**
  - Vector store for:
    - RAG knowledge bases (global, company‑specific, user‑specific)
    - Embedded resume snippets and interview history
    - Semantic search across documents and previous answers.

- **AI & Media Providers**
  - Gemini (via LangChain) for:
    - ATS resume feedback and rewriting
    - Question generation
    - Answer evaluation and rubric‑based scoring
    - Feedback synthesis and career advising
    - Study plan generation and readiness prediction logic (hybrid with rules/models)
  - Whisper for speech‑to‑text in voice interviews.
  - ElevenLabs for text‑to‑speech (AI interviewer voice, feedback narration).
  - OpenCV + MediaPipe for webcam confidence and engagement analysis.

### 4. Logical Module Breakdown

Within the API service:

- `auth` module
  - Registration, login, token management, password reset (if applicable).
  - OIDC integration (future).
  - Role and permission checking.
- `resume` module
  - Upload and storage metadata.
  - Parsing, normalization, and ATS scoring orchestration.
  - Integration with resume review and RAG (embedding relevant resume parts).
- `interview` module
  - Interview template definitions and company‑specific configurations.
  - Session lifecycle (create → start → ask question → capture answer → complete).
  - Supports text‑only, voice, and video modes.
- `evaluation` module
  - Rubric definitions and versioning.
  - Answer‑level and session‑level evaluation.
  - Feedback summarization and improvement tracking signals.
- `planner` module
  - Career goals.
  - Study plan creation and updates based on evaluation history.
  - Task management and reminders (integration ready).
- `analytics` module
  - User‑level and system‑level metrics.
  - Data for dashboards and readiness predictor.
- `admin` module
  - User management, audit log views.
  - Feature flags and configuration for experiments.

These modules share the domain and application layers but keep their interfaces and infrastructure adapters cohesive.

### 5. Realtime and Media Architecture

- **Realtime**
  - WebSocket endpoints exposed via FastAPI for:
    - Mock interview live sessions (question events, answer events, typing indicators).
    - Streaming AI feedback during and after answers (tokens/partial results).
  - Redis used for session and connection coordination if multiple API instances.

- **Voice**
  - Audio chunks uploaded/streamed from the client to the API service.
  - API or worker passes audio to Whisper for transcription.
  - Transcribed text stored and passed to evaluation agents.
  - ElevenLabs generates synthesized interviewer questions or feedback as audio for the client.

- **Video**
  - Client captures key frames or low‑frequency video stream (depending on bandwidth constraints).
  - Server runs OpenCV/MediaPipe pipelines:
    - Face detection, gaze, head pose, basic affect proxies.
  - Derived metrics (attention, confidence, stability) stored as per‑answer/per‑session signals.

### 6. Scalability & Evolution

- **Horizontal scaling**
  - Stateless API instances behind a load balancer.
  - Worker processes scaled based on job throughput and latency SLAs.
  - Database and vector store sized and tuned independently.

- **Service decomposition (future)**
  - RAG/knowledge base service.
  - Media/transcription service.
  - Analytics/readiness predictor service.
  - Each new service reuses the same domain contracts via shared packages.

- **Resilience**
  - Circuit breakers and timeouts for external AI/media APIs.
  - Idempotent jobs and retriable workflows.
  - Dead‑letter queues for failed jobs (on top of Redis, or a dedicated queue later).

### 7. Observability & Operations

- **Logging**
  - Structured JSON logs with correlation/trace IDs.
  - Separate channels for access logs, application logs, and security/audit logs.
- **Metrics**
  - API latency, error rates, job queue depths, model call counts, cost estimates.
  - Business KPIs (interview completion rates, improvement deltas, readiness distributions).
- **Tracing**
  - OpenTelemetry instrumentation from incoming HTTP/WebSocket requests through AI and worker calls.
  - Traces link user interactions to model calls and database queries.

This architecture provides a solid foundation to implement and evolve the 22 core features of InterviewGPT while keeping the system maintainable, secure, and scalable.

