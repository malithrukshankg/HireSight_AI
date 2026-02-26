from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SQLALCHEMY_DATABASE_URI: str = Field(alias="DATABASE_URL")
    SQLALCHEMY_ECHO: bool = False
    S3_BUCKET: str = "hiresight-upload-cv"
    AWS_REGION: str = "ap-southeast-2"
    CV_MAX_SIZE_MB: int = 5
    CV_PLACEHOLDER_CANDIDATE_ID: str = "00000000-0000-0000-0000-000000000001"
    CV_PLACEHOLDER_UPLOADED_BY_USER_ID: str = "00000000-0000-0000-0000-000000000002"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    REDIS_ENABLED: bool = True
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_DEFAULT_TTL_SECONDS: int = 120
    REDIS_KEY_PREFIX: str = "hiresight"


settings = Settings()