from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel

from models.organizations import PlanEnum


class OrganizationCreate(BaseModel):
    """Request body for POST /organizations."""

    name: str
    plan: PlanEnum = PlanEnum.free


class OrganizationUpdate(BaseModel):
    """Request body for PATCH /organizations/{id}. All fields optional."""

    name: Optional[str] = None
    plan: Optional[PlanEnum] = None


class OrganizationRead(BaseModel):
    """Response model for organization endpoints."""

    id: uuid.UUID
    name: str
    plan: PlanEnum
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
