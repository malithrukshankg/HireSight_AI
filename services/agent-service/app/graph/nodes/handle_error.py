from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def handle_error(state: AgentState) -> dict:
    logger.error(
        "handle_error: job_id=%s cv_id=%s request_id=%s fatal_error=%s",
        state["job_id"],
        state["cv_id"],
        state["request_id"],
        state.get("fatal_error"),
    )
    return {"steps_taken": state["steps_taken"] + ["handle_error"]}
