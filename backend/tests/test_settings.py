import pytest

from app.core.config import get_settings


def test_settings_load_correctly(monkeypatch: pytest.MonkeyPatch) -> None:
    # 1. Test defaults
    monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
    settings = get_settings()
    assert "*.onrender.com" in settings.ALLOWED_HOSTS

    # 2. Test environment override with comma-separated list
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("ALLOWED_HOSTS", "localhost,127.0.0.1,test-render.onrender.com")
    settings = get_settings()
    assert settings.ENV == "development"
    assert settings.DEBUG is True
    assert "localhost" in settings.ALLOWED_HOSTS
    assert "test-render.onrender.com" in settings.ALLOWED_HOSTS
