from database import Base
from sqlalchemy import String, Boolean, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

class RecruiterOrganization(Base):
    __tablename__ = "recruiter_organization"

    userid: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True),ForeignKey("users.id"), primary_key=True)
    organizationif: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),ForeignKey("organizations.id"), primary_key=True
    )
