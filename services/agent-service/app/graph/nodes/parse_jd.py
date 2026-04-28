from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone

import httpx

from app.clients.gateway_client import GatewayClient
from app.config import settings
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def parse_jd(state: AgentState) -> dict:
    job_id = state["job_id"]
    request_id = state["request_id"]
    jd_raw = state.get("jd_raw")

    if not jd_raw:
        logger.error(
            "parse_jd: jd_raw missing, cannot re-parse job_id=%s request_id=%s",
            job_id,
            request_id,
        )
        return {
            "fatal_error": "Cannot re-parse JD: raw text is missing from state",
            "steps_taken": state["steps_taken"] + ["parse_jd"],
        }

    logger.info(
        "parse_jd: calling parse endpoint job_id=%s request_id=%s",
        job_id,
        request_id,
    )

    try:
        parsed_jd = await GatewayClient().parse_jd_text(description=jd_raw)
    except httpx.HTTPStatusError as exc:
        logger.error(
            "parse_jd: parse endpoint returned %s job_id=%s request_id=%s",
            exc.response.status_code,
            job_id,
            request_id,
        )
        return {
            "fatal_error": f"JD parse failed: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["parse_jd"],
        }
    except httpx.RequestError as exc:
        logger.error(
            "parse_jd: request error job_id=%s request_id=%s error=%s",
            job_id,
            request_id,
            exc,
        )
        return {
            "fatal_error": f"JD parse failed: {exc}",
            "steps_taken": state["steps_taken"] + ["parse_jd"],
        }

    parse_metadata = {
        "parse_version": settings.EXPECTED_JD_PARSE_VERSION,
        "model_version": settings.EXPECTED_JD_MODEL_VERSION,
        "prompt_version": settings.EXPECTED_JD_PROMPT_VERSION,
        "content_hash": hashlib.sha256(jd_raw.encode("utf-8")).hexdigest(),
        "parsed_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(
        "parse_jd: parse complete job_id=%s request_id=%s",
        job_id,
        request_id,
    )

    return {
        "parsed_jd": parsed_jd,
        "jd_parse_metadata": parse_metadata,
        "steps_taken": state["steps_taken"] + ["parse_jd"],
    }
