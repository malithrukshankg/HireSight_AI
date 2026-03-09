from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SQLALCHEMY_DATABASE_URI: str = Field(alias="DATABASE_URL")
    SQLALCHEMY_ECHO: bool = False
    CV_SERVICE_URL: str = "http://localhost:8001"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    REDIS_ENABLED: bool = True
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_DEFAULT_TTL_SECONDS: int = 120
    REDIS_KEY_PREFIX: str = "hiresight"
    JOBS_CACHE_TTL_SECONDS: int = 120


settings = Settings()