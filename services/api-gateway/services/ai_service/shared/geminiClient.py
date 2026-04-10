"""Thin wrapper around the Google Gemini API (`google-generativeai`)."""

from __future__ import annotations

import logging

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from config import settings
from services.ai_service.shared.aiExceptions import (
    GeminiConfigurationError,
    GeminiInvocationError,
)

logger = logging.getLogger(__name__)


class GeminiClient:
    """Synchronous Gemini client; use from async code via `asyncio.to_thread`."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout_seconds: int | None = None,
    ):
        self._api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self._model_name = model_name or settings.GEMINI_MODEL
        self._timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else settings.GEMINI_TIMEOUT_SECONDS
        )

    def is_configured(self) -> bool:
        key = self._api_key
        return bool(key and str(key).strip())

    def generate_json_text(
        self,
        *,
        user_content: str,
        system_instruction: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        """
        Ask the model for JSON-only output (`response_mime_type=application/json`).
        Returns the raw text (JSON string); validate with `structuredOutputHelper`.
        """
        if not self.is_configured():
            raise GeminiConfigurationError("GEMINI_API_KEY is not set or empty")

        genai.configure(api_key=self._api_key.strip())

        model = genai.GenerativeModel(
            self._model_name,
            system_instruction=system_instruction,
        )

        generation_config = genai.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json",
        )

        try:
            response = model.generate_content(
                user_content,
                generation_config=generation_config,
                request_options={"timeout": self._timeout_seconds},
            )
        except google_exceptions.GoogleAPIError as e:
            logger.warning("Gemini API error: %s", e)
            raise GeminiInvocationError("Gemini request failed", cause=e) from e
        except Exception as e:
            logger.exception("Unexpected Gemini error")
            raise GeminiInvocationError("Gemini request failed unexpectedly", cause=e) from e

        if not response.candidates:
            block = getattr(response, "prompt_feedback", None)
            logger.warning("Gemini returned no candidates; prompt_feedback=%s", block)
            raise GeminiInvocationError("Gemini returned no response candidates")

        try:
            text = (response.text or "").strip()
        except ValueError as e:
            logger.warning("Gemini response.text unavailable: %s", e)
            raise GeminiInvocationError(
                "Gemini response blocked or incomplete",
                cause=e,
            ) from e

        if not text:
            raise GeminiInvocationError("Gemini returned empty text")
        return text
