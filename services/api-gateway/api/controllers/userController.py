from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.repositories.userRepository import UserRepository
from api.services.userService import UserService
from api.schemas.userSchema import userCreate
from models import User

class UserController:
    def __init__(self, db:AsyncSession):
        self.repo = UserRepository(db)
        self.service = UserService(self.repo)

    async def create_user(self,payload:userCreate):
        try:
            return await self.service.create_user(payload)
        except ValueError as e:
            raise HTTPException(status_code=400,detail=str(e))

    async def upsert_user(self, email: str, auth0_sub: str, role: str = "candidate") -> User:
        """Upsert a user by auth0_sub."""
        try:
            return await self.service.upsert_user(email, auth0_sub, role)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))