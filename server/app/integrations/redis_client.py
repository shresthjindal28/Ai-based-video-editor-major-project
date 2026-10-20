from __future__ import annotations

import asyncio
import json
import logging
import random
import secrets
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.metrics import CACHE

logger = logging.getLogger(__name__)
T = TypeVar("T")
_redis: Redis | None = None
_local_locks: dict[str, asyncio.Lock] = {}


def redis_client() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(get_settings().redis_url, decode_responses=True, socket_timeout=2)
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await cast(Any, _redis).aclose()
        _redis = None


class Cache:
    """Tenant-aware cache-aside. Redis failures never affect source-of-truth operations."""

    def __init__(self, client: Redis | None = None, namespace: str = "autocut:v1"):
        self.client = client or redis_client()
        self.namespace = namespace

    def key(self, name: str, scope: str, identity: str) -> str:
        return f"{name}:{scope}:{identity}"

    async def get_or_load(
        self,
        key: str,
        loader: Callable[[], Awaitable[T | None]],
        ttl: int | None = None,
        *,
        negative_ttl: int = 0,
    ) -> T | None:
        full_key = f"{self.namespace}:{key}"
        try:
            value = await self.client.get(full_key)
            if value is not None:
                CACHE.labels(outcome="hit").inc()
                decoded = json.loads(value)
                if isinstance(decoded, dict) and decoded.get("__negative__") is True:
                    return None  # type: ignore[return-value]
                return cast(T, decoded)
        except Exception:
            CACHE.labels(outcome="error").inc()
            logger.warning("cache read failed; using database", extra={"operation": "cache_read"})
        CACHE.labels(outcome="miss").inc()
        lock = _local_locks.setdefault(full_key, asyncio.Lock())
        async with lock:
            token = secrets.token_urlsafe(24)
            lock_key = f"{full_key}:fill-lock"
            distributed_lock = False
            try:
                value = await self.client.get(full_key)
                if value is not None:
                    CACHE.labels(outcome="hit").inc()
                    decoded = json.loads(value)
                    return cast(
                        T | None,
                        (
                            None
                            if isinstance(decoded, dict) and decoded.get("__negative__")
                            else decoded
                        ),
                    )
            except Exception:
                pass
            try:
                distributed_lock = bool(await self.client.set(lock_key, token, nx=True, ex=15))
            except Exception:
                CACHE.labels(outcome="error").inc()
            if not distributed_lock:
                for _ in range(10):
                    await asyncio.sleep(0.05)
                    try:
                        value = await self.client.get(full_key)
                        if value is not None:
                            decoded = json.loads(value)
                            CACHE.labels(outcome="hit").inc()
                            return cast(
                                T | None,
                                None if isinstance(decoded, dict) and decoded.get("__negative__") else decoded,
                            )
                    except Exception:
                        break
            try:
                loaded = await loader()
                if loaded is None and negative_ttl <= 0:
                    return loaded
                try:
                    expiry = negative_ttl if loaded is None else (ttl or get_settings().cache_ttl_seconds)
                    expiry = max(1, int(expiry * random.uniform(0.9, 1.1)))
                    encoded = {"__negative__": True} if loaded is None else loaded
                    await self.client.set(
                        full_key, json.dumps(encoded, separators=(",", ":"), default=str), ex=expiry
                    )
                except Exception:
                    CACHE.labels(outcome="error").inc()
                    logger.warning("cache write failed", extra={"operation": "cache_write"})
                return loaded
            finally:
                if distributed_lock:
                    try:
                        await self.client.eval(
                            "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end",
                            1, lock_key, token,
                        )
                    except Exception:
                        CACHE.labels(outcome="error").inc()

    async def invalidate(self, key: str) -> None:
        try:
            await self.client.delete(f"{self.namespace}:{key}")
        except Exception:
            CACHE.labels(outcome="error").inc()
            logger.warning("cache invalidation failed", extra={"operation": "cache_invalidate"})

    async def invalidate_prefix(self, prefix: str) -> None:
        try:
            cursor = 0
            pattern = f"{self.namespace}:{prefix}*"
            while True:
                cursor, keys = await self.client.scan(cursor=cursor, match=pattern, count=200)
                if keys:
                    await self.client.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            CACHE.labels(outcome="error").inc()
            logger.warning(
                "cache prefix invalidation failed", extra={"operation": "cache_invalidate"}
            )


class RedisLock:
    """Lease lock with token-checked release; DB checks remain authoritative."""

    def __init__(self, key: str, ttl: int = 60, client: Redis | None = None):
        self.client = client or redis_client()
        self.key = f"autocut:lock:v1:{key}"
        self.ttl = ttl
        self.token = secrets.token_urlsafe(24)

    async def acquire(self) -> bool:
        return bool(await self.client.set(self.key, self.token, nx=True, ex=self.ttl))

    async def release(self) -> None:
        await self.client.eval(
            "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end",
            1,
            self.key,
            self.token,
        )
