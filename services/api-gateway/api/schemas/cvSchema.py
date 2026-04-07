from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel


class CVUploadResponse(BaseModel):
    id: uuid.UUID
    s3_key: str
    bucket: str
    original_filename: str
    content_type: str
    file_size_bytes: int | None = None
    created_at: datetime
    extraction_status: str | None = None
    extracted_text: str | None = None
    page_count: int | None = None
    extraction_error: str | None = None
    structured_extraction_status: str | None = None
    parsed_profile_json: dict[str, Any] | None = None
    structured_extraction_error: str | None = None


class CVExtractionResponse(BaseModel):
    id: uuid.UUID
    extraction_status: str
    extracted_text: str | None = None
    page_count: int | None = None
    extraction_error: str | None = None


class CVStructuredExtractionResponse(BaseModel):
    id: uuid.UUID
    structured_extraction_status: str
    parsed_profile_json: dict[str, Any] | None = None
    structured_extraction_error: str | None = None
