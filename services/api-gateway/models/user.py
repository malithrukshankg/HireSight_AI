from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

if TYPE_CHECKING:
    from .jobs import Job
    from .recruiter_organization import RecruiterOrganization
    from .candidate import Candidate
    from .cv import CV


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    email: Mapped[str] = mapped_column(
        String(225), unique=True, index=True, nullable=False
    )

    auth0_sub: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin','recruiter','candidate')", name="ck_users_role"
        ),
    )

    # Relationships (1 User -> many RecruiterOrganization; FK: recruiter_organization.user_id)
    recruiter_organizations: Mapped[list["RecruiterOrganization"]] = relationship(
        "RecruiterOrganization",
        back_populates="user",
        foreign_keys="RecruiterOrganization.user_id",
        cascade="all, delete-orphan",
    )

    # Relationships (1 User -> many Jobs as creator)
    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="created_by_user",
        foreign_keys="Job.created_by_user_id",
    )

    # Relationships (1 User -> many Candidates; FK: candidates.user_id, optional)
    candidates: Mapped[list["Candidate"]] = relationship(
        "Candidate",
        back_populates="user",
        foreign_keys="Candidate.user_id",
    )

    # Relationships (1 User -> many CVs uploaded; FK: cvs.uploaded_by_user_id)
    uploaded_cvs: Mapped[list["CV"]] = relationship(
        "CV",
        back_populates="uploaded_by_user",
        foreign_keys="CV.uploaded_by_user_id",
    )
