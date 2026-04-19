# agent-service -- Service Rules

Inherits all shared rules from `services/CLAUDE.md` and root `CLAUDE.md`.

## Ownership

The agent-service owns:
- JD scoring workflows (CV vs job description comparison logic)
- AI orchestration for candidate-to-job matching
- Explainable scoring pipelines
- Multi-step recruitment workflow coordination

## What agent-service Must NOT Contain

- CV ingestion, PDF parsing, or S3 operations (owned by cv-service)
- Auth0 JWT validation or access control (owned by api-gateway)
- Job or candidate entity persistence (owned by api-gateway)
- Public-facing routes -- agent-service endpoints are internal only

## Key Patterns

- Use LangChain inside components (prompts, chains, tools) where appropriate.
- Use LangGraph for multi-step workflow orchestration within this service.
- Call cv-service via HTTP (`CV_SERVICE_URL`) to get structured/normalized CV data; do not duplicate CV extraction.
- Call api-gateway via HTTP (`GATEWAY_SERVICE_URL`) for job/domain context where needed.
- All internal endpoints must not be exposed publicly (container port is internal to Docker network).
- Scoring and hiring decisions must remain explainable and auditable.
