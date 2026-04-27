from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def validate_jd_parse(state: AgentState) -> dict:
    logger.info(
        "validate_jd_parse: job_id=%s request_id=%s",
        state["job_id"],
        state["request_id"],
    )
    return {"steps_taken": state["steps_taken"] + ["validate_jd_parse"]}
