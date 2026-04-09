from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SERVICE_NAME: str = Field(default="agent-service", alias="SERVICE_NAME")
    CV_SERVICE_URL: str = Field(default="http://localhost:8001", alias="CV_SERVICE_URL")
    GATEWAY_SERVICE_URL: str = Field(default="http://localhost:8000", alias="GATEWAY_SERVICE_URL")
    HTTP_TIMEOUT_SECONDS: float = Field(default=30.0, alias="HTTP_TIMEOUT_SECONDS")


settings = Settings()
