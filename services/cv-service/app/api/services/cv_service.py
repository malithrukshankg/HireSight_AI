from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import logging
import re
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile

from app.api.repositories.cv_repository import CVRepository
from app.config import settings

logger = logging.getLogger(__name__)


class CVValidationError(ValueError):
    pass


class CVS3UploadError(RuntimeError):
    pass


class CVExtractionError(RuntimeError):
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

    def _read_upload_bytes(self, upload: UploadFile) -> bytes:
        """Read upload bytes without breaking downstream stream consumers."""
        stream = upload.file
        try:
            current = stream.tell()
        except Exception as e:
            raise CVValidationError("Unable to read uploaded file stream") from e

        try:
            # We always rewind to start because extraction should process full PDF content.
            stream.seek(0)
            content = stream.read()
        except Exception as e:
            raise CVValidationError("Failed to read uploaded file content") from e
        finally:
            # Restore stream position so the same UploadFile can be reused safely later.
            try:
                stream.seek(current)
            except Exception:
                pass

        if not isinstance(content, (bytes, bytearray)):
            raise CVValidationError("Uploaded file content is not a valid byte stream")

        if len(content) == 0:
            raise CVValidationError("Uploaded file is empty")

        return bytes(content)

    def _extract_pdf_text(self, file_bytes: bytes, *, source_name: str) -> tuple[str, int]:
        """Extract plain text from a PDF byte stream using PyMuPDF."""
        if not file_bytes:
            raise CVValidationError("Uploaded file is empty")

        logger.info("CV extraction started: source=%s bytes=%s", source_name, len(file_bytes))

        try:
            import fitz
        except Exception as e:
            logger.exception("PyMuPDF import failed: source=%s", source_name)
            raise CVExtractionError("PyMuPDF is not available for extraction") from e

        document = None
        try:
            document = fitz.open(stream=file_bytes, filetype="pdf")
            page_count = document.page_count
            page_text_parts: list[str] = []

            for page_index in range(page_count):
                # Keep extraction raw/plain for phase 1; parsing/structuring comes later.
                page = document.load_page(page_index)
                page_text_parts.append(page.get_text("text") or "")

            extracted_text = "\n".join(page_text_parts).strip()
            logger.info(
                "CV extraction succeeded: source=%s pages=%s text_chars=%s",
                source_name,
                page_count,
                len(extracted_text),
            )
            return extracted_text, page_count
        except CVValidationError:
            raise
        except Exception as e:
            logger.exception("CV extraction failed: source=%s", source_name)
            raise CVExtractionError("Failed to extract text from PDF") from e
        finally:
            if document is not None:
                try:
                    document.close()
                except Exception:
                    pass

    def extract_pdf_text_from_upload(self, file: UploadFile) -> tuple[str, int]:
        """
        Public service helper for PDF text extraction from an UploadFile.

        This is intentionally separated so upload orchestration can call extraction
        when needed (automatic and manual flows) without duplicating stream logic.
        """
        file_bytes = self._read_upload_bytes(file)
        source_name = self._sanitize_filename(file.filename or "upload.pdf")
        return self._extract_pdf_text(file_bytes, source_name=source_name)

    def _validate_and_upload_to_s3(
        self, file: UploadFile
    ) -> tuple[str, str, str, str, int | None, str]:
        """Validate file and upload to S3. Returns (original_filename, content_type, s3_key, file_type, size_bytes)."""
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

        return original_filename, content_type, s3_key, file_type, file_size_bytes

    async def upload_cv(self, file: UploadFile, principal: dict) -> dict:
        _ = principal  # keep dependency contract for future user-aware keys

        original_filename, content_type, s3_key, file_type, file_size_bytes = (
            self._validate_and_upload_to_s3(file)
        )

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

    async def upload_cv_for_candidate(
        self,
        *,
        file: UploadFile,
        candidate_id: uuid.UUID,
        uploaded_by_user_id: uuid.UUID,
    ) -> dict:
        """Upload CV for a specific candidate (job apply flow)."""
        original_filename, content_type, s3_key, file_type, file_size_bytes = (
            self._validate_and_upload_to_s3(file)
        )

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
