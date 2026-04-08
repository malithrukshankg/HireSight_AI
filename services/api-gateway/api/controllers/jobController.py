from typing import Optional
import uuid

import httpx
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.clients.cv_client import CvClient
from api.repositories.candidateRepository import CandidateRepository
from api.repositories.jobRepository import JobRepository
from api.repositories.organizationRepository import OrganizationRepository
from api.repositories.userRepository import UserRepository
from api.schemas.jobSchema import (
    JobApplicationRead,
    JobApplyResponse,
    JobCreate,
    JobRead,
    JobUpdate,
)
from api.services.jobService import JobService
from models import Job
from models.jobs import JobStatusEnum


class JobController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.candidate_repo = CandidateRepository(db)
        self.cv_client = CvClient()
        self.service = JobService(
            self.job_repo,
            self.org_repo,
            self.candidate_repo,
            self.cv_client,
        )

    def _handle_error(self, e: ValueError) -> None:
        msg = str(e).lower()
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        if "not a member" in msg:
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    async def create(self, payload: JobCreate, auth0_sub: str) -> Job:
        user_repo = UserRepository(self.db)
        user = await user_repo.find_by_auth0_sub(auth0_sub)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            return await self.service.create(payload, user_id=user.id)
        except ValueError as e:
            self._handle_error(e)

    async def get_by_id(self, id: uuid.UUID) -> Job:
        try:
            return await self.service.get_by_id(id)
        except ValueError as e:
            self._handle_error(e)

    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
        organization_id: uuid.UUID | None = None,
        status: JobStatusEnum | None = None,
        query: Optional[str] = None,
        location: Optional[str] = None,
        sort: str = "recent",
        role: Optional[str] = None,
    ) -> list[JobRead]:
        try:
            return await self.service.list_all(
                limit=limit,
                offset=offset,
                organization_id=organization_id,
                status=status,
                query=query,
                location=location,
                sort=sort,
                role=role,
            )
        except ValueError as e:
            self._handle_error(e)

    async def list_for_current_user(self, auth0_sub: str) -> list[Job]:
        user_repo = UserRepository(self.db)
        user = await user_repo.find_by_auth0_sub(auth0_sub)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            return await self.service.list_by_creator(user_id=user.id)
        except ValueError as e:
            self._handle_error(e)

    async def update(
        self,
        id: uuid.UUID,
        payload: JobUpdate,
        auth0_sub: str,
    ) -> Job:
        user_repo = UserRepository(self.db)
        user = await user_repo.find_by_auth0_sub(auth0_sub)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            return await self.service.update(id, payload, user_id=user.id)
        except ValueError as e:
            self._handle_error(e)

    async def delete(self, id: uuid.UUID, auth0_sub: str) -> None:
        user_repo = UserRepository(self.db)
        user = await user_repo.find_by_auth0_sub(auth0_sub)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            await self.service.delete(id, user_id=user.id)
        except ValueError as e:
            self._handle_error(e)

    async def apply(
        self,
        *,
        job_id: uuid.UUID,
        auth0_sub: str,
        email: str,
        full_name: str,
        phone: str | None,
        cv_file: UploadFile | None,
    ) -> JobApplyResponse:
        user_repo = UserRepository(self.db)
        user = await user_repo.find_by_auth0_sub(auth0_sub)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            result = await self.service.apply(
                job_id=job_id,
                user_id=user.id,
                email=email,
                full_name=full_name,
                phone=phone,
                cv_file=cv_file,
            )
            return JobApplyResponse.model_validate(result)
        except httpx.HTTPStatusError as e:
            try:
                detail = e.response.json().get("detail", str(e)) if e.response.text else str(e)
            except Exception:
                detail = e.response.text or str(e)
            raise HTTPException(status_code=e.response.status_code, detail=detail)
        except ValueError as e:
            self._handle_error(e)

    async def list_applications(
        self, *, job_id: uuid.UUID, auth0_sub: str
    ) -> list[JobApplicationRead]:
        user_repo = UserRepository(self.db)
        user = await user_repo.find_by_auth0_sub(auth0_sub)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            return await self.service.list_applications(job_id=job_id, user_id=user.id)
        except httpx.HTTPStatusError as e:
            try:
                detail = e.response.json().get("detail", str(e)) if e.response.text else str(e)
            except Exception:
                detail = e.response.text or str(e)
            raise HTTPException(status_code=e.response.status_code, detail=detail)
        except ValueError as e:
            self._handle_error(e)
