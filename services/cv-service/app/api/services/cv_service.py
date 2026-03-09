from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile

from app.api.repositories.cv_repository import CVRepository
from app.config import settings


class CVValidationError(ValueError):
    pass


class CVS3UploadError(RuntimeError):
    pass


class CvService:
    _ALLOWED_CONTENT_TYPES = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    }

    def __init__(self, repo: CVRepository):
        self.repo = repo
        self.s3_client = boto3.client("s3", region_name=settings.AWS_REGION)

    def _sanitize_filename(self, filename: str) -> str:
        name = Path(filename).name.strip()
        if not name:
            raise CVValidationError("Filename is required")
        return re.sub(r"[^A-Za-z0-9._-]", "_", name)

    def _resolve_file_size(self, upload: UploadFile) -> int | None:
        stream = upload.file
        try:
            current = stream.tell()
            stream.seek(0, 2)
            size = stream.tell()
            stream.seek(current)
            return int(size)
        except Exception:
            return None

    async def upload_cv(self, file: UploadFile, principal: dict) -> dict:
        _ = principal  # keep dependency contract for future user-aware keys

        if file is None:
            raise CVValidationError("No file provided")

        content_type = (file.content_type or "").strip().lower()
        file_type = self._ALLOWED_CONTENT_TYPES.get(content_type)
        if file_type is None:
            allowed = ", ".join(sorted(self._ALLOWED_CONTENT_TYPES.keys()))
            raise CVValidationError(f"Unsupported content type. Allowed: {allowed}")

        original_filename = self._sanitize_filename(file.filename or "")
        file_size_bytes = self._resolve_file_size(file)

        max_size_bytes = settings.CV_MAX_SIZE_MB * 1024 * 1024
        if file_size_bytes is not None and file_size_bytes > max_size_bytes:
            raise CVValidationError(
                f"File too large. Max allowed size is {settings.CV_MAX_SIZE_MB}MB"
            )

        s3_key = f"cvs/{uuid.uuid4()}-{original_filename}"
        try:
            file.file.seek(0)
            self.s3_client.upload_fileobj(
                file.file,
                settings.S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": content_type},
            )
        except (BotoCoreError, ClientError, Exception) as e:
            raise CVS3UploadError("Failed to upload file to S3") from e

        try:
            candidate_id = uuid.UUID(settings.CV_PLACEHOLDER_CANDIDATE_ID)
            uploaded_by_user_id = uuid.UUID(settings.CV_PLACEHOLDER_UPLOADED_BY_USER_ID)
        except ValueError as e:
            raise CVValidationError("Invalid placeholder UUID configuration") from e

        cv = await self.repo.upsert_uploaded_cv(
            candidate_id=candidate_id,
            uploaded_by_user_id=uploaded_by_user_id,
            s3_bucket=settings.S3_BUCKET,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=file_size_bytes,
            file_type=file_type,
            s3_key=s3_key,
        )

        return {
            "id": cv.id,
            "s3_key": s3_key,
            "bucket": settings.S3_BUCKET,
            "original_filename": original_filename,
            "content_type": content_type,
            "file_size_bytes": file_size_bytes,
            "created_at": cv.created_at or datetime.now(timezone.utc),
        }
