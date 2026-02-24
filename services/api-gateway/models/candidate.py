from __future__ import annotations

from typing import TYPE_CHECKING
from database import Base
from sqlalchemy import DateTime, ForeignKey, Text, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .organizations import Organization
    from .user import User


class Candidate(Base):
    __tablename__ = "candidates"

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

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    email: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="new",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('new', 'screening', 'interviewing', 'offered', 'rejected', 'hired')",
            name="ck_candidates_status",
        ),
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
        back_populates="candidates",
        foreign_keys=[organization_id],
    )

    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="candidates",
        foreign_keys=[user_id],
    )
