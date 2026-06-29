import pytest

from app.core.config import get_settings


def test_settings_load_correctly(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that settings load and parse list fields from env vars."""
    # Test environment override with comma-separated list
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("ALLOWED_HOSTS", "localhost,127.0.0.1,test-render.onrender.com")
    settings = get_settings()
    assert settings.ENV == "development"
    assert settings.DEBUG is True
    assert "localhost" in settings.ALLOWED_HOSTS
    assert "127.0.0.1" in settings.ALLOWED_HOSTS
    assert "test-render.onrender.com" in settings.ALLOWED_HOSTS


def test_settings_json_list_format(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that JSON array format is also parsed correctly."""
    monkeypatch.setenv("ALLOWED_HOSTS", '["a.com","b.com"]')
    settings = get_settings()
    assert "a.com" in settings.ALLOWED_HOSTS
    assert "b.com" in settings.ALLOWED_HOSTS
