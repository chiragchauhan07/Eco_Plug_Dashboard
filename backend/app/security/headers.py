from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware


def setup_trusted_host(app: FastAPI, allowed_hosts: list[str]) -> None:
    """
    Setup Trusted Host Middleware to prevent HTTP Host Header attacks.
    """
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
