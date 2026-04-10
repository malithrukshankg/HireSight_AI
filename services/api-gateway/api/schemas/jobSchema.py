from datetime import datetime
from typing import Any, Optional

import uuid

from pydantic import BaseModel

from models.jobs import JobStatusEnum


class JobCreate(BaseModel):
    """Request body for POST /jobs."""

    organization_id: uuid.UUID
    title: str
    description: str
    location: str
    employment_type: str
    status: JobStatusEnum = JobStatusEnum.draft
    requirements_json: Optional[dict[str, Any]] = None


class JobUpdate(BaseModel):
    """Request body for PATCH /jobs/{id}. All fields optional."""

    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    status: Optional[JobStatusEnum] = None
    requirements_json: Optional[dict[str, Any]] = None


class JobRead(BaseModel):
    """Response model for job endpoints."""

    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_user_id: uuid.UUID
    title: str
    description: str
    location: str
    employment_type: str
    status: JobStatusEnum
    requirements_json: Optional[dict[str, Any]] = None
    parsed_job_description_json: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobApplyResponse(BaseModel):
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    cv_id: uuid.UUID
    message: str


class JobApplicationRead(BaseModel):
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    organization_id: uuid.UUID
    full_name: str
    email: str
    phone: str | None = None
    status: str
    applied_at: datetime
    cv_id: uuid.UUID | None = None
