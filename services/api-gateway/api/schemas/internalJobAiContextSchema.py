from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel


class JdParseMetadata(BaseModel):
    parse_version: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None
    content_hash: str | None = None
    parsed_at: datetime | None = None


class JobAiContextResponse(BaseModel):
    job_id: uuid.UUID
    title: str
    description: str
    parsed_job_description: dict[str, Any] | None = None
    parse_metadata: JdParseMetadata
