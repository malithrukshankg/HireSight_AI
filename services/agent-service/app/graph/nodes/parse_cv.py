from __future__ import annotations

import logging

import httpx

from app.clients.cv_service_client import CvServiceClient
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def parse_cv(state: AgentState) -> dict:
    cv_id = state["cv_id"]
    request_id = state["request_id"]

    logger.info(
        "parse_cv: triggering re-parse cv_id=%s request_id=%s",
        cv_id,
        request_id,
    )

    client = CvServiceClient()

    try:
        await client.trigger_cv_parse(cv_id)
    except httpx.HTTPStatusError as exc:
        logger.error(
            "parse_cv: trigger failed status=%s cv_id=%s request_id=%s",
            exc.response.status_code,
            cv_id,
            request_id,
        )
        return {
            "fatal_error": f"CV parse trigger failed: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["parse_cv"],
        }
    except httpx.RequestError as exc:
        logger.error(
            "parse_cv: request error cv_id=%s request_id=%s error=%s",
            cv_id,
            request_id,
            exc,
        )
        return {
            "fatal_error": f"CV parse trigger failed: {exc}",
            "steps_taken": state["steps_taken"] + ["parse_cv"],
        }

    logger.info(
        "parse_cv: trigger complete, re-fetching context cv_id=%s request_id=%s",
        cv_id,
        request_id,
    )

    try:
        payload = await client.get_cv_ai_context(cv_id)
    except httpx.HTTPStatusError as exc:
        logger.error(
            "parse_cv: re-fetch failed status=%s cv_id=%s request_id=%s",
            exc.response.status_code,
            cv_id,
            request_id,
        )
        return {
            "fatal_error": f"CV context re-fetch failed: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["parse_cv"],
        }
    except httpx.RequestError as exc:
        logger.error(
            "parse_cv: re-fetch request error cv_id=%s request_id=%s error=%s",
            cv_id,
            request_id,
            exc,
        )
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
