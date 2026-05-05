import uuid
from typing import Any

from pydantic import BaseModel, Field


class JDScoreRequest(BaseModel):
    """Input for JD vs CV scoring workflow (placeholder fields for future pipeline)."""

    job_id: uuid.UUID
    cv_id: uuid.UUID


class JDScoreResponse(BaseModel):
    status: str = Field(description="'completed' or 'failed'")
    job_id: uuid.UUID
    cv_id: uuid.UUID
    request_id: str
    scores: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
