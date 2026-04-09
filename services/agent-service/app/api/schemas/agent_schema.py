import uuid
from typing import Any

from pydantic import BaseModel, Field


class JDScoreRequest(BaseModel):
    """Input for JD vs CV scoring workflow (placeholder fields for future pipeline)."""

    job_id: uuid.UUID
    cv_id: uuid.UUID


class JDScoreResponse(BaseModel):
    """Stub response until scoring pipeline is implemented."""

    status: str = Field(description="Pipeline status, e.g. stub")
    job_id: uuid.UUID
    cv_id: uuid.UUID
    scores: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
