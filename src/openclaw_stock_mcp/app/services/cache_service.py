from __future__ import annotations

from threading import RLock

from cachetools import TTLCache


class CacheService:
    def __init__(self, maxsize: int = 1024, ttl: int = 60) -> None:
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = RLock()

    def get(self, key: str):
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value):
        with self._lock:
            self._cache[key] = value

    def has(self, key: str) -> bool:
        with self._lock:
            return key in self._cache
