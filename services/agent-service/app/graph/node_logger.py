from __future__ import annotations

import logging

from app.graph.state import AgentState


class NodeLoggerAdapter(logging.LoggerAdapter):
    """Injects node_name, request_id, job_id, cv_id into every log record."""

    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        kwargs.setdefault("extra", {}).update(self.extra)
        return msg, kwargs


def get_node_logger(
    logger: logging.Logger,
    state: AgentState,
    node_name: str,
) -> NodeLoggerAdapter:
    return NodeLoggerAdapter(logger, {
        "node_name": node_name,
        "request_id": state.get("request_id", ""),
        "job_id": str(state.get("job_id", "")),
        "cv_id": str(state.get("cv_id", "")),
    })
