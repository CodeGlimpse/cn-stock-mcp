from cachetools import TTLCache


class CacheService:
    def __init__(self, maxsize: int = 1024, ttl: int = 60) -> None:
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str):
        return self._cache.get(key)

    def set(self, key: str, value):
        self._cache[key] = value

    def has(self, key: str) -> bool:
        return key in self._cache
