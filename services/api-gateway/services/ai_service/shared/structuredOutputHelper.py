"""Parse and validate structured (JSON) model output."""

from __future__ import annotations

import json
import logging
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from services.ai_service.shared.aiExceptions import StructuredOutputValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

_FENCE_PATTERN = re.compile(
    r"^\s*```(?:json)?\s*\n?(.*?)\n?```\s*$",
    re.DOTALL | re.IGNORECASE,
)


def strip_json_fences(raw: str) -> str:
    """Remove optional ``` / ```json fences from model output."""
    text = raw.strip()
    match = _FENCE_PATTERN.match(text)
    if match:
        return match.group(1).strip()
    return text


def parse_json_object(raw: str) -> dict:
    """Parse a JSON object string into a dict."""
    cleaned = strip_json_fences(raw)
    if not cleaned:
        raise StructuredOutputValidationError("Model returned empty content")
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning("JSON decode failed: %s", e)
        raise StructuredOutputValidationError("Model output is not valid JSON") from e
    if not isinstance(data, dict):
        raise StructuredOutputValidationError("Model output must be a JSON object")
    return data


def validate_pydantic(data: dict, model_cls: type[T]) -> T:
    """Validate a dict against a Pydantic model."""
    try:
        return model_cls.model_validate(data)
    except ValidationError as e:
        logger.warning("Pydantic validation failed: %s", e)
        raise StructuredOutputValidationError("Model output does not match expected schema") from e


def parse_and_validate(raw: str, model_cls: type[T]) -> T:
    """Parse JSON text and validate as `model_cls`."""
    return validate_pydantic(parse_json_object(raw), model_cls)
