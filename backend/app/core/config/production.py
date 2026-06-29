from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """
    Production specific configuration settings.
    """

    DEBUG: bool = False
    ENV: str = "production"

    # Must be explicitly set in production environment variables
    # CORS_ORIGINS = ["https://yourdomain.com"]
    # ALLOWED_HOSTS = ["yourdomain.com"]
