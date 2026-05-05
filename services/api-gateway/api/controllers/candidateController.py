import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.candidateRepository import CandidateRepository
from api.services.candidateService import CandidateNotFoundError, CandidateService


class CandidateController:
    def __init__(self, db: AsyncSession):
        self.service = CandidateService(CandidateRepository(db))

    async def update_match_result(
        self,
        candidate_id: uuid.UUID,
        match_score: float,
        scores_json: dict[str, Any],
    ) -> dict:
        try:
            candidate = await self.service.update_match_result(
                candidate_id=candidate_id,
                match_score=match_score,
                scores_json=scores_json,
            )
        except CandidateNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return {"candidate_id": str(candidate.id), "match_score": candidate.match_score}
