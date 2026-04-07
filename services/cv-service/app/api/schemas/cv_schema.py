from datetime import datetime
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
    extraction_status: str
    extracted_text: str | None = None
    page_count: int | None = None
    extraction_error: str | None = None


class CVByCandidateResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    s3_key: str
    bucket: str
    original_filename: str
    content_type: str
    file_size_bytes: int | None = None
    created_at: datetime
