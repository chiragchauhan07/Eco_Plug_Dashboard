from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware


def setup_compression(app: FastAPI) -> None:
    """
    Setup compression for the FastAPI application.
    """
    app.add_middleware(GZipMiddleware, minimum_size=1000)
