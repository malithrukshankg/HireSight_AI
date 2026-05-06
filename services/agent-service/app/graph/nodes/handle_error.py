from __future__ import annotations

import logging

from app.graph.node_logger import get_node_logger
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def handle_error(state: AgentState) -> dict:
    log = get_node_logger(logger, state, "handle_error")
    log.error("graph aborted: fatal_error=%s", state.get("fatal_error"))
    return {"steps_taken": state["steps_taken"] + ["handle_error"]}
