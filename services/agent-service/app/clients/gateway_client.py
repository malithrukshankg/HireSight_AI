from __future__ import annotations

import uuid
from typing import Any

import httpx

from app.config import settings

_JOB_AI_CONTEXT_PATH = "/internal/jobs/{job_id}/ai-context"
_JD_PARSE_PATH = "/internal/ai/jobs/parse-description"
_CANDIDATE_MATCH_RESULT_PATH = "/internal/candidates/{candidate_id}/match-result"


class GatewayClient:
    """HTTP client for api-gateway internal endpoints."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.GATEWAY_SERVICE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.HTTP_TIMEOUT_SECONDS

    async def get_job_ai_context(self, job_id: uuid.UUID) -> dict:
        """Fetch job title, raw description, parsed JD output, and parse metadata.

        Returns the JobAiContextResponse payload as a dict:
            job_id, title, description, parsed_job_description, parse_metadata
        Raises httpx.HTTPStatusError on 4xx/5xx.
        """
        path = _JOB_AI_CONTEXT_PATH.format(job_id=job_id)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}")
            response.raise_for_status()
            return response.json()

    async def save_match_result(
        self,
        candidate_id: uuid.UUID,
        match_score: float,
        scores_json: dict[str, Any],
    ) -> None:
        """Persist match score and breakdown to the candidate record in api-gateway.

        Raises httpx.HTTPStatusError on 4xx/5xx.
        """
        path = _CANDIDATE_MATCH_RESULT_PATH.format(candidate_id=candidate_id)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                f"{self.base_url}{path}",
                json={"match_score": match_score, "scores_json": scores_json},
            )
            response.raise_for_status()

    async def parse_jd_text(self, description: str, title: str | None = None) -> dict:
        """Call the internal Gemini JD parsing endpoint with raw text.

        Returns the JobDescriptionParseResponse payload as a dict.
        Raises httpx.HTTPStatusError on 4xx/5xx.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{_JD_PARSE_PATH}",
                json={"description": description, "title": title},
            )
            response.raise_for_status()
            return response.json()
