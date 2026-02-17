from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.schemas.userSchema import userCreate
import uuid

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

    async def find_by_email(self, email: str) -> User | None:
        """Find a user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def find_by_auth0_sub(self, auth0_sub: str) -> User | None:
        """Find a user by auth0_sub (primary identity reference for Auth0 users)."""
        result = await self.db.execute(select(User).where(User.auth0_sub == auth0_sub))
        return result.scalar_one_or_none()

    async def upsert_user(self, email: str, auth0_sub: str, role: str = "candidate") -> User:
        """Upsert a user: find by auth0_sub, update if exists, create if not."""
        user = await self.find_by_auth0_sub(auth0_sub)
        
        if user:
            # Update existing user - update email and role if changed
            if email and user.email != email:
                user.email = email
            if role and user.role != role:
                user.role = role
            await self.db.commit()
            await self.db.refresh(user)
            return user
        else:
            # Create new user
            new_user = User(
                email=email,
                auth0_sub=auth0_sub,
                role=role
            )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user