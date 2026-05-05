import uuid
from typing import Any

from database import DBSession
from fastapi import APIRouter
from pydantic import BaseModel

from api.controllers.candidateController import CandidateController

internalCandidatesRouter = APIRouter(prefix="/internal/candidates", tags=["internal"])


class MatchResultPayload(BaseModel):
    match_score: float
    scores_json: dict[str, Any]


@internalCandidatesRouter.put("/{candidate_id}/match-result")
async def update_candidate_match_result(
    candidate_id: uuid.UUID,
    payload: MatchResultPayload,
    db: DBSession,
):
    return await CandidateController(db).update_match_result(
        candidate_id=candidate_id,
        match_score=payload.match_score,
        scores_json=payload.scores_json,
    )
