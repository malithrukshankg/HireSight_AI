from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def persist_results(state: AgentState) -> dict:
    logger.info(
        "persist_results: job_id=%s cv_id=%s request_id=%s",
        state["job_id"],
        state["cv_id"],
        state["request_id"],
    )
    return {"steps_taken": state["steps_taken"] + ["persist_results"]}
