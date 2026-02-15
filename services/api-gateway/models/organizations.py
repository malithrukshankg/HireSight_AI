from database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

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