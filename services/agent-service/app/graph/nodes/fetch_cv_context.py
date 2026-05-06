from __future__ import annotations

import logging
import uuid

import httpx

from app.clients.cv_service_client import CvServiceClient
from app.graph.node_logger import get_node_logger
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def fetch_cv_context(state: AgentState) -> dict:
    log = get_node_logger(logger, state, "fetch_cv_context")
    log.info("fetching CV context")

    try:
        payload = await CvServiceClient().get_cv_ai_context(state["cv_id"])
    except httpx.HTTPStatusError as exc:
        log.error("cv-service returned HTTP %s", exc.response.status_code)
        return {
            "fatal_error": f"Failed to fetch CV context: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["fetch_cv_context"],
        }
    except httpx.RequestError as exc:
        log.error("request error: %s", exc)
        return {
            "fatal_error": f"Failed to fetch CV context: {exc}",
            "steps_taken": state["steps_taken"] + ["fetch_cv_context"],
        }

    raw_metadata = payload.get("parse_metadata") or {}
    parse_metadata = {
        "parse_version": raw_metadata.get("parse_version"),
        "model_version": raw_metadata.get("model_version"),
        "prompt_version": raw_metadata.get("prompt_version"),
        "content_hash": raw_metadata.get("content_hash"),
        "parsed_at": raw_metadata.get("parsed_at"),
    }

    log.debug("fetched has_parsed_cv=%s", payload.get("parsed_profile") is not None)

    candidate_id_raw = payload.get("candidate_id")
    candidate_id = uuid.UUID(candidate_id_raw) if candidate_id_raw else None

    return {
        "cv_raw": payload.get("extracted_text"),
        "parsed_cv": payload.get("parsed_profile"),
        "cv_parse_metadata": parse_metadata,
        "candidate_id": candidate_id,
        "steps_taken": state["steps_taken"] + ["fetch_cv_context"],
    }
