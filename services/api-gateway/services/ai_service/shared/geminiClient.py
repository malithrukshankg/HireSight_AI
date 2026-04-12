"""Thin wrapper around the Google Gemini API (`google-genai`)."""

from __future__ import annotations

import logging
import threading
from typing import TypeVar

from google import genai
from google.genai import errors
from google.genai import types
from pydantic import BaseModel

from config import settings
from services.ai_service.shared.aiExceptions import (
    GeminiConfigurationError,
    GeminiInvocationError,
)
from services.ai_service.shared.structuredOutputHelper import (
    parse_and_validate,
    validate_pydantic,
)

TModel = TypeVar("TModel", bound=BaseModel)

logger = logging.getLogger(__name__)

_shared_genai_client: genai.Client | None = None
_shared_lock = threading.Lock()


def _client_http_options(*, timeout_ms: int) -> types.HttpOptions:
    ver = (settings.GEMINI_API_VERSION or "").strip()
    if ver:
        return types.HttpOptions(timeout=timeout_ms, api_version=ver)
    return types.HttpOptions(timeout=timeout_ms)


def _build_generate_config(
    *,
    system_instruction: str | None,
    temperature: float,
    response_schema: type[BaseModel] | None = None,
) -> types.GenerateContentConfig:
    config_kwargs: dict = {
        "temperature": temperature,
        "response_mime_type": "application/json",
    }
    if system_instruction is not None:
        config_kwargs["system_instruction"] = system_instruction
    if response_schema is not None:
        config_kwargs["response_schema"] = response_schema
    return types.GenerateContentConfig(**config_kwargs)


def _text_from_response(response: object) -> str:
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


def _structured_model_from_response(response: object, model_cls: type[TModel]) -> TModel:
    """Prefer SDK `response.parsed`; fall back to JSON text + `parse_and_validate`."""
    if not response.candidates:
        block = getattr(response, "prompt_feedback", None)
        logger.warning("Gemini returned no candidates; prompt_feedback=%s", block)
        raise GeminiInvocationError("Gemini returned no response candidates")

    parsed = getattr(response, "parsed", None)
    if parsed is not None:
        if isinstance(parsed, model_cls):
            return parsed
        if isinstance(parsed, dict):
            return validate_pydantic(parsed, model_cls)
        if isinstance(parsed, BaseModel):
            return validate_pydantic(parsed.model_dump(mode="json"), model_cls)

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
    return parse_and_validate(text, model_cls)


def _get_shared_genai_client() -> genai.Client:
    """Process-wide client for default gateway settings (Gemini Developer API)."""
    global _shared_genai_client
    key = (settings.GEMINI_API_KEY or "").strip()
    timeout_ms = int(settings.GEMINI_TIMEOUT_SECONDS * 1000)
    with _shared_lock:
        if _shared_genai_client is None:
            _shared_genai_client = genai.Client(
                api_key=key,
                http_options=_client_http_options(timeout_ms=timeout_ms),
            )
        return _shared_genai_client


async def close_shared_gemini_sdk_client_async() -> None:
    """Release HTTP resources; call from app shutdown when the shared client was used."""
    global _shared_genai_client
    with _shared_lock:
        client = _shared_genai_client
        _shared_genai_client = None
    if client is None:
        return
    try:
        await client.aio.aclose()
    except Exception:
        logger.debug("Gemini async client aclose failed", exc_info=True)
    try:
        client.close()
    except Exception:
        logger.debug("Gemini sync client close failed", exc_info=True)


class GeminiClient:
    """Gemini client: use `generate_structured_async` for Pydantic output (SDK response_schema)."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout_seconds: int | None = None,
    ):
        self._explicit_api_key = api_key is not None
        self._explicit_timeout = timeout_seconds is not None
        self._api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self._model_name = model_name or settings.GEMINI_MODEL
        self._timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else settings.GEMINI_TIMEOUT_SECONDS
        )

    def _uses_shared_backend(self) -> bool:
        return not self._explicit_api_key and not self._explicit_timeout

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
        Synchronous generate (new `genai.Client` per call). Use from threads or tests;
        async routes should call `generate_json_text_async`.
        """
        if not self.is_configured():
            raise GeminiConfigurationError(
                "Gemini is not configured. Set GEMINI_API_KEY and GEMINI_MODEL."
            )

        if self._timeout_seconds <= 0:
            raise GeminiConfigurationError("GEMINI_TIMEOUT_SECONDS must be greater than 0")

        timeout_ms = int(self._timeout_seconds * 1000)
        http_options = _client_http_options(timeout_ms=timeout_ms)
        config = _build_generate_config(
            system_instruction=system_instruction,
            temperature=temperature,
        )

        try:
            with genai.Client(api_key=self._api_key.strip(), http_options=http_options) as client:
                response = client.models.generate_content(
                    model=self._model_name,
                    contents=user_content,
                    config=config,
                )
        except errors.APIError as e:
            logger.warning("Gemini API error (model=%s): %s", self._model_name, e)
            raise GeminiInvocationError("Gemini request failed", cause=e) from e
        except Exception as e:
            logger.exception("Unexpected Gemini error")
            raise GeminiInvocationError("Gemini request failed unexpectedly", cause=e) from e

        return _text_from_response(response)

    def generate_structured(
        self,
        *,
        user_content: str,
        system_instruction: str | None = None,
        temperature: float = 0.2,
        model_cls: type[TModel],
    ) -> TModel:
        """
        Synchronous structured generate using SDK `response_schema` (Pydantic model).
        Falls back to parsing `response.text` when `response.parsed` is absent.
        """
        if not self.is_configured():
            raise GeminiConfigurationError(
                "Gemini is not configured. Set GEMINI_API_KEY and GEMINI_MODEL."
            )

        if self._timeout_seconds <= 0:
            raise GeminiConfigurationError("GEMINI_TIMEOUT_SECONDS must be greater than 0")

        timeout_ms = int(self._timeout_seconds * 1000)
        http_options = _client_http_options(timeout_ms=timeout_ms)
        config = _build_generate_config(
            system_instruction=system_instruction,
            temperature=temperature,
            response_schema=model_cls,
        )

        try:
            with genai.Client(api_key=self._api_key.strip(), http_options=http_options) as client:
                response = client.models.generate_content(
                    model=self._model_name,
                    contents=user_content,
                    config=config,
                )
        except errors.APIError as e:
            logger.warning("Gemini API error (model=%s): %s", self._model_name, e)
            raise GeminiInvocationError("Gemini request failed", cause=e) from e
        except Exception as e:
            logger.exception("Unexpected Gemini error")
            raise GeminiInvocationError("Gemini request failed unexpectedly", cause=e) from e

        return _structured_model_from_response(response, model_cls)

    async def generate_json_text_async(
        self,
        *,
        user_content: str,
        system_instruction: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        """
        Async generate. Uses a process-wide `genai.Client` when constructed with default
        gateway settings; otherwise a short-lived client for the request.
        """
        if not self.is_configured():
            raise GeminiConfigurationError(
                "Gemini is not configured. Set GEMINI_API_KEY and GEMINI_MODEL."
            )

        if self._timeout_seconds <= 0:
            raise GeminiConfigurationError("GEMINI_TIMEOUT_SECONDS must be greater than 0")

        config = _build_generate_config(
            system_instruction=system_instruction,
            temperature=temperature,
        )

        try:
            if self._uses_shared_backend():
                client = _get_shared_genai_client()
                response = await client.aio.models.generate_content(
                    model=self._model_name,
                    contents=user_content,
                    config=config,
                )
            else:
                timeout_ms = int(self._timeout_seconds * 1000)
                http_options = _client_http_options(timeout_ms=timeout_ms)
                with genai.Client(api_key=self._api_key.strip(), http_options=http_options) as client:
                    response = await client.aio.models.generate_content(
                        model=self._model_name,
                        contents=user_content,
                        config=config,
                    )
        except errors.APIError as e:
            logger.warning("Gemini API error (model=%s): %s", self._model_name, e)
            raise GeminiInvocationError("Gemini request failed", cause=e) from e
        except Exception as e:
            logger.exception("Unexpected Gemini error")
            raise GeminiInvocationError("Gemini request failed unexpectedly", cause=e) from e

        return _text_from_response(response)

    async def generate_structured_async(
        self,
        *,
        user_content: str,
        system_instruction: str | None = None,
        temperature: float = 0.2,
        model_cls: type[TModel],
    ) -> TModel:
        """
        Async structured generate using SDK `response_schema` (Pydantic model).
        Falls back to parsing `response.text` when `response.parsed` is absent.
        """
        if not self.is_configured():
            raise GeminiConfigurationError(
                "Gemini is not configured. Set GEMINI_API_KEY and GEMINI_MODEL."
            )

        if self._timeout_seconds <= 0:
            raise GeminiConfigurationError("GEMINI_TIMEOUT_SECONDS must be greater than 0")

        config = _build_generate_config(
            system_instruction=system_instruction,
            temperature=temperature,
            response_schema=model_cls,
        )

        try:
            if self._uses_shared_backend():
                client = _get_shared_genai_client()
                response = await client.aio.models.generate_content(
                    model=self._model_name,
                    contents=user_content,
                    config=config,
                )
            else:
                timeout_ms = int(self._timeout_seconds * 1000)
                http_options = _client_http_options(timeout_ms=timeout_ms)
                with genai.Client(api_key=self._api_key.strip(), http_options=http_options) as client:
                    response = await client.aio.models.generate_content(
                        model=self._model_name,
                        contents=user_content,
                        config=config,
                    )
        except errors.APIError as e:
            logger.warning("Gemini API error (model=%s): %s", self._model_name, e)
            raise GeminiInvocationError("Gemini request failed", cause=e) from e
        except Exception as e:
            logger.exception("Unexpected Gemini error")
            raise GeminiInvocationError("Gemini request failed unexpectedly", cause=e) from e

        return _structured_model_from_response(response, model_cls)
