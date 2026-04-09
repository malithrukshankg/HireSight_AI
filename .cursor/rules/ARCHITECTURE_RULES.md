# HireSight AI – Architecture Rules

## 1. System Overview

HireSight AI is a microservices-based recruitment platform built with:

- **FastAPI** (backend services)
- **React** (frontend)
- **Auth0** (authentication)
- **PostgreSQL** (primary database)
- **Redis** (caching / conversational state)
- **Docker** (containerized deployment)

The system follows a **microservices architecture**.

Services are located under the `services/` directory (including **api-gateway**, **cv-service**, **agent-service**, and any future services).

Each service must remain **logically independent**.

The API Gateway is the only public entry point.

---

## 2. Microservices Principles

### 2.1 Service Isolation

- Each service owns its business logic.
- Each service owns its database schema.
- No direct cross-service database joins are allowed.
- Cross-service communication must be via:
  - HTTP API
  - Events (future)
  - Message broker (future)

**Database layout (shared PostgreSQL):**

- One database, one database user (no per-service roles).
- Schema-per-service: `public` (api-gateway), `cv_schema` (cv-service), etc.
- No cross-schema foreign keys. Store external entity IDs (e.g. `candidate_id`) as plain UUID columns — logical references only. Referential validation at application level via API calls.

### 2.2 API Gateway Responsibilities

The API Gateway is responsible for:

- JWT validation via Auth0
- Access control aligned with user roles
- Request validation
- Public routing and delegation to internal services (HTTP)
- Basic middleware (logging, rate limiting)
- **Job and candidate domain** ownership as implemented today (persistence in gateway-owned schema, business rules for jobs/candidates)

The API Gateway must **NOT** contain:

- CV file storage, S3, or CV normalization logic (owned by **cv-service**)
- AI workflow orchestration or JD scoring pipelines (owned by **agent-service**)

It forwards and delegates to those services via HTTP clients (e.g. `CV_SERVICE_URL`, `AGENT_SERVICE_URL`).

---

## 3. Core Business Domains

### 3.1 Organization Management

- An organization represents a hiring entity.
- An organization can have multiple users.
- An organization owns jobs and recruiter memberships.

### 3.2 User Management

Users are authenticated via Auth0.

User roles include:

- admin
- recruiter
- candidate

Rules:

- Passwords are **NOT** stored for Auth0 users.
- `auth0_sub` is the primary identity reference.
- Users may belong to an organization.
- Recruiters may belong to multiple organizations via an association table.

### 3.3 Recruiter–Organization Relationship

- Many-to-many relationship.
- Implemented via the `RecruiterOrganization` association object.
- May contain metadata such as status, role, and permissions.

### 3.4 Job Lifecycle

- Jobs belong to an organization.
- Only authorized organization members can create or manage jobs.

### 3.5 CV Processing

- CV upload and storage are handled by the **cv-service** (`services/cv-service/`).
- api-gateway proxies CV requests to cv-service via HTTP (CvClient).
- cv-service owns `cv_schema.cvs`; S3 storage is configured in cv-service.
- Internal cv-service endpoints (`/internal/*`) are not exposed publicly (port not published).

### 3.6 Agent Service (JD Scoring and AI Orchestration)

The **agent-service** (`services/agent-service/`) owns **AI-driven orchestration** for recruitment workflows, including **JD scoring** (CV vs job description comparison), future **explainable scoring pipelines**, and coordination of multi-step flows.

- **LangChain** is intended for use **inside** agent components (e.g. prompts, chains, tools) where appropriate.
- **LangGraph** is intended for **multi-step workflow orchestration** within agent-service (not as a replacement for microservice boundaries).
- agent-service calls **cv-service** over HTTP for **structured/normalized CV data**; it does **not** duplicate CV extraction, storage, or normalization.
- agent-service may call **api-gateway** (or future dedicated services) over HTTP for **job or domain context** once stable internal contracts exist. Do not duplicate job/candidate persistence owned by the gateway.
- Internal agent endpoints (e.g. under `/internal/...`) must not be exposed publicly; container port is internal to the Docker network unless debugging.

**Domain ownership (do not duplicate across services):**

| Concern | Owner |
|--------|--------|
| Auth0 JWT validation, public API surface, job/candidate entities as implemented | **api-gateway** |
| CV upload, storage, text extraction, structured CV | **cv-service** |
| JD scoring workflow, CV vs JD comparison logic, AI orchestration, explainable scoring pipeline | **agent-service** |

### 3.7 Interview (Future)

- A dedicated interview service may manage interview sessions when introduced.
- Scoring that is **AI-orchestrated and JD-related** belongs under **agent-service** (see §3.6); any separate interview product logic should remain in its owning service.
- Scoring and hiring decisions must remain explainable and auditable where applicable.

---

## 4. Database Rules

- All schema changes must align with the ER diagram.
- Migrations must be created intentionally.
- Migration files must never be auto-deleted or rewritten.
- No schema shortcuts are allowed for convenience.
- Referential integrity must always be preserved.

---

## 5. Authentication Rules

- Auth0 validates users externally.
- The backend validates JWT tokens.
- No email/password login inside the backend.
- User records are created or updated via authenticated requests.

---

## 6. Audit & Security

- Security-sensitive actions must be auditable.
- Actions like job creation, CV upload, and interview scoring must be traceable.
- Internal service APIs must never be exposed publicly.

---

## 7. Internal Service Communication

- Internal services (**cv-service**, **agent-service**, etc.) are reachable on the Docker network; typically only **api-gateway** (and other internal services as needed) should call them.
- Do not publish internal service ports to the host unless required for debugging.
- Gateway calls internal services via `{SERVICE}_URL` (e.g. `CV_SERVICE_URL`, `AGENT_SERVICE_URL`).
- Service-to-service calls use HTTP; **agent-service** uses configured base URLs (e.g. `CV_SERVICE_URL`, `GATEWAY_SERVICE_URL`) consistent with gateway client patterns.
- Optional: shared API key header (`X-Internal-Api-Key`) for defense in depth on internal routes.

---

## 8. Migrations and Alembic

- Each service has its own Alembic under `services/{service}/alembic/`.
- When multiple services share one database, each service must use a distinct `version_table` in `alembic/env.py` to avoid conflicts (e.g. `cv_alembic_version` for cv-service).
- Migration files must never be auto-deleted or rewritten.
- SQLAlchemy models: when `__table_args__` is a tuple with schema and constraints, the options dict (e.g. `{"schema": "cv_schema"}`) must be the **last** element.

---

## 9. Non-Negotiable Safety Rules

The following actions require explicit approval:

- Deleting files or folders
- Modifying `infra/`
- Modifying Docker configurations
- Modifying Alembic migrations
- Collapsing multiple services into one
- Introducing cross-service DB coupling

All refactors must:

- Provide a plan first
- Make minimal diffs
- Preserve service boundaries
