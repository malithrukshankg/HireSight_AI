from app.api.schemas.agent_schema import JDScoreRequest, JDScoreResponse
from app.api.services.agent_orchestrator import AgentOrchestrator


class AgentController:
    def __init__(self) -> None:
        self._orchestrator = AgentOrchestrator()

    async def jd_score(self, body: JDScoreRequest) -> JDScoreResponse:
        return await self._orchestrator.run_jd_score_stub(body)
