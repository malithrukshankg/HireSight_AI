from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SERVICE_NAME: str = Field(default="agent-service", alias="SERVICE_NAME")
    CV_SERVICE_URL: str = Field(default="http://localhost:8001", alias="CV_SERVICE_URL")
    GATEWAY_SERVICE_URL: str = Field(default="http://localhost:8000", alias="GATEWAY_SERVICE_URL")
    HTTP_TIMEOUT_SECONDS: float = Field(default=30.0, alias="HTTP_TIMEOUT_SECONDS")

    # PostgreSQL connection string for LangGraph checkpointer (psycopg3 format)
    # e.g. postgresql://user:pass@localhost:5432/hiresight
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/hiresight", alias="DATABASE_URL")

    # PostgreSQL schema for LangGraph checkpoint tables
    LANGGRAPH_SCHEMA: str = Field(default="agent_schema", alias="LANGGRAPH_SCHEMA")

    # Parse version constants - bump these to force re-parse on next run
    EXPECTED_JD_PARSE_VERSION: str = Field(default="1.0", alias="EXPECTED_JD_PARSE_VERSION")
    EXPECTED_JD_MODEL_VERSION: str = Field(default="gemini-2.5-flash", alias="EXPECTED_JD_MODEL_VERSION")
    EXPECTED_JD_PROMPT_VERSION: str = Field(default="jd-parse-v1", alias="EXPECTED_JD_PROMPT_VERSION")

    EXPECTED_CV_PARSE_VERSION: str = Field(default="1.0", alias="EXPECTED_CV_PARSE_VERSION")
    EXPECTED_CV_MODEL_VERSION: str = Field(default="gpt-4o-mini", alias="EXPECTED_CV_MODEL_VERSION")
    EXPECTED_CV_PROMPT_VERSION: str = Field(default="cv-parse-v1", alias="EXPECTED_CV_PROMPT_VERSION")


settings = Settings()
