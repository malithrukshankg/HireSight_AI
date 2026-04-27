from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def fetch_cv_context(state: AgentState) -> dict:
    logger.info(
        "fetch_cv_context: cv_id=%s request_id=%s",
        state["cv_id"],
        state["request_id"],
    )
    return {"steps_taken": state["steps_taken"] + ["fetch_cv_context"]}
