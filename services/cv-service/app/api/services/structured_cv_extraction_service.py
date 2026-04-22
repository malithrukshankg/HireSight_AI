from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import instructor
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.api.schemas.cv_schema import CVStructuredProfile
from app.config import settings

logger = logging.getLogger(__name__)


class StructuredExtractionConfigError(RuntimeError):
    pass


class StructuredExtractionProviderError(RuntimeError):
    pass


class StructuredExtractionValidationError(RuntimeError):
    pass


@dataclass
class CVExtractionResult:
    """Parsed CV profile together with the metadata needed for cache validity checks."""
    profile: CVStructuredProfile
    content_hash: str
    parse_version: str
    model_version: str
    prompt_version: str
    parsed_at: datetime


class StructuredCVExtractionService:
    """Extracts structured CV data from raw text using Instructor + OpenAI."""

    def __init__(self, *, api_key: str | None, model: str, max_retries: int = 2):
        self.api_key = (api_key or "").strip()
        self.model = model
        self.max_retries = max(1, int(max_retries))
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        if not self.api_key:
            raise StructuredExtractionConfigError(
                "OPENAI_API_KEY is not configured for structured CV extraction"
            )

        openai_client = AsyncOpenAI(api_key=self.api_key)
        self._client = instructor.from_openai(openai_client)
        return self._client

    def _build_messages(self, *, raw_text: str) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "You are a CV parser. Extract candidate profile data from CV text. "
                    "Return data that strictly matches the response schema."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Extract structured CV data from the text below. "
                    "If a field is missing, return an empty string for scalar fields and "
                    "an empty list for array fields.\n\n"
                    f"CV TEXT:\n{raw_text}"
                ),
            },
        ]

    async def extract_from_raw_text(self, *, raw_text: str) -> CVExtractionResult:
        text = (raw_text or "").strip()
        if not text:
            raise StructuredExtractionValidationError(
                "CV extracted text is empty; cannot run structured extraction"
            )

        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        logger.info("Structured CV extraction started: text_chars=%s", len(text))
        client = self._get_client()

        try:
            profile = await client.chat.completions.create(
                model=self.model,
                response_model=CVStructuredProfile,
                messages=self._build_messages(raw_text=text),
                temperature=0,
                max_retries=self.max_retries,
            )
            logger.info("Structured CV extraction succeeded: text_chars=%s", len(text))
            return CVExtractionResult(
                profile=profile,
                content_hash=content_hash,
                parse_version=settings.CV_PARSE_VERSION,
                model_version=self.model,
                prompt_version=settings.CV_PROMPT_VERSION,
                parsed_at=datetime.now(timezone.utc),
            )
        except ValidationError as e:
            logger.exception("Structured CV extraction validation failed")
            raise StructuredExtractionValidationError(
                "Structured CV extraction failed schema validation"
            ) from e
        except Exception as e:
            logger.exception("Structured CV extraction provider call failed")
            raise StructuredExtractionProviderError(
                "Failed to extract structured CV data from LLM provider"
            ) from e
