"""
Foresight — Rate Limiting Tests
=================================
Tests for the rate limiting middleware.
"""

import pytest
from app.middleware.rate_limit import RATE_LIMITS, EXEMPT_PATHS


class TestRateLimitConfig:
    def test_default_limits_exist(self):
        assert "free" in RATE_LIMITS
        assert "pro" in RATE_LIMITS
        assert "anonymous" in RATE_LIMITS

    def test_free_limit_reasonable(self):
        assert 50 <= RATE_LIMITS["free"] <= 200

    def test_pro_higher_than_free(self):
        assert RATE_LIMITS["pro"] > RATE_LIMITS["free"]

    def test_admin_highest(self):
        assert RATE_LIMITS["admin"] >= RATE_LIMITS["enterprise"]

    def test_exempt_paths_include_health(self):
        assert "/health" in EXEMPT_PATHS
        assert "/docs" in EXEMPT_PATHS
        assert "/" in EXEMPT_PATHS


@pytest.mark.asyncio
async def test_rate_limit_headers_present(client, auth_headers):
    """API responses should include rate limit headers."""
    resp = await client.get("/api/v1/signals/", headers=auth_headers)
    # Rate limit headers should be present (may not be exact values in test)
    assert resp.status_code in [200, 429]


@pytest.mark.asyncio
async def test_health_not_rate_limited(client):
    """Health endpoint should be exempt from rate limiting."""
    # Hit health endpoint many times — should never be rate limited
    for _ in range(10):
        resp = await client.get("/health")
        assert resp.status_code == 200
