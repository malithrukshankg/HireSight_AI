from __future__ import annotations

from typing import TYPE_CHECKING
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

if TYPE_CHECKING:
    from .jobs import Job
    from .recruiter_organization import RecruiterOrganization
    from .candidate import Candidate

class PlanEnum(str, enum.Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"

class Organization(Base):

    __tablename__ = "organizations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    plan: Mapped[PlanEnum] = mapped_column(
        Enum(PlanEnum, name="plan_enum"),
        nullable=False,
        default=PlanEnum.free
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships (1 Organization -> many RecruiterOrganization; FK: recruiter_organization.organization_id)
    recruiter_organizations: Mapped[list["RecruiterOrganization"]] = relationship(
        "RecruiterOrganization",
        back_populates="organization",
        foreign_keys="RecruiterOrganization.organization_id",
        cascade="all, delete-orphan",
    )

    # Relationships (1 Organization -> many Jobs)
    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="organization",
        foreign_keys="Job.organization_id",
        cascade="all, delete-orphan",
    )

    # Relationships (1 Organization -> many Candidates; FK: candidates.organization_id)
    candidates: Mapped[list["Candidate"]] = relationship(
        "Candidate",
        back_populates="organization",
        foreign_keys="Candidate.organization_id",
        cascade="all, delete-orphan",
    )