import logging
import uuid
from typing import Optional

from fastapi import UploadFile

from api.clients.cv_client import CvClient
from api.repositories.candidateRepository import CandidateRepository
from api.schemas.jobSchema import JobCreate, JobRead, JobUpdate
from config import settings
from core.cache_service import (
    build_cache_key,
    build_version_key,
    get_counter,
    get_json,
    incr_counter,
    set_json,
)
from api.repositories.jobRepository import JobRepository
from api.repositories.organizationRepository import OrganizationRepository
from models import Job
from models.jobs import JobStatusEnum

logger = logging.getLogger(__name__)


class JobService:
    def __init__(
        self,
        job_repo: JobRepository,
        org_repo: OrganizationRepository,
        candidate_repo: CandidateRepository | None = None,
        cv_client: CvClient | None = None,
    ):
        self.job_repo = job_repo
        self.org_repo = org_repo
        self.candidate_repo = candidate_repo
        self.cv_client = cv_client

    async def _bump_jobs_list_cache_version(self) -> None:
        version_key = build_version_key("jobs", "list")
        next_version = await incr_counter(version_key)
        if next_version is None:
            logger.warning("Job cache version bump skipped (Redis unavailable)")
            return
        logger.debug("Job cache version bumped to %s", next_version)

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

        job = await self.job_repo.create(
            organization_id=payload.organization_id,
            created_by_user_id=user_id,
            title=title,
            description=payload.description.strip(),
            location=payload.location.strip(),
            employment_type=payload.employment_type.strip(),
            status=payload.status,
            requirements_json=payload.requirements_json,
        )
        await self._bump_jobs_list_cache_version()
        return job

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
        role: Optional[str] = None,
    ) -> list[JobRead]:
        """List jobs with optional filters and pagination."""
        if limit < 1 or limit > 500:
            raise ValueError("Limit must be between 1 and 500")
        if offset < 0:
            raise ValueError("Offset must be non-negative")
        if sort not in ("recent",):
            raise ValueError("Sort must be one of: recent")

        normalized_query = query.strip() if query else None
        normalized_location = location.strip() if location else None
        cache_key: str | None = None

        if role == "candidate":
            version_key = build_version_key("jobs", "list")
            version = await get_counter(version_key, default=1)
            cache_key = build_cache_key(
                "jobs",
                "list",
                scope=role,
                version=version,
                params={
                    "organization_id": str(organization_id) if organization_id else None,
                    "status": status.value if status else None,
                    "query": normalized_query,
                    "location": normalized_location,
                    "limit": limit,
                    "offset": offset,
                    "sort": sort,
                },
            )
            cached_payload = await get_json(cache_key)
            if isinstance(cached_payload, list):
                logger.debug("Job list cache hit for role=%s key=%s", role, cache_key)
                return [JobRead.model_validate(item) for item in cached_payload]
            logger.debug("Job list cache miss for role=%s key=%s", role, cache_key)

        jobs = await self.job_repo.find_all(
            limit=limit,
            offset=offset,
            organization_id=organization_id,
            status=status,
            query=normalized_query,
            location=normalized_location,
            sort=sort,
        )
        serialized_jobs = [JobRead.model_validate(job) for job in jobs]

        if cache_key is not None:
            cache_written = await set_json(
                cache_key,
                [job.model_dump(mode="json") for job in serialized_jobs],
                ttl_seconds=settings.JOBS_CACHE_TTL_SECONDS,
            )
            if cache_written:
                logger.debug("Job list cache stored key=%s ttl=%s", cache_key, settings.JOBS_CACHE_TTL_SECONDS)
            else:
                logger.debug("Job list cache store skipped key=%s", cache_key)

        return serialized_jobs

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
            updated_job = await self.job_repo.update(job, **kwargs)
            await self._bump_jobs_list_cache_version()
            return updated_job
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
        await self._bump_jobs_list_cache_version()

    async def apply(
        self,
        *,
        job_id: uuid.UUID,
        user_id: uuid.UUID,
        email: str,
        full_name: str,
        phone: str | None,
        cv_file: UploadFile | None,
    ):
        if self.candidate_repo is None or self.cv_client is None:
            raise ValueError("Candidate/CV services are not configured")

        job = await self.job_repo.find_by_id(job_id)
        if job is None:
            raise ValueError("Job not found")
        if job.status != JobStatusEnum.open:
            raise ValueError("Job is not open for applications")

        normalized_email = (email or "").strip().lower()
        normalized_name = (full_name or "").strip()
        normalized_phone = phone.strip() if phone else None
        if not normalized_email:
            raise ValueError("Email is required")
        if not normalized_name:
            raise ValueError("Full name is required")

        candidate = await self.candidate_repo.find_by_user_and_organization(
            user_id=user_id,
            organization_id=job.organization_id,
        )
        if candidate is None:
            candidate = await self.candidate_repo.create(
                organization_id=job.organization_id,
                user_id=user_id,
                email=normalized_email,
                full_name=normalized_name,
                phone=normalized_phone,
                status="new",
            )
        else:
            candidate = await self.candidate_repo.update(
                candidate,
                email=normalized_email,
                full_name=normalized_name,
                phone=normalized_phone,
            )

        if cv_file is not None:
            cv_response = await self.cv_client.upload_for_candidate(
                file=cv_file,
                candidate_id=candidate.id,
                user_id=user_id,
            )
            cv_id = uuid.UUID(cv_response["id"])
        else:
            cv_response = await self.cv_client.get_by_candidate_id(candidate.id)
            if cv_response is None:
                raise ValueError("CV is required. Please upload a CV to apply.")
            cv_id = uuid.UUID(cv_response["id"])

        return {
            "job_id": job.id,
            "candidate_id": candidate.id,
            "cv_id": cv_id,
            "message": "Application details saved successfully",
        }
