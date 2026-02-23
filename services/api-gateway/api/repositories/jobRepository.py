from typing import Any, Optional

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Job
from models.jobs import JobStatusEnum


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        organization_id: uuid.UUID,
        created_by_user_id: uuid.UUID,
        title: str,
        description: str,
        location: str,
        employment_type: str,
        status: JobStatusEnum = JobStatusEnum.draft,
        requirements_json: Optional[dict[str, Any]] = None,
    ) -> Job:
        """Create a new job."""
        job = Job(
            organization_id=organization_id,
            created_by_user_id=created_by_user_id,
            title=title,
            description=description,
            location=location,
            employment_type=employment_type,
            status=status,
            requirements_json=requirements_json,
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def find_by_id(self, id: uuid.UUID) -> Job | None:
        """Find a job by ID."""
        result = await self.db.execute(select(Job).where(Job.id == id))
        return result.scalar_one_or_none()

    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        organization_id: Optional[uuid.UUID] = None,
        status: Optional[JobStatusEnum] = None,
    ) -> list[Job]:
        """List jobs with optional filters and pagination."""
        stmt = select(Job)
        if organization_id is not None:
            stmt = stmt.where(Job.organization_id == organization_id)
        if status is not None:
            stmt = stmt.where(Job.status == status)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_by_organization_id(self, organization_id: uuid.UUID) -> list[Job]:
        """Find all jobs for an organization."""
        result = await self.db.execute(
            select(Job).where(Job.organization_id == organization_id)
        )
        return list(result.scalars().all())

    async def find_by_created_by_user_id(self, user_id: uuid.UUID) -> list[Job]:
        """Find all jobs created by a user (recruiter)."""
        result = await self.db.execute(
            select(Job).where(Job.created_by_user_id == user_id)
        )
        return list(result.scalars().all())

    async def update(self, job: Job, **kwargs: Any) -> Job:
        """Update job fields. Only non-None kwargs are applied."""
        for key, value in kwargs.items():
            if value is not None and hasattr(job, key):
                setattr(job, key, value)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def delete(self, job: Job) -> None:
        """Delete a job."""
        await self.db.delete(job)
        await self.db.commit()
