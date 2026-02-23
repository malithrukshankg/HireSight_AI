from __future__ import annotations

from typing import TYPE_CHECKING, Any
from database import Base
from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

if TYPE_CHECKING:
    from .organizations import Organization
    from .user import User


class JobStatusEnum(str, enum.Enum):
    draft = "draft"
    open = "open"
    closed = "closed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    employment_type: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[JobStatusEnum] = mapped_column(
        Enum(JobStatusEnum, name="job_status_enum"),
        nullable=False,
        default=JobStatusEnum.draft,
    )

    requirements_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="jobs",
        foreign_keys=[organization_id],
    )

    created_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="jobs",
        foreign_keys=[created_by_user_id],
    )
