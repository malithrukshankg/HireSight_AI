"""Thin wrapper around the Google Gemini API (`google-genai`)."""

from __future__ import annotations

import logging

from google import genai
from google.genai import errors
from google.genai import types

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
        model_name = self._model_name
        return bool(
            key and str(key).strip() and model_name and str(model_name).strip()
        )

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
            raise GeminiConfigurationError(
                "Gemini is not configured. Set GEMINI_API_KEY and GEMINI_MODEL."
            )

        if self._timeout_seconds <= 0:
            raise GeminiConfigurationError("GEMINI_TIMEOUT_SECONDS must be greater than 0")

        timeout_ms = int(self._timeout_seconds * 1000)
        http_options = types.HttpOptions(timeout=timeout_ms)

        config_kwargs: dict = {
            "temperature": temperature,
            "response_mime_type": "application/json",
        }
        if system_instruction is not None:
            config_kwargs["system_instruction"] = system_instruction

        try:
            with genai.Client(api_key=self._api_key.strip(), http_options=http_options) as client:
                response = client.models.generate_content(
                    model=self._model_name,
                    contents=user_content,
                    config=types.GenerateContentConfig(**config_kwargs),
                )
        except errors.APIError as e:
            logger.warning("Gemini API error (model=%s): %s", self._model_name, e)
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
