from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """
    Base configuration settings shared across environments.
    """

    APP_NAME: str = "ECO PLUG AI Customer Intelligence Dashboard"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENV: str = "production"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    CORS_ORIGINS: List[str] = []
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # AI Configuration
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    CLAUDE_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )
