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
