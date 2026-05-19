"""
Foresight — Rate Limiting Middleware
=====================================
Token-bucket rate limiter using Redis.
Limits requests per user (authenticated) or per IP (anonymous).

Follows Technical Bible §2.3 — Rate Limiting specification.
Defaults: 100 requests/minute for free users, 500 for pro+.
"""

import time
import logging
import os
from typing import Optional

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("foresight.ratelimit")

# ── Configuration ────────────────────────────────────────────────

RATE_LIMITS = {
    "free": int(os.getenv("RATE_LIMIT_FREE", "100")),          # requests per minute
    "pro": int(os.getenv("RATE_LIMIT_PRO", "500")),
    "team": int(os.getenv("RATE_LIMIT_TEAM", "1000")),
    "enterprise": int(os.getenv("RATE_LIMIT_ENTERPRISE", "5000")),
    "admin": int(os.getenv("RATE_LIMIT_ADMIN", "10000")),
    "anonymous": int(os.getenv("RATE_LIMIT_ANON", "30")),      # anonymous/unauthenticated
}

WINDOW_SECONDS = 60  # 1 minute window

# Paths exempt from rate limiting
EXEMPT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/metrics", "/"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis token bucket.
    Falls back to in-memory limiter if Redis is unavailable.
    """

    def __init__(self, app):
        super().__init__(app)
        self._local_counters: dict[str, dict] = {}

    async def dispatch(self, request: Request, call_next):
        # Skip exempt paths
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        # Skip non-API paths
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Determine rate limit key and limit
        identifier, limit = self._get_rate_info(request)

        # Check rate limit
        allowed, remaining, reset = await self._check_limit(identifier, limit)

        if not allowed:
            logger.warning(f"Rate limit exceeded: {identifier} ({limit}/min)")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Try again later.",
                    "limit": limit,
                    "window": "60s",
                    "retry_after": reset,
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset),
                    "Retry-After": str(reset),
                },
            )

        # Process request and add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        return response

    def _get_rate_info(self, request: Request) -> tuple[str, int]:
        """Extract rate limit identifier and limit from request."""
        # Try to get user info from auth header (set by auth middleware)
        user_role = request.state.__dict__.get("user_role", None)
        user_id = request.state.__dict__.get("user_id", None)

        if user_id and user_role:
            limit = RATE_LIMITS.get(user_role, RATE_LIMITS["free"])
            return f"user:{user_id}", limit

        # Fall back to IP-based limiting
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        return f"ip:{client_ip}", RATE_LIMITS["anonymous"]

    async def _check_limit(
        self, identifier: str, limit: int
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit.
        Returns (allowed, remaining, seconds_until_reset).

        Tries Redis first, falls back to in-memory.
        """
        # Try Redis
        try:
            return await self._check_redis(identifier, limit)
        except Exception:
            pass

        # Fallback: in-memory
        return self._check_local(identifier, limit)

    async def _check_redis(
        self, identifier: str, limit: int
    ) -> tuple[bool, int, int]:
        """Rate limit check using Redis sliding window."""
        from app.cache.redis_cache import get_redis

        redis = await get_redis()
        if not redis:
            raise RuntimeError("Redis unavailable")

        key = f"ratelimit:{identifier}"
        now = int(time.time())
        window_start = now - WINDOW_SECONDS

        pipe = redis.pipeline()
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Add current request
        pipe.zadd(key, {str(now) + f":{id(now)}": now})
        # Count requests in window
        pipe.zcard(key)
        # Set expiry on the key
        pipe.expire(key, WINDOW_SECONDS + 1)

        results = await pipe.execute()
        request_count = results[2]

        remaining = max(limit - request_count, 0)
        reset = WINDOW_SECONDS

        return request_count <= limit, remaining, reset

    def _check_local(
        self, identifier: str, limit: int
    ) -> tuple[bool, int, int]:
        """Fallback in-memory rate limit check (simple counter)."""
        now = time.time()

        if identifier not in self._local_counters:
            self._local_counters[identifier] = {"count": 0, "window_start": now}

        entry = self._local_counters[identifier]

        # Reset window if expired
        if now - entry["window_start"] >= WINDOW_SECONDS:
            entry["count"] = 0
            entry["window_start"] = now

        entry["count"] += 1
        remaining = max(limit - entry["count"], 0)
        reset = int(WINDOW_SECONDS - (now - entry["window_start"]))

        return entry["count"] <= limit, remaining, max(reset, 0)
