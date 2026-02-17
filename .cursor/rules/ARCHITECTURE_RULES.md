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

Services are located under the `services/` directory.

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

### 2.2 API Gateway Responsibilities

The API Gateway is responsible for:

- JWT validation via Auth0
- Request validation
- Routing to internal services
- Basic middleware (logging, rate limiting)

The API Gateway must **NOT** contain business logic.

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

- CV upload is handled by the CV service.
- Extracted data and embeddings are stored.
- File storage (S3 or equivalent) is external to the core database.

### 3.6 Interview and Scoring

- The Interview service manages interview sessions.
- The Scoring service evaluates candidate performance.
- Scoring results must be explainable and auditable.

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

## 7. Non-Negotiable Safety Rules

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
