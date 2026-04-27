from __future__ import annotations

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def fetch_jd_context(state: AgentState) -> dict:
    logger.info(
        "fetch_jd_context: job_id=%s request_id=%s",
        state["job_id"],
        state["request_id"],
    )
    return {"steps_taken": state["steps_taken"] + ["fetch_jd_context"]}
