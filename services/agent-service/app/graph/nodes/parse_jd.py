from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def parse_jd(state: AgentState) -> dict:
    logger.info(
        "parse_jd: job_id=%s request_id=%s",
        state["job_id"],
        state["request_id"],
    )
    return {"steps_taken": state["steps_taken"] + ["parse_jd"]}
