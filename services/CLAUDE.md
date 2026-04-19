# HireSight AI -- Backend Services (Shared Rules)

These rules apply to all three backend services: `api-gateway`, `cv-service`, and `agent-service`.

Each service also has its own `CLAUDE.md` with service-specific ownership rules.

Always follow the root `CLAUDE.md` for system-wide architecture and safety gates.

## File Safety

- Never delete files or folders without explicit approval.
- Never modify unless explicitly instructed:
  - `infra/` or any Docker files (Dockerfile, docker-compose*.yml)
  - `alembic/` directories or migration files
  - `.devcontainer/`
  - `requirements.txt`
  - `pyproject.toml`
- Never rewrite or auto-delete migration files.
- Never auto-generate migrations unless explicitly requested.

## Database Integrity

- All schema changes must align with the ER diagram.
- Preserve referential integrity; no schema shortcuts.
- Auth0 is the primary identity -- do NOT introduce password-based login.
- `auth0_sub` is the primary identity reference; never replace it.
- Each service must have a unique `version_table` in `alembic/env.py` to avoid revision conflicts.
- SQLAlchemy `__table_args__` tuple: constraints first, options dict (e.g. `{"schema": "..."}`) last.

## Scope and Diff Size

- Only modify files explicitly mentioned in the user's prompt or strictly required for the change.
- Do not refactor or "improve" unrelated code.
- Make minimal diffs. Avoid style-only changes unless requested.

## Refactors

- Explain the plan before refactoring: describe what will change and why.
- If a change impacts architecture boundaries, ask for confirmation first.
- If unsure, ask instead of modifying.

## Safety Priority

When in doubt:
1. Preserve architecture
2. Preserve data integrity
3. Preserve service boundaries
4. Preserve minimal diffs
