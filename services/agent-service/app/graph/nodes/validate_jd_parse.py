from __future__ import annotations

import hashlib
import logging

from app.config import settings
from app.graph.node_logger import get_node_logger
from app.graph.state import AgentState

logger = logging.getLogger(__name__)

_INVALID_REASON_LABELS = {
    "no_parse": "parsed_jd is None",
    "no_raw": "jd_raw is None - cannot verify content hash",
    "hash_mismatch": "content hash changed",
    "parse_version_mismatch": "parse_version changed",
    "model_version_mismatch": "model_version changed",
    "prompt_version_mismatch": "prompt_version changed",
}


def _compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def validate_jd_parse(state: AgentState) -> dict:
    log = get_node_logger(logger, state, "validate_jd_parse")

    parsed_jd = state.get("parsed_jd")
    jd_raw = state.get("jd_raw")
    meta = state.get("jd_parse_metadata") or {}

    invalid_reason: str | None = None

    if parsed_jd is None:
        invalid_reason = "no_parse"
    elif jd_raw is None:
        invalid_reason = "no_raw"
    elif _compute_hash(jd_raw) != meta.get("content_hash"):
        invalid_reason = "hash_mismatch"
    elif meta.get("parse_version") != settings.EXPECTED_JD_PARSE_VERSION:
        invalid_reason = "parse_version_mismatch"
    elif meta.get("model_version") != settings.EXPECTED_JD_MODEL_VERSION:
        invalid_reason = "model_version_mismatch"
    elif meta.get("prompt_version") != settings.EXPECTED_JD_PROMPT_VERSION:
        invalid_reason = "prompt_version_mismatch"

    valid = invalid_reason is None

    if valid:
        log.info("parse VALID")
    else:
        log.info("parse INVALID reason=%s", _INVALID_REASON_LABELS[invalid_reason])

    return {
        "jd_parse_valid": valid,
        "steps_taken": state["steps_taken"] + ["validate_jd_parse"],
    }
