from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def run_matching_analysis(state: AgentState) -> dict:
    logger.info(
        "run_matching_analysis: job_id=%s cv_id=%s request_id=%s",
        state["job_id"],
        state["cv_id"],
        state["request_id"],
    )
    return {"steps_taken": state["steps_taken"] + ["run_matching_analysis"]}
