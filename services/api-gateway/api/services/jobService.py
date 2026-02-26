import uuid
from typing import Optional

from api.repositories.jobRepository import JobRepository
from api.repositories.organizationRepository import OrganizationRepository
from api.schemas.jobSchema import JobCreate, JobUpdate
from models import Job
from models.jobs import JobStatusEnum


class JobService:
    def __init__(
        self,
        job_repo: JobRepository,
        org_repo: OrganizationRepository,
    ):
        self.job_repo = job_repo
        self.org_repo = org_repo

    async def create(self, payload: JobCreate, user_id: uuid.UUID) -> Job:
        """Create a job. User must be a member of the organization."""
        org = await self.org_repo.find_by_id(payload.organization_id)
        if org is None:
            raise ValueError("Organization not found")

        is_member = await self.org_repo.user_is_org_member(user_id, payload.organization_id)
        if not is_member:
            raise ValueError("User is not a member of this organization")

        title = (payload.title or "").strip()
        if not title:
            raise ValueError("Job title is required and cannot be empty")
        if not (payload.description or "").strip():
            raise ValueError("Job description is required and cannot be empty")
        if not (payload.location or "").strip():
            raise ValueError("Job location is required and cannot be empty")
        if not (payload.employment_type or "").strip():
            raise ValueError("Job employment type is required and cannot be empty")

        return await self.job_repo.create(
            organization_id=payload.organization_id,
            created_by_user_id=user_id,
            title=title,
            description=payload.description.strip(),
            location=payload.location.strip(),
            employment_type=payload.employment_type.strip(),
            status=payload.status,
            requirements_json=payload.requirements_json,
        )

    async def get_by_id(self, id: uuid.UUID) -> Job:
        """Get a job by ID. Raises ValueError if not found."""
        job = await self.job_repo.find_by_id(id)
        if job is None:
            raise ValueError("Job not found")
        return job

    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
        organization_id: Optional[uuid.UUID] = None,
        status: Optional[JobStatusEnum] = None,
        query: Optional[str] = None,
        location: Optional[str] = None,
        sort: str = "recent",
    ) -> list[Job]:
        """List jobs with optional filters and pagination."""
        if limit < 1 or limit > 500:
            raise ValueError("Limit must be between 1 and 500")
        if offset < 0:
            raise ValueError("Offset must be non-negative")
        if sort not in ("recent",):
            raise ValueError("Sort must be one of: recent")
        return await self.job_repo.find_all(
            limit=limit,
            offset=offset,
            organization_id=organization_id,
            status=status,
            query=query,
            location=location,
            sort=sort,
        )

    async def list_by_creator(self, user_id: uuid.UUID) -> list[Job]:
        """List jobs created by a user (recruiter)."""
        return await self.job_repo.find_by_created_by_user_id(user_id)

    async def update(
        self,
        id: uuid.UUID,
        payload: JobUpdate,
        user_id: uuid.UUID,
    ) -> Job:
        """Update a job. User must be a member of the job's organization."""
        job = await self.job_repo.find_by_id(id)
        if job is None:
            raise ValueError("Job not found")

        is_member = await self.org_repo.user_is_org_member(user_id, job.organization_id)
        if not is_member:
            raise ValueError("User is not a member of this organization")

        kwargs = {}
        if payload.title is not None:
            title = payload.title.strip()
            if not title:
                raise ValueError("Job title cannot be empty")
            kwargs["title"] = title
        if payload.description is not None:
            if not payload.description.strip():
                raise ValueError("Job description cannot be empty")
            kwargs["description"] = payload.description.strip()
        if payload.location is not None:
            if not payload.location.strip():
                raise ValueError("Job location cannot be empty")
            kwargs["location"] = payload.location.strip()
        if payload.employment_type is not None:
            if not payload.employment_type.strip():
                raise ValueError("Job employment type cannot be empty")
            kwargs["employment_type"] = payload.employment_type.strip()
        if payload.status is not None:
            kwargs["status"] = payload.status
        if payload.requirements_json is not None:
            kwargs["requirements_json"] = payload.requirements_json

        if kwargs:
            return await self.job_repo.update(job, **kwargs)
        return job

    async def delete(self, id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a job. User must be a member of the job's organization."""
        job = await self.job_repo.find_by_id(id)
        if job is None:
            raise ValueError("Job not found")

        is_member = await self.org_repo.user_is_org_member(user_id, job.organization_id)
        if not is_member:
            raise ValueError("User is not a member of this organization")

        await self.job_repo.delete(job)
