from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def validate_cv_parse(state: AgentState) -> dict:
    logger.info(
        "validate_cv_parse: cv_id=%s request_id=%s",
        state["cv_id"],
        state["request_id"],
    )
    return {"steps_taken": state["steps_taken"] + ["validate_cv_parse"]}
