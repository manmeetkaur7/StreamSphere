import json
import logging
import time
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Protocol

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class CacheBackend(Protocol):
    backend_name: str

    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str, ttl_seconds: int) -> None: ...

    def delete(self, key: str) -> None: ...

    def ping(self) -> bool: ...


class InMemoryCacheBackend:
    backend_name = "memory"

    def __init__(self) -> None:
        self._values: dict[str, tuple[str, float]] = {}

    def get(self, key: str) -> str | None:
        item = self._values.get(key)
        if item is None:
            return None
        value, expires_at = item
        if expires_at < time.time():
            self._values.pop(key, None)
            return None
        return value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._values[key] = (value, time.time() + ttl_seconds)

    def delete(self, key: str) -> None:
        self._values.pop(key, None)

    def ping(self) -> bool:
        return True


class RedisCacheBackend:
    backend_name = "redis"

    def __init__(self, url: str) -> None:
        self._client = Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._client.set(name=key, value=value, ex=ttl_seconds)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def ping(self) -> bool:
        return bool(self._client.ping())


class CacheService:
    def __init__(
        self,
        primary_backend: CacheBackend | None = None,
        fallback_backend: CacheBackend | None = None,
    ) -> None:
        settings = get_settings()
        self._fallback_backend = fallback_backend or InMemoryCacheBackend()
        if primary_backend is not None:
            self._primary_backend = primary_backend
        elif settings.redis_enabled:
            self._primary_backend = RedisCacheBackend(settings.redis_url)
        else:
            self._primary_backend = None

    @property
    def backend_name(self) -> str:
        if self._primary_backend is None:
            return self._fallback_backend.backend_name
        try:
            if self._primary_backend.ping():
                return self._primary_backend.backend_name
        except RedisError:
            return self._fallback_backend.backend_name
        return self._fallback_backend.backend_name

    def ping(self) -> tuple[bool, str]:
        if self._primary_backend is None:
            return True, self._fallback_backend.backend_name
        try:
            return self._primary_backend.ping(), self._primary_backend.backend_name
        except RedisError:
            logger.warning("Redis cache unavailable; falling back to in-memory cache.", exc_info=True)
            return False, self._fallback_backend.backend_name

    def get_json(self, key: str) -> Any | None:
        payload = self._read(key)
        if payload is None:
            return None
        return json.loads(payload)

    def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        settings = get_settings()
        effective_ttl = ttl_seconds or settings.cache_default_ttl_seconds
        serialized = json.dumps(value, default=str)
        self._write(key, serialized, effective_ttl)

    def delete(self, key: str) -> None:
        backends = [backend for backend in (self._primary_backend, self._fallback_backend) if backend]
        for backend in backends:
            try:
                backend.delete(key)
            except RedisError:
                logger.warning("Cache delete failed for key '%s'.", key, exc_info=True)

    def _read(self, key: str) -> str | None:
        if self._primary_backend is not None:
            try:
                value = self._primary_backend.get(key)
                if value is not None:
                    return value
            except RedisError:
                logger.warning("Redis cache read failed for key '%s'.", key, exc_info=True)
        return self._fallback_backend.get(key)

    def _write(self, key: str, value: str, ttl_seconds: int) -> None:
        if self._primary_backend is not None:
            try:
                self._primary_backend.set(key, value, ttl_seconds)
                return
            except RedisError:
                logger.warning("Redis cache write failed for key '%s'.", key, exc_info=True)
        self._fallback_backend.set(key, value, ttl_seconds)


class InMemoryRateLimitStore:
    def __init__(self) -> None:
        self._windows: dict[str, list[float]] = defaultdict(list)

    def increment(self, key: str, window_seconds: int) -> int:
        now = time.time()
        threshold = now - window_seconds
        self._windows[key] = [timestamp for timestamp in self._windows.get(key, []) if timestamp > threshold]
        self._windows[key].append(now)
        return len(self._windows[key])


class RedisRateLimitStore:
    def __init__(self, url: str) -> None:
        self._client = Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    def increment(self, key: str, window_seconds: int) -> int:
        pipeline = self._client.pipeline()
        pipeline.incr(key)
        pipeline.expire(key, window_seconds)
        count, _ = pipeline.execute()
        return int(count)


class RateLimitService:
    def __init__(
        self,
        primary_store: RedisRateLimitStore | None = None,
        fallback_store: InMemoryRateLimitStore | None = None,
    ) -> None:
        settings = get_settings()
        self._fallback_store = fallback_store or InMemoryRateLimitStore()
        if primary_store is not None:
            self._primary_store = primary_store
        elif settings.redis_enabled:
            self._primary_store = RedisRateLimitStore(settings.redis_url)
        else:
            self._primary_store = None

    def hit(self, key: str, window_seconds: int) -> int:
        if self._primary_store is not None:
            try:
                return self._primary_store.increment(key, window_seconds)
            except RedisError:
                logger.warning("Redis rate-limit store unavailable; using in-memory fallback.", exc_info=True)
        return self._fallback_store.increment(key, window_seconds)


_cache_service: CacheService | None = None
_rate_limit_service: RateLimitService | None = None


def get_cache_service() -> CacheService:
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def get_rate_limit_service() -> RateLimitService:
    global _rate_limit_service
    if _rate_limit_service is None:
        _rate_limit_service = RateLimitService()
    return _rate_limit_service


def reset_runtime_services() -> None:
    global _cache_service, _rate_limit_service
    _cache_service = None
    _rate_limit_service = None


def stable_cache_key(prefix: str, value: str) -> str:
    digest = sha256(value.strip().lower().encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"
