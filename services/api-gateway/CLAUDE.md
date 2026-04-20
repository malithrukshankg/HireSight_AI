# api-gateway -- Service Rules

Inherits all shared rules from `services/CLAUDE.md` and root `CLAUDE.md`.

## Ownership

The api-gateway owns:
- Auth0 JWT validation via `get_current_principal()` FastAPI dependency
- Access control aligned with user roles (admin, recruiter, candidate)
- Public REST API surface and request routing
- Job and candidate domain: CRUD, user/org management, job lifecycle
- Gemini JD parsing (gateway-owned AI feature)
- HTTP proxying to internal services via `CV_SERVICE_URL` and `AGENT_SERVICE_URL`

## What the Gateway Must NOT Contain

- CV file storage, S3 operations, or CV normalization logic (owned by cv-service)
- AI workflow orchestration or JD scoring pipelines (owned by agent-service)
- Do not duplicate domain logic owned by other services

## AI Service Implementation Pattern

When adding AI for a gateway-owned domain, follow this structure exactly:

```
services/api-gateway/services/ai_service/
  <feature_name>/
    agents/
    prompts/
    orchestrator/
    utils/
    schemas/
  shared/
```

Rules:
- AI business logic must live under `services/ai_service/`; never in routers/controllers.
- Routers stay thin: authn/authz/validation/delegation/error mapping only.
- Do not create flat AI files directly under `services/`.
- Keep `orchestrator` and `agent` separated so LangGraph can wrap orchestrators later with minimal refactor.
- `shared/` holds reusable AI infrastructure (Gemini clients, AI exceptions, structured output helpers).

## Routing Rules

- Only the gateway exposes public ports.
- Internal services (cv-service, agent-service) are called via their configured base URLs.
- Do not expose cv-service or agent-service internal endpoints publicly.
