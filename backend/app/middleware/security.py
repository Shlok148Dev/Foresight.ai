"""
Foresight — Security Hardening Middleware
==========================================
Phase 1C: Security headers, account lockout, token blacklist.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from collections import defaultdict
from threading import Lock

# ── In-memory account lockout store ──────────────────────────────
_failed_attempts: dict[str, list[float]] = defaultdict(list)
_lockout_lock = Lock()
_LOCKOUT_WINDOW = 900  # 15 minutes
_MAX_ATTEMPTS = 5


def record_failed_login(identifier: str) -> bool:
    """Record a failed login attempt. Returns True if account is now locked."""
    now = time.time()
    with _lockout_lock:
        attempts = _failed_attempts[identifier]
        # Prune old attempts outside the window
        attempts[:] = [t for t in attempts if now - t < _LOCKOUT_WINDOW]
        attempts.append(now)
        return len(attempts) >= _MAX_ATTEMPTS


def is_locked_out(identifier: str) -> bool:
    """Check if an identifier (email/IP) is locked out."""
    now = time.time()
    with _lockout_lock:
        attempts = _failed_attempts.get(identifier, [])
        recent = [t for t in attempts if now - t < _LOCKOUT_WINDOW]
        return len(recent) >= _MAX_ATTEMPTS


def clear_failed_attempts(identifier: str) -> None:
    """Clear failed attempts on successful login."""
    with _lockout_lock:
        _failed_attempts.pop(identifier, None)


# ── Security Headers Middleware ───────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach OWASP-recommended security headers to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        # Remove server banner
        if "server" in response.headers:
            del response.headers["server"]
        return response
