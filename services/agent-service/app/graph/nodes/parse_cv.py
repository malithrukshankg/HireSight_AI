from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def parse_cv(state: AgentState) -> dict:
    logger.info(
        "parse_cv: cv_id=%s request_id=%s",
        state["cv_id"],
        state["request_id"],
    )
    return {"steps_taken": state["steps_taken"] + ["parse_cv"]}
