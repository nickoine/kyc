from __future__ import annotations

# External
from django.core.cache import caches

# Internal
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any


class AbstractCacheManager(ABC):
    """Abstract base class for cache managers."""


    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve an item from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set an item in cache."""
        pass

    @abstractmethod
    def get_or_set(self, key: str, default: Callable[[], Any], timeout: Optional[int] = None) -> Any:
        """Retrieve an item from cache or set it if not present."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete an item from cache."""
        pass

    @abstractmethod
    def incr(self, key: str, delta: int = 1) -> int:
        """Increment a cache value atomically."""
        pass


class CacheManager(AbstractCacheManager):
    """Django-based cache manager implementation."""

    CACHE_BACKEND = "default"
    CACHE_TIMEOUT: int = 60 * 15  # Default 15-minute timeout


    def _get_cache(self):
        """Get the appropriate cache backend."""
        return caches[self.CACHE_BACKEND]


    def get(self, key: str) -> Optional[Any]:
        """Retrieve an item from cache."""
        return self._get_cache().get(key)


    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set an item in cache."""
        self._get_cache().set(key, value, timeout or self.CACHE_TIMEOUT)


    def get_or_set(self, key: str, default: Callable[[], Any], timeout: Optional[int] = None) -> Any:
        """Retrieve an item from cache or set it if not present."""
        return self._get_cache().get_or_set(key, default, timeout or self.CACHE_TIMEOUT)


    def delete(self, key: str) -> None:
        """Delete an item from cache."""
        self._get_cache().delete(key)


    def incr(self, key: str, delta: int = 1) -> int:
        """Increment a cache value atomically."""

        cache = self._get_cache()
        return cache.incr(key, delta=delta) if cache.get(key) else 1


#
# class CacheManager:
#     """Handles caching operations independently of Django's cache module."""
#
#     CACHE_TIMEOUT = 60 * 15  # 15 minutes
#     CACHE_BACKEND = "default"
#
#     @classmethod
#     def get_cache(cls):
#         """Get the appropriate cache backend."""
#         return caches[cls.CACHE_BACKEND]
#
#     @classmethod
#     def get(cls, key: str) -> Optional[Any]:
#         """Retrieve an item from cache."""
#         return cls.get_cache().get(key)
#
#     @classmethod
#     def set(cls, key: str, value: Any, timeout: Optional[int] = None) -> None:
#         """Set an item in cache."""
#         cls.get_cache().set(key, value, timeout or cls.CACHE_TIMEOUT)
#
#     @classmethod
#     def get_or_set(cls, key: str, default: Callable[[], Any], timeout: Optional[int] = None) -> Any:
#         """Retrieve an item from cache or set it if not present."""
#         return cls.get_cache().get_or_set(key, default, timeout or cls.CACHE_TIMEOUT)
#
#     @classmethod
#     def delete(cls, key: str) -> None:
#         """Delete an item from cache."""
#         cls.get_cache().delete(key)
#
#     @classmethod
#     def incr(cls, key: str, delta: int = 1) -> int:
#         """Increment a cache value atomically."""
#         return cls.get_cache().incr(key, delta=delta) if cls.get_cache().get(key) else 1
