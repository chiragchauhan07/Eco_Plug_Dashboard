import os

from .base import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig


def get_settings() -> BaseConfig:
    env = os.getenv("ENV", "development").lower()
    if env == "production":
        return ProductionConfig()  # type: ignore
    return DevelopmentConfig()  # type: ignore


settings = get_settings()
