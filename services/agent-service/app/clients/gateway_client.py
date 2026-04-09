from __future__ import annotations

import uuid

import httpx

from app.config import settings

# Gateway does not yet expose a stable internal job API for service-to-service calls.
# When it does, point this path at that contract (and add auth if required).
_INTERNAL_JOB_CONTEXT_PATH = "/internal/jobs/{job_id}"


class GatewayClient:
    """HTTP client for future internal gateway APIs (e.g. job context for JD scoring)."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.GATEWAY_SERVICE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.HTTP_TIMEOUT_SECONDS

    async def get_job_context(self, job_id: uuid.UUID) -> dict:
        """
        Fetch job context for scoring. Not implemented on api-gateway yet — call only
        after an internal route exists; until then orchestration should not depend on this.
        """
        path = _INTERNAL_JOB_CONTEXT_PATH.format(job_id=job_id)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}")
            response.raise_for_status()
            return response.json()
