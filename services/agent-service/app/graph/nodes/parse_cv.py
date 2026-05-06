from __future__ import annotations

import logging

import httpx

from app.clients.cv_service_client import CvServiceClient
from app.graph.node_logger import get_node_logger
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def parse_cv(state: AgentState) -> dict:
    log = get_node_logger(logger, state, "parse_cv")
    log.info("triggering CV re-parse")

    client = CvServiceClient()

    try:
        await client.trigger_cv_parse(state["cv_id"])
    except httpx.HTTPStatusError as exc:
        log.error("trigger failed HTTP %s", exc.response.status_code)
        return {
            "fatal_error": f"CV parse trigger failed: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["parse_cv"],
        }
    except httpx.RequestError as exc:
        log.error("trigger request error: %s", exc)
        return {
            "fatal_error": f"CV parse trigger failed: {exc}",
            "steps_taken": state["steps_taken"] + ["parse_cv"],
        }

    log.info("trigger complete, re-fetching CV context")

    try:
        payload = await client.get_cv_ai_context(state["cv_id"])
    except httpx.HTTPStatusError as exc:
        log.error("re-fetch failed HTTP %s", exc.response.status_code)
        return {
            "fatal_error": f"CV context re-fetch failed: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["parse_cv"],
        }
    except httpx.RequestError as exc:
        log.error("re-fetch request error: %s", exc)
        return {
            "fatal_error": f"CV context re-fetch failed: {exc}",
            "steps_taken": state["steps_taken"] + ["parse_cv"],
        }

    raw_metadata = payload.get("parse_metadata") or {}
    parse_metadata = {
        "parse_version": raw_metadata.get("parse_version"),
        "model_version": raw_metadata.get("model_version"),
        "prompt_version": raw_metadata.get("prompt_version"),
        "content_hash": raw_metadata.get("content_hash"),
        "parsed_at": raw_metadata.get("parsed_at"),
    }

    return {
        "cv_raw": payload.get("extracted_text"),
        "parsed_cv": payload.get("parsed_profile"),
        "cv_parse_metadata": parse_metadata,
        "steps_taken": state["steps_taken"] + ["parse_cv"],
    }
