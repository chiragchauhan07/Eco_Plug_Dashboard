import pytest

from app.core.config import get_settings


def test_settings_load_correctly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "development")
    settings = get_settings()
    assert settings.ENV == "development"
    assert settings.DEBUG is True
    assert "localhost" in settings.ALLOWED_HOSTS
