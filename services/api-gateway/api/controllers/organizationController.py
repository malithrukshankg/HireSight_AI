import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.organizationRepository import OrganizationRepository
from api.repositories.userRepository import UserRepository
from api.schemas.organizationSchema import OrganizationCreate, OrganizationUpdate
from api.services.organizationService import OrganizationService
from models import Organization


class OrganizationController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OrganizationRepository(db)
        self.service = OrganizationService(self.repo)

    def _handle_error(self, e: ValueError) -> None:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    async def create(self, payload: OrganizationCreate, auth0_sub: str) -> Organization:
        user_repo = UserRepository(self.db)
        user = await user_repo.find_by_auth0_sub(auth0_sub)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            return await self.service.create(payload, user_id=user.id)
        except ValueError as e:
            self._handle_error(e)

    async def get_by_id(self, id: uuid.UUID) -> Organization:
        try:
            return await self.service.get_by_id(id)
        except ValueError as e:
            self._handle_error(e)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Organization]:
        try:
            return await self.service.list_all(limit=limit, offset=offset)
        except ValueError as e:
            self._handle_error(e)

    async def list_for_current_user(self, auth0_sub: str) -> list[Organization]:
        user_repo = UserRepository(self.db)
        user = await user_repo.find_by_auth0_sub(auth0_sub)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            return await self.service.list_for_user(user_id=user.id)
        except ValueError as e:
            self._handle_error(e)

    async def update(self, id: uuid.UUID, payload: OrganizationUpdate) -> Organization:
        try:
            return await self.service.update(id, payload)
        except ValueError as e:
            self._handle_error(e)

    async def delete(self, id: uuid.UUID) -> None:
        try:
            await self.service.delete(id)
        except ValueError as e:
            self._handle_error(e)
