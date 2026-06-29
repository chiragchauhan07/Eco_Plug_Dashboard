import json
from typing import Any, List

from pydantic import model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


def _parse_list_value(v: Any) -> List[str]:
    """Parse a value that could be a list, JSON string, or comma-separated string."""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return []
        if v.startswith("["):
            try:
                return json.loads(v)
            except Exception:
                pass
        return [item.strip() for item in v.split(",") if item.strip()]
    return []


class _SafeEnvSettingsSource(EnvSettingsSource):
    """
    Custom EnvSettingsSource that gracefully handles comma-separated
    list values instead of requiring strict JSON arrays.
    """

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
    ALLOWED_HOSTS: List[str] = ["*"]

    # AI Configuration
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    CLAUDE_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    @model_validator(mode="before")
    @classmethod
    def parse_list_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Normalise CORS_ORIGINS and ALLOWED_HOSTS from any format."""
        for field in ("CORS_ORIGINS", "ALLOWED_HOSTS"):
            if field in data:
                data[field] = _parse_list_value(data[field])
        return data

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Replace default EnvSettingsSource with our safe variant that
        # can handle comma-separated strings for list fields.
        safe_env = _SafeEnvSettingsSource(
            settings_cls,
            case_sensitive=settings_cls.model_config.get("case_sensitive"),
            env_prefix=settings_cls.model_config.get("env_prefix", ""),
        )
        return (
            init_settings,
            safe_env,
            dotenv_settings,
            file_secret_settings,
        )
