from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.api.schemas.agent_schema import JDScoreRequest, JDScoreResponse
import app.graph.jd_cv_matching_graph as _graph_module
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

        final_state: AgentState = await _graph_module.compiled_graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": request_id}},
        )

        if final_state.get("fatal_error"):
            return JDScoreResponse(
                status="failed",
                job_id=request.job_id,
                cv_id=request.cv_id,
                request_id=request_id,
                scores={},
                notes=final_state["fatal_error"],
            )

        result = final_state.get("matching_result") or {}
        scores = {
            "overall": result.get("overall", 0.0),
            "required_skills_coverage": result.get("required_skills_coverage", 0.0),
            "preferred_skills_coverage": result.get("preferred_skills_coverage", 0.0),
            "overall_skills_coverage": result.get("overall_skills_coverage", 0.0),
            "matched_required": result.get("matched_required", []),
            "matched_preferred": result.get("matched_preferred", []),
            "unmatched_required": result.get("unmatched_required", []),
        }

        return JDScoreResponse(
            status="completed",
            job_id=request.job_id,
            cv_id=request.cv_id,
            request_id=request_id,
            scores=scores,
            notes=None,
        )
