# cv-service -- Service Rules

Inherits all shared rules from `services/CLAUDE.md` and root `CLAUDE.md`.

## Ownership

The cv-service owns:
- PDF ingestion via PyMuPDF
- CV file upload and storage in S3 (boto3)
- Structured CV extraction using OpenAI + Instructor
- `cv_schema` database schema

## What cv-service Must NOT Contain

- Job matching logic or JD scoring (owned by agent-service)
- Auth0 JWT validation or access control (owned by api-gateway)
- Public-facing routes -- all cv-service endpoints are internal only

## Key Patterns

- All CV extraction uses Instructor structured output patterns; preserve these schemas.
- Internal endpoints live under `/internal/*` and must not be reachable publicly (port not published to host).
- S3 configuration is owned entirely by this service; do not reference S3 from other services.
- Alembic `version_table` must be set to `cv_alembic_version` in `alembic/env.py`.
