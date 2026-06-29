from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """
    Development specific configuration settings.
    """

    DEBUG: bool = True
    ENV: str = "development"

    # Allows all for easier local dev
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]
    ALLOWED_HOSTS: list[str] = ["*"]
