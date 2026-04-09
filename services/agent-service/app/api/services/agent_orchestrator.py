import logging

from app.api.schemas.agent_schema import JDScoreRequest, JDScoreResponse

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinates JD scoring and related AI workflows (stub until LangGraph pipeline exists)."""

    async def run_jd_score_stub(self, request: JDScoreRequest) -> JDScoreResponse:
        logger.info(
            "jd-score stub: job_id=%s cv_id=%s",
            request.job_id,
            request.cv_id,
        )
        return JDScoreResponse(
            status="stub",
            job_id=request.job_id,
            cv_id=request.cv_id,
            scores={},
            notes="JD scoring pipeline not implemented yet.",
        )
