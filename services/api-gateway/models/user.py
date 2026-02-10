from sqlalchemy import String, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    organization_id: Mapped[str]

    email: Mapped[str] = mapped_column(
        String(225), unique=True, index=True, nullable=False
    )

    password_hash: Mapped[str] = mapped_column(String(225), nullable=False)

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin','recruiter','candidate')", name="ck_users_role"
        ),
    )
