from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_emty=True, extra="ignore"
    )

    SQLALCHEMY_DATABASE_URI : str = ""
    SQLALCHEMY_ECHO: str = ""


settings = Settings()