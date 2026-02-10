from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.repositories.userRepository import UserRepository
from api.services.userService import UserService
from api.schemas.userSchema import userCreate

class UserController:
    def __init__(self, db:AsyncSession):
        self.repo = UserRepository(db)
        self.service = UserService(self.repo)

    async def create_user(self,payload:userCreate):
        try:
            return await self.service.create_user(payload)
        except ValueError as e:
            raise HTTPException(status_code=400,detail=str(e))