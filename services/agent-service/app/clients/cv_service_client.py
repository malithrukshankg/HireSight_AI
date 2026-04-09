from __future__ import annotations

import uuid
from typing import Any

import httpx

from app.config import settings


class CvServiceClient:
    """HTTP client for cv-service internal APIs (structured CV owned by cv-service)."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.CV_SERVICE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.HTTP_TIMEOUT_SECONDS

    async def get_cv_detail(self, cv_id: uuid.UUID) -> dict[str, Any]:
        """GET CV detail (including structured profile) by CV ID."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/internal/cv/{cv_id}")
            response.raise_for_status()
            return response.json()
