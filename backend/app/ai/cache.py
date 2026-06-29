from abc import ABC, abstractmethod
from typing import Any, Optional
import time

class AICacheInterface(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    async def clear(self) -> None:
        pass

class InMemoryCache(AICacheInterface):
    """
    A simple thread-safe in-memory cache for AI responses.
    Suitable for development or single-worker environments.
    """
    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    async def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if entry["expires_at"] is None or entry["expires_at"] > time.time():
                return entry["value"]
            else:
                del self._cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires_at = time.time() + ttl if ttl else None
        self._cache[key] = {"value": value, "expires_at": expires_at}

    async def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    async def clear(self) -> None:
        self._cache.clear()

# Global instance for the application to use
ai_cache = InMemoryCache()
