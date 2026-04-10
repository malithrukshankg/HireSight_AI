"""Exceptions for gateway AI features."""


class AiServiceError(Exception):
    """Base class for AI layer failures."""


class GeminiConfigurationError(AiServiceError):
    """Raised when Gemini is used but not configured (e.g. missing API key)."""


class GeminiInvocationError(AiServiceError):
    """Raised when the Gemini API call fails or returns an unusable response."""

    def __init__(self, message: str, cause: Exception | None = None):
        self.cause = cause
        super().__init__(message)


class StructuredOutputValidationError(AiServiceError):
    """Raised when model output is not valid JSON or fails Pydantic validation."""

    def __init__(self, message: str, cause: Exception | None = None):
        self.cause = cause
        super().__init__(message)
