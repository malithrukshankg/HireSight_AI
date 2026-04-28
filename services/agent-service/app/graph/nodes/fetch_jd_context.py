from __future__ import annotations

import logging

import httpx

from app.clients.gateway_client import GatewayClient
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def fetch_jd_context(state: AgentState) -> dict:
    job_id = state["job_id"]
    request_id = state["request_id"]

    logger.info(
        "fetch_jd_context: job_id=%s request_id=%s",
        job_id,
        request_id,
    )

    try:
        payload = await GatewayClient().get_job_ai_context(job_id)
    except httpx.HTTPStatusError as exc:
        logger.error(
            "fetch_jd_context: gateway returned %s for job_id=%s request_id=%s",
            exc.response.status_code,
            job_id,
            request_id,
        )
        return {
            "fatal_error": f"Failed to fetch job context: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["fetch_jd_context"],
        }
    except httpx.RequestError as exc:
        logger.error(
            "fetch_jd_context: request error job_id=%s request_id=%s error=%s",
            job_id,
            request_id,
            exc,
        )
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

    logger.debug(
        "fetch_jd_context: fetched job_id=%s has_parsed_jd=%s request_id=%s",
        job_id,
        payload.get("parsed_job_description") is not None,
        request_id,
    )

    return {
        "jd_raw": payload.get("description"),
        "parsed_jd": payload.get("parsed_job_description"),
        "jd_parse_metadata": parse_metadata,
        "steps_taken": state["steps_taken"] + ["fetch_jd_context"],
    }
