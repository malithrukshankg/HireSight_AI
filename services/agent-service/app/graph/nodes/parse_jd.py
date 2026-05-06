from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone

import httpx

from app.clients.gateway_client import GatewayClient
from app.config import settings
from app.graph.node_logger import get_node_logger
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def parse_jd(state: AgentState) -> dict:
    log = get_node_logger(logger, state, "parse_jd")
    jd_raw = state.get("jd_raw")

    if not jd_raw:
        log.error("jd_raw missing from state, cannot re-parse")
        return {
            "fatal_error": "Cannot re-parse JD: raw text is missing from state",
            "steps_taken": state["steps_taken"] + ["parse_jd"],
        }

    log.info("calling parse endpoint")

    try:
        parsed_jd = await GatewayClient().parse_jd_text(description=jd_raw)
    except httpx.HTTPStatusError as exc:
        log.error("parse endpoint returned HTTP %s", exc.response.status_code)
        return {
            "fatal_error": f"JD parse failed: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["parse_jd"],
        }
    except httpx.RequestError as exc:
        log.error("request error: %s", exc)
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

    log.info("parse complete")

    return {
        "parsed_jd": parsed_jd,
        "jd_parse_metadata": parse_metadata,
        "steps_taken": state["steps_taken"] + ["parse_jd"],
    }
