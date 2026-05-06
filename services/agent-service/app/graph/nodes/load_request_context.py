from __future__ import annotations

import logging

from app.graph.node_logger import get_node_logger
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def load_request_context(state: AgentState) -> dict:
    log = get_node_logger(logger, state, "load_request_context")
    log.info("graph started")
    return {"steps_taken": state["steps_taken"] + ["load_request_context"]}
