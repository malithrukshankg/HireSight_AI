from __future__ import annotations

import logging

import httpx

from app.clients.cv_service_client import CvServiceClient
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def fetch_cv_context(state: AgentState) -> dict:
    cv_id = state["cv_id"]
    request_id = state["request_id"]

    logger.info(
        "fetch_cv_context: cv_id=%s request_id=%s",
        cv_id,
        request_id,
    )

    try:
        payload = await CvServiceClient().get_cv_ai_context(cv_id)
    except httpx.HTTPStatusError as exc:
        logger.error(
            "fetch_cv_context: cv-service returned %s for cv_id=%s request_id=%s",
            exc.response.status_code,
            cv_id,
            request_id,
        )
        return {
            "fatal_error": f"Failed to fetch CV context: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["fetch_cv_context"],
        }
    except httpx.RequestError as exc:
        logger.error(
            "fetch_cv_context: request error cv_id=%s request_id=%s error=%s",
            cv_id,
            request_id,
            exc,
        )
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

    logger.debug(
        "fetch_cv_context: fetched cv_id=%s has_parsed_cv=%s request_id=%s",
        cv_id,
        payload.get("parsed_profile") is not None,
        request_id,
    )

    return {
        "cv_raw": payload.get("extracted_text"),
        "parsed_cv": payload.get("parsed_profile"),
        "cv_parse_metadata": parse_metadata,
        "steps_taken": state["steps_taken"] + ["fetch_cv_context"],
    }
