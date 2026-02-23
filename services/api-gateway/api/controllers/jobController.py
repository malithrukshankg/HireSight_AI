import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.jobRepository import JobRepository
from api.repositories.organizationRepository import OrganizationRepository
from api.repositories.userRepository import UserRepository
from api.schemas.jobSchema import JobCreate, JobUpdate
from api.services.jobService import JobService
from models import Job
from models.jobs import JobStatusEnum


class JobController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.service = JobService(self.job_repo, self.org_repo)

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
    ) -> list[Job]:
        try:
            return await self.service.list_all(
                limit=limit,
                offset=offset,
                organization_id=organization_id,
                status=status,
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
