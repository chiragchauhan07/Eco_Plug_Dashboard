import json
from typing import Any, List

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class CustomEnvSettingsSource(EnvSettingsSource):
    def decode_complex_value(self, field_name: str, field: FieldInfo, value: str) -> Any:
        try:
            return json.loads(value)
        except Exception:
            return [item.strip() for item in value.split(",") if item.strip()]


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
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*.onrender.com"]

    # AI Configuration
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    CLAUDE_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Wrap EnvSettingsSource to parse comma-separated lists gracefully
        custom_env_settings = CustomEnvSettingsSource(
            settings_cls,
            case_sensitive=settings_cls.model_config.get("case_sensitive"),
            env_prefix=settings_cls.model_config.get("env_prefix", ""),
        )
        return (
            init_settings,
            custom_env_settings,
            dotenv_settings,
            file_secret_settings,
        )
