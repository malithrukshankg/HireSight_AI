import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Candidate


class CandidateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_user_and_organization(
        self, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Candidate | None:
        result = await self.db.execute(
            select(Candidate).where(
                Candidate.user_id == user_id,
                Candidate.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        email: str,
        full_name: str,
        phone: str | None,
        status: str = "new",
    ) -> Candidate:
        candidate = Candidate(
            organization_id=organization_id,
            user_id=user_id,
            email=email,
            full_name=full_name,
            phone=phone,
            status=status,
        )
        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate

    async def update(self, candidate: Candidate, **kwargs) -> Candidate:
        for key, value in kwargs.items():
            if hasattr(candidate, key) and value is not None:
                setattr(candidate, key, value)
        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate
