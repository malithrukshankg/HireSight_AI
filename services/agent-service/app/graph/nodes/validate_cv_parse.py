from __future__ import annotations

import hashlib
import logging

from app.config import settings
from app.graph.state import AgentState

logger = logging.getLogger(__name__)

_INVALID_REASON_LABELS = {
    "no_parse": "parsed_cv is None",
    "no_raw": "cv_raw is None - cannot verify content hash",
    "hash_mismatch": "content hash changed",
    "parse_version_mismatch": "parse_version changed",
    "model_version_mismatch": "model_version changed",
    "prompt_version_mismatch": "prompt_version changed",
}


def _compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def validate_cv_parse(state: AgentState) -> dict:
    cv_id = state["cv_id"]
    request_id = state["request_id"]

    parsed_cv = state.get("parsed_cv")
    cv_raw = state.get("cv_raw")
    meta = state.get("cv_parse_metadata") or {}

    invalid_reason: str | None = None

    if parsed_cv is None:
        invalid_reason = "no_parse"
    elif cv_raw is None:
        invalid_reason = "no_raw"
    elif _compute_hash(cv_raw) != meta.get("content_hash"):
        invalid_reason = "hash_mismatch"
    elif meta.get("parse_version") != settings.EXPECTED_CV_PARSE_VERSION:
        invalid_reason = "parse_version_mismatch"
    elif meta.get("model_version") != settings.EXPECTED_CV_MODEL_VERSION:
        invalid_reason = "model_version_mismatch"
    elif meta.get("prompt_version") != settings.EXPECTED_CV_PROMPT_VERSION:
        invalid_reason = "prompt_version_mismatch"

    valid = invalid_reason is None

    if valid:
        logger.info(
            "validate_cv_parse: VALID cv_id=%s request_id=%s",
            cv_id,
            request_id,
        )
    else:
        logger.info(
            "validate_cv_parse: INVALID reason=%s cv_id=%s request_id=%s",
            _INVALID_REASON_LABELS[invalid_reason],
            cv_id,
            request_id,
        )

    return {
        "cv_parse_valid": valid,
        "steps_taken": state["steps_taken"] + ["validate_cv_parse"],
    }
