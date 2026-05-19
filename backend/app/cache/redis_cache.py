"""
Foresight — Redis Caching Service
===================================
Provides async caching for hot paths:
  - Signal list queries
  - Detection results
  - User sessions

Cache invalidation: TTL-based with manual invalidation on write operations.
Follows Technical Bible §2.4 — Caching Layer.
"""

import json
import logging
import os
from typing import Optional, Any
from datetime import timedelta

logger = logging.getLogger("foresight.cache")

# ── Configuration ────────────────────────────────────────────────

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_TTL = int(os.getenv("REDIS_CACHE_TTL", "300"))  # 5 minutes


# ── Redis Connection ─────────────────────────────────────────────

_redis_client = None


async def get_redis():
    """
    Get or create the Redis async client.
    Returns None if Redis is unavailable (graceful degradation).
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        # Verify connection
        await _redis_client.ping()
        logger.info(f"Redis connected: {REDIS_URL}")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis unavailable ({e}) — caching disabled, operating without cache")
        _redis_client = None
        return None


async def close_redis():
    """Close the Redis connection pool."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


# ── Cache Operations ─────────────────────────────────────────────

async def cache_get(key: str) -> Optional[Any]:
    """
    Get a value from cache. Returns None on miss or if Redis is unavailable.
    Automatically deserializes JSON.
    """
    redis = await get_redis()
    if not redis:
        return None

    try:
        value = await redis.get(key)
        if value is not None:
            logger.debug(f"Cache HIT: {key}")
            return json.loads(value)
        logger.debug(f"Cache MISS: {key}")
        return None
    except Exception as e:
        logger.warning(f"Cache get error ({key}): {e}")
        return None


async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    """
    Set a value in cache with TTL (seconds).
    Automatically serializes to JSON.
    """
    redis = await get_redis()
    if not redis:
        return False

    try:
        serialized = json.dumps(value, default=str)
        await redis.set(key, serialized, ex=ttl)
        logger.debug(f"Cache SET: {key} (ttl={ttl}s)")
        return True
    except Exception as e:
        logger.warning(f"Cache set error ({key}): {e}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    redis = await get_redis()
    if not redis:
        return False

    try:
        await redis.delete(key)
        logger.debug(f"Cache DELETE: {key}")
        return True
    except Exception as e:
        logger.warning(f"Cache delete error ({key}): {e}")
        return False


async def cache_delete_pattern(pattern: str) -> int:
    """
    Delete all keys matching a pattern (e.g., 'signals:*').
    Returns count of deleted keys.
    """
    redis = await get_redis()
    if not redis:
        return 0

    try:
        keys = []
        async for key in redis.scan_iter(match=pattern, count=100):
            keys.append(key)

        if keys:
            deleted = await redis.delete(*keys)
            logger.debug(f"Cache DELETE pattern '{pattern}': {deleted} keys")
            return deleted
        return 0
    except Exception as e:
        logger.warning(f"Cache delete pattern error ({pattern}): {e}")
        return 0


# ── Cache Key Builders ───────────────────────────────────────────

def signal_list_key(
    platform: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """Build cache key for signal list queries."""
    parts = ["signals:list"]
    if platform:
        parts.append(f"platform={platform}")
    parts.append(f"limit={limit}")
    parts.append(f"offset={offset}")
    return ":".join(parts)


def signal_detail_key(signal_id: str) -> str:
    """Build cache key for single signal lookup."""
    return f"signals:detail:{signal_id}"


def detection_list_key(
    stage: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """Build cache key for detection list queries."""
    parts = ["detections:list"]
    if stage:
        parts.append(f"stage={stage}")
    parts.append(f"limit={limit}")
    parts.append(f"offset={offset}")
    return ":".join(parts)


def detection_detail_key(detection_id: str) -> str:
    """Build cache key for single detection lookup."""
    return f"detections:detail:{detection_id}"


def user_session_key(user_id: str) -> str:
    """Build cache key for user session data."""
    return f"sessions:{user_id}"


# ── Cache-Aside Helper ───────────────────────────────────────────

async def cache_aside(
    key: str,
    fetch_fn,
    ttl: int = DEFAULT_TTL,
) -> Any:
    """
    Cache-aside pattern: check cache first, fetch from DB on miss.

    Usage:
        data = await cache_aside(
            key="signals:list:limit=50:offset=0",
            fetch_fn=lambda: db.execute(query),
            ttl=300,
        )
    """
    # Check cache first
    cached = await cache_get(key)
    if cached is not None:
        return cached

    # Cache miss — fetch from source
    result = await fetch_fn()

    # Store in cache
    await cache_set(key, result, ttl=ttl)
    return result
