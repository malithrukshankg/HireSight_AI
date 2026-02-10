from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.schemas.userSchema import userCreate

from models import User

class UserRepository:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create(self,payload:userCreate)->User:
        user = User(id=payload.id,organization_id="12234",email= payload.email,password_hash=payload.password,role=payload.role)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user