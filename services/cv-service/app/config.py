from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SQLALCHEMY_DATABASE_URI: str = Field(alias="DATABASE_URL")
    SQLALCHEMY_ECHO: bool = False
    CV_DB_SCHEMA: str = Field(default="cv_schema", alias="CV_DB_SCHEMA")
    S3_BUCKET: str = Field(default="hiresight-upload-cv", alias="S3_BUCKET")
    AWS_REGION: str = Field(default="ap-southeast-2", alias="AWS_REGION")
    CV_MAX_SIZE_MB: int = Field(default=5, alias="CV_MAX_SIZE_MB")
    CV_PLACEHOLDER_CANDIDATE_ID: str = Field(
        default="00000000-0000-0000-0000-000000000001",
        alias="CV_PLACEHOLDER_CANDIDATE_ID",
    )
    CV_PLACEHOLDER_UPLOADED_BY_USER_ID: str = Field(
        default="00000000-0000-0000-0000-000000000002",
        alias="CV_PLACEHOLDER_UPLOADED_BY_USER_ID",
    )
    OPENAI_API_KEY: str | None = Field(default=None, alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    CV_STRUCTURED_MAX_RETRIES: int = Field(default=2, alias="CV_STRUCTURED_MAX_RETRIES")

    # CV parsing versioning - bump when the prompt or output schema changes so that
    # the agent-service knows to re-parse instead of reusing a stale result.
    CV_PARSE_VERSION: str = Field(default="1.0", alias="CV_PARSE_VERSION")
    CV_PROMPT_VERSION: str = Field(default="cv-parse-v1", alias="CV_PROMPT_VERSION")


settings = Settings()
