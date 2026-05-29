# InterviewGPT Backend (FastAPI)

This folder contains the **production-ready backend foundation** for InterviewGPT.

## Architecture

- **Clean Architecture-ish layering**
  - `app/core`: cross-cutting concerns (config, logging, middleware, error handling)
  - `app/api`: HTTP layer (routers, dependencies)
  - `app/modules/*`: feature modules (ports + service layer + API)
  - `app/db`: database session wiring and base repository abstractions

## Quick start (later)

This repo currently includes **only the foundation**. Business logic, models, and migrations will be added next.

