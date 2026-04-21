from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Loads from process environment and `.env` (same keys, uppercase).

    Gemini (JD parsing and other gateway AI): set GEMINI_API_KEY. Use a
    GEMINI_MODEL id that the current Gemini API supports (for example
    gemini-2.5-flash); retired names such as gemini-1.5-flash often return 404.
    Optional GEMINI_API_VERSION (for example v1) maps to the SDK HTTP api_version;
    leave unset to use the google-genai default. After changing dependencies or
    env, rebuild and restart the api-gateway process.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SQLALCHEMY_DATABASE_URI: str = Field(validation_alias="DATABASE_URL")
    SQLALCHEMY_ECHO: bool = Field(default=False, validation_alias="SQLALCHEMY_ECHO")
    CV_SERVICE_URL: str = Field(
        default="http://localhost:8001",
        validation_alias="CV_SERVICE_URL",
    )
    AGENT_SERVICE_URL: str = Field(
        default="http://localhost:8002",
        validation_alias="AGENT_SERVICE_URL",
    )
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        validation_alias="CORS_ORIGINS",
    )
    REDIS_ENABLED: bool = Field(default=True, validation_alias="REDIS_ENABLED")
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL",
    )
    REDIS_DEFAULT_TTL_SECONDS: int = Field(
        default=120,
        validation_alias="REDIS_DEFAULT_TTL_SECONDS",
    )
    REDIS_KEY_PREFIX: str = Field(default="hiresight", validation_alias="REDIS_KEY_PREFIX")
    JOBS_CACHE_TTL_SECONDS: int = Field(
        default=120,
        validation_alias="JOBS_CACHE_TTL_SECONDS",
    )

    # Gemini (google-genai) — optional; see class docstring.
    GEMINI_API_KEY: str | None = Field(
        default=None,
        validation_alias="GEMINI_API_KEY",
        description="Gemini API key (Gemini Developer API). Required for JD parsing.",
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        validation_alias="GEMINI_MODEL",
        description="Model id passed to generateContent (must be supported for your API version).",
    )
    GEMINI_TIMEOUT_SECONDS: int = Field(
        default=60,
        validation_alias="GEMINI_TIMEOUT_SECONDS",
        ge=1,
        description="HTTP timeout for each Gemini request, in seconds.",
    )
    GEMINI_API_VERSION: str | None = Field(
        default=None,
        validation_alias="GEMINI_API_VERSION",
        description=(
            "Optional REST API version for Gemini (e.g. v1, v1alpha). "
            "Forwarded to google-genai HttpOptions.api_version; omit for SDK default."
        ),
    )

    # JD parsing versioning - bump when the prompt or output schema changes so that
    # the agent-service knows to re-parse instead of reusing a stale result.
    JD_PARSE_VERSION: str = Field(
        default="1.0",
        validation_alias="JD_PARSE_VERSION",
    )
    JD_PROMPT_VERSION: str = Field(
        default="jd-parse-v1",
        validation_alias="JD_PROMPT_VERSION",
    )


settings = Settings()