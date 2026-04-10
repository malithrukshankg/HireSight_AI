from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Loads from process environment and `.env` (same keys, uppercase)."""

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

    # Gemini (google-generativeai) — optional; see module docstring.
    GEMINI_API_KEY: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(
        default="gemini-2.0-flash",
        validation_alias="GEMINI_MODEL",
    )
    GEMINI_TIMEOUT_SECONDS: int = Field(
        default=60,
        validation_alias="GEMINI_TIMEOUT_SECONDS",
    )


settings = Settings()