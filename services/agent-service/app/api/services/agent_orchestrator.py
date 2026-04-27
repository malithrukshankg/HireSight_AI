from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.api.schemas.agent_schema import JDScoreRequest, JDScoreResponse
from app.graph.jd_cv_matching_graph import compiled_graph
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinates JD scoring and related AI workflows via the LangGraph pipeline."""

    async def run_jd_score(self, request: JDScoreRequest) -> JDScoreResponse:
        request_id = str(uuid.uuid4())

        initial_state: AgentState = {
            "job_id": request.job_id,
            "cv_id": request.cv_id,
            "candidate_id": None,
            "request_id": request_id,
            "triggered_by": "api",
            "jd_raw": None,
            "cv_raw": None,
            "parsed_jd": None,
            "parsed_cv": None,
            "jd_parse_metadata": None,
            "cv_parse_metadata": None,
            "jd_parse_valid": False,
            "cv_parse_valid": False,
            "normalized_jd": None,
            "normalized_cv": None,
            "matching_result": None,
            "match_score": None,
            "errors": [],
            "fatal_error": None,
            "steps_taken": [],
            "started_at": datetime.now(timezone.utc),
            "completed_at": None,
            "retry_count": 0,
        }

        logger.info(
            "jd-score: invoking graph job_id=%s cv_id=%s request_id=%s",
            request.job_id,
            request.cv_id,
            request_id,
        )

        final_state: AgentState = await compiled_graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": request_id}},
        )

        if final_state.get("fatal_error"):
            return JDScoreResponse(
                status="failed",
                job_id=request.job_id,
                cv_id=request.cv_id,
                scores={},
                notes=final_state["fatal_error"],
            )

        scores: dict = {}
        if final_state.get("matching_result"):
            scores = final_state["matching_result"]
        if final_state.get("match_score") is not None:
            scores["overall"] = final_state["match_score"]

        return JDScoreResponse(
            status="completed",
            job_id=request.job_id,
            cv_id=request.cv_id,
            scores=scores,
            notes=None,
        )
