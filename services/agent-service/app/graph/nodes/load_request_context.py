from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def load_request_context(state: AgentState) -> dict:
    logger.info(
        "load_request_context: job_id=%s cv_id=%s",
        state["job_id"],
        state["cv_id"],
    )
    return {"steps_taken": state["steps_taken"] + ["load_request_context"]}
