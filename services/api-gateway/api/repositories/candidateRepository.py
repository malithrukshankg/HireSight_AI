import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Candidate


class CandidateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_user_organization_and_job(
        self, user_id: uuid.UUID, organization_id: uuid.UUID, job_id: uuid.UUID
    ) -> Candidate | None:
        result = await self.db.execute(
            select(Candidate).where(
                Candidate.user_id == user_id,
                Candidate.organization_id == organization_id,
                Candidate.job_id == job_id,
            )
        )
        return result.scalar_one_or_none()

    async def find_by_id(self, candidate_id: uuid.UUID) -> Candidate | None:
        result = await self.db.execute(select(Candidate).where(Candidate.id == candidate_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        email: str,
        full_name: str,
        phone: str | None,
        status: str = "new",
    ) -> Candidate:
        candidate = Candidate(
            organization_id=organization_id,
            user_id=user_id,
            job_id=job_id,
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

    async def update_match_result(
        self,
        candidate_id: uuid.UUID,
        match_score: float,
        scores_json: dict[str, Any],
    ) -> Candidate | None:
        candidate = await self.find_by_id(candidate_id)
        if candidate is None:
            return None
        return await self.update(
            candidate,
            match_score=match_score,
            scores_json=scores_json,
            matched_at=datetime.now(timezone.utc),
        )

    async def list_by_job_id(
        self, job_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[Candidate]:
        result = await self.db.execute(
            select(Candidate)
            .where(
                Candidate.job_id == job_id,
                Candidate.organization_id == organization_id,
            )
            .order_by(desc(Candidate.created_at))
        )
        return list(result.scalars().all())
