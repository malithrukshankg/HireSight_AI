from fastapi import APIRouter

from app.api.controllers.agent_controller import AgentController
from app.api.schemas.agent_schema import JDScoreRequest, JDScoreResponse

internal_agent_router = APIRouter(prefix="/internal/agent", tags=["agent-internal"])


@internal_agent_router.post("/jd-score", response_model=JDScoreResponse)
async def jd_score(body: JDScoreRequest) -> JDScoreResponse:
    return await AgentController().jd_score(body)
