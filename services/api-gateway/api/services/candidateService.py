import uuid
from typing import Any

from api.repositories.candidateRepository import CandidateRepository
from models import Candidate


class CandidateNotFoundError(Exception):
    pass


class CandidateService:
    def __init__(self, candidate_repo: CandidateRepository):
        self.candidate_repo = candidate_repo

    async def update_match_result(
        self,
        candidate_id: uuid.UUID,
        match_score: float,
        scores_json: dict[str, Any],
    ) -> Candidate:
        candidate = await self.candidate_repo.update_match_result(
            candidate_id=candidate_id,
            match_score=match_score,
            scores_json=scores_json,
        )
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate {candidate_id} not found")
        return candidate
