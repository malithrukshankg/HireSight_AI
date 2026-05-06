from __future__ import annotations

import logging

import httpx

from app.clients.gateway_client import GatewayClient
from app.graph.node_logger import get_node_logger
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def fetch_jd_context(state: AgentState) -> dict:
    log = get_node_logger(logger, state, "fetch_jd_context")
    log.info("fetching JD context")

    try:
        payload = await GatewayClient().get_job_ai_context(state["job_id"])
    except httpx.HTTPStatusError as exc:
        log.error("api-gateway returned HTTP %s", exc.response.status_code)
        return {
            "fatal_error": f"Failed to fetch job context: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["fetch_jd_context"],
        }
    except httpx.RequestError as exc:
        log.error("request error: %s", exc)
        return {
            "fatal_error": f"Failed to fetch job context: {exc}",
            "steps_taken": state["steps_taken"] + ["fetch_jd_context"],
        }

    raw_metadata = payload.get("parse_metadata") or {}
    parse_metadata = {
        "parse_version": raw_metadata.get("parse_version"),
        "model_version": raw_metadata.get("model_version"),
        "prompt_version": raw_metadata.get("prompt_version"),
        "content_hash": raw_metadata.get("content_hash"),
        "parsed_at": raw_metadata.get("parsed_at"),
    }

    log.debug("fetched has_parsed_jd=%s", payload.get("parsed_job_description") is not None)

    return {
        "jd_raw": payload.get("description"),
        "parsed_jd": payload.get("parsed_job_description"),
        "jd_parse_metadata": parse_metadata,
        "steps_taken": state["steps_taken"] + ["fetch_jd_context"],
    }
