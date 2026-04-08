from __future__ import annotations

import uuid
from typing import Any

import httpx
from fastapi import UploadFile

from config import settings


class CvClient:
    """HTTP client for cv-service."""

    def __init__(self, base_url: str | None = None, timeout: float = 30):
        self.base_url = (base_url or settings.CV_SERVICE_URL).rstrip("/")
        self.timeout = timeout

    async def upload_cv(self, file: UploadFile) -> dict:
        """POST file to cv-service /cv/upload (standalone, uses placeholder IDs)."""
        content = await file.read()
        files = {
            "file": (
                file.filename or "upload",
                content,
                file.content_type or "application/octet-stream",
            )
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/cv/upload",
                files=files,
            )
            response.raise_for_status()
            return response.json()

    async def upload_for_candidate(
        self,
        file: UploadFile,
        candidate_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> dict:
        """POST file to cv-service /internal/upload-for-candidate."""
        content = await file.read()
        files = {
            "file": (
                file.filename or "upload",
                content,
                file.content_type or "application/octet-stream",
            )
        }
        headers = {
            "X-Candidate-Id": str(candidate_id),
            "X-User-Id": str(user_id),
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/internal/upload-for-candidate",
                files=files,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_by_candidate_id(self, candidate_id: uuid.UUID) -> dict | None:
        """GET CV metadata for candidate. Returns None on 404."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/internal/by-candidate/{candidate_id}",
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    async def trigger_extraction(self, cv_id: uuid.UUID) -> dict:
        """POST to cv-service manual extraction endpoint for an existing CV."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/internal/extract/{cv_id}",
            )
            response.raise_for_status()
            return response.json()

    async def trigger_structured_extraction(self, cv_id: uuid.UUID) -> dict:
        """POST to cv-service manual structured extraction endpoint for an existing CV."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/internal/extract-structured/{cv_id}",
            )
            response.raise_for_status()
            return response.json()

    async def get_cv_detail(self, cv_id: uuid.UUID) -> dict[str, Any]:
        """GET CV detail (including parsed profile) by CV ID."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/internal/cv/{cv_id}",
            )
            response.raise_for_status()
            return response.json()

    async def get_cv_file(self, cv_id: uuid.UUID) -> tuple[bytes, str, str]:
        """GET CV file bytes by CV ID."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/internal/cv/{cv_id}/file",
            )
            response.raise_for_status()
            content_disposition = response.headers.get("content-disposition", "")
            media_type = response.headers.get("content-type", "application/octet-stream")
            return response.content, media_type, content_disposition
