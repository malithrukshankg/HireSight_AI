from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=str(settings.SQLALCHEMY_ECHO).lower() in ("1", "true", "yes", "on"),
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    expire_on_commit=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    """Declarative base for SQLAlchemy models."""


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


DBSession = Annotated[AsyncSession, Depends(get_db)]
