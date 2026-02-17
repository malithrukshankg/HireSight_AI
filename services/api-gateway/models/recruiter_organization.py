from __future__ import annotations

from typing import TYPE_CHECKING
from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

if TYPE_CHECKING:
    from .user import User
    from .organizations import Organization


class RecruiterOrganization(Base):
    __tablename__ = "recruiter_organization"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships (many RecruiterOrganization -> 1 User; many RecruiterOrganization -> 1 Organization)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="recruiter_organizations",
        foreign_keys=[user_id],
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="recruiter_organizations",
        foreign_keys=[organization_id],
    )
