# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Frontend (`front_end/`)
```bash
npm run dev        # Start Vite dev server (http://localhost:5173)
npm run build      # TypeScript check + Vite production build
npm run lint       # ESLint
npm run preview    # Preview production build
```

### Backend Services (each in `services/api-gateway/`, `services/cv-service/`, `services/agent-service/`)
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000   # api-gateway
uvicorn main:app --reload --port 8001   # cv-service
uvicorn main:app --reload --port 8002   # agent-service
```

### Full Stack (local)
```bash
cd infra && docker compose up --build   # Starts all services + PostgreSQL + Redis
```

### Database Migrations (Alembic, run inside each service directory)
```bash
alembic upgrade head          # Apply migrations
alembic revision --autogenerate -m "description"  # Generate new migration
```

## Architecture

This is a microservices monorepo. The **frontend only talks to the API Gateway**; it never calls CV Service or Agent Service directly.

```
front_end/  (React 19 + TypeScript + Vite)
    ↓  Bearer JWT (Auth0)
services/api-gateway/   (FastAPI, port 8000 — public)
    ↓  httpx internal calls
services/cv-service/    (FastAPI, port 8001 — internal only)
services/agent-service/ (FastAPI, port 8002 — internal only)
    ↓
PostgreSQL 15 + Redis 7
```

### Service Responsibilities

| Service | Responsibility |
|---------|---------------|
| **api-gateway** | Public REST API, JWT auth, job CRUD, user/org management, Gemini JD parsing, proxies CV/agent calls |
| **cv-service** | PDF ingestion via PyMuPDF, S3 upload (boto3), CV extraction via OpenAI + Instructor structured output |
| **agent-service** | AI orchestration for candidate-to-job matching |

### Authentication Flow
- Auth0 issues JWTs to the frontend
- Every API request includes `Authorization: Bearer <jwt>`
- `get_current_principal()` FastAPI dependency (in api-gateway) validates tokens on every protected route

### Key Data Models (api-gateway)
`User` → belongs to `Organization` → owns `Job` listings → receives `Application`s linked to `Candidate` CVs. Models live in `services/api-gateway/models/`.

### AI Stack
- **Google Gemini** (`google-genai` SDK, model configurable via `GEMINI_MODEL` env var, default `gemini-2.5-flash`): JD parsing in api-gateway
- **OpenAI + Instructor**: Structured CV extraction in cv-service

### Environment Variables
Each service reads from its own `.env` file. Key variables:
- `DATABASE_URL` — shared PostgreSQL instance (both api-gateway and cv-service hit the same DB)
- `REDIS_URL` — shared Redis
- `GEMINI_API_KEY` / `GEMINI_MODEL` — api-gateway
- `CV_SERVICE_URL` / `AGENT_SERVICE_URL` — api-gateway → internal service routing
- `VITE_API_URL` — frontend (defaults to `/api`)
- Auth0: `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`, `AUTH0_CLIENT_ID`, role-based claims

### Deployment
- **api-gateway + frontend**: EC2 behind Nginx, deployed via GitHub Actions on `api-gateway-v*` / `frontend-v*` git tags
- **cv-service**: AWS ECS Fargate, images pushed to ECR, deployed on `api-gateway-v*` tags
- Frontend build output is served statically; Nginx proxies `/api/*` to the gateway

## Architecture Rules and Safety

### Service Ownership

| Concern | Owner |
|---------|-------|
| Auth0 JWT validation, public API, job/candidate entities | **api-gateway** |
| CV upload, S3 storage, text extraction, structured CV output | **cv-service** |
| JD scoring, CV vs JD comparison, AI orchestration pipeline | **agent-service** |

### Cross-Service Communication
- Services communicate via HTTP only (`CV_SERVICE_URL`, `AGENT_SERVICE_URL`)
- No direct cross-service database joins
- Shared PostgreSQL uses schema-per-service: `public` (api-gateway), `cv_schema` (cv-service)
- No cross-schema foreign keys -- store external IDs as plain UUID columns; validate at application level
- Internal service ports must not be published publicly

### Alembic
- Each service has its own Alembic under `services/{service}/alembic/`
- Each service must use a distinct `version_table` in `alembic/env.py` (e.g. `cv_alembic_version`)
- Never auto-delete or rewrite migration files

### Actions Requiring Explicit Approval
- Deleting any files or folders
- Modifying `infra/` or any Docker configuration
- Modifying Alembic migration files
- Merging multiple services into one
- Introducing any cross-service database coupling

All refactors must: provide a plan first, make minimal diffs, and preserve service boundaries.
