import pytest

from app.database.session import engine


@pytest.mark.asyncio
async def test_database_url_configured() -> None:
    """
    Test that the database engine can be instantiated correctly.
    Does not actually connect to avoid requiring a running DB during simple CI.
    """
    assert engine.url.database is not None
