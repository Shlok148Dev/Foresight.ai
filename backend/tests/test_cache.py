"""
Foresight — Redis Cache Tests
================================
Tests for cache operations (uses mock Redis).
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.cache.redis_cache import (
    cache_get,
    cache_set,
    cache_delete,
    signal_list_key,
    signal_detail_key,
    detection_list_key,
    detection_detail_key,
    user_session_key,
)


# ── Key Builder Tests ────────────────────────────────────────────

class TestKeyBuilders:
    def test_signal_list_key_default(self):
        key = signal_list_key()
        assert key == "signals:list:limit=50:offset=0"

    def test_signal_list_key_with_platform(self):
        key = signal_list_key(platform="twitter", limit=20, offset=10)
        assert "platform=twitter" in key
        assert "limit=20" in key
        assert "offset=10" in key

    def test_signal_detail_key(self):
        key = signal_detail_key("abc-123")
        assert key == "signals:detail:abc-123"

    def test_detection_list_key_default(self):
        key = detection_list_key()
        assert key == "detections:list:limit=50:offset=0"

    def test_detection_list_key_with_stage(self):
        key = detection_list_key(stage="emerging")
        assert "stage=emerging" in key

    def test_detection_detail_key(self):
        key = detection_detail_key("det-456")
        assert key == "detections:detail:det-456"

    def test_user_session_key(self):
        key = user_session_key("user-789")
        assert key == "sessions:user-789"


# ── Cache Operations Tests (with mock) ───────────────────────────

class TestCacheOperations:
    @pytest.mark.asyncio
    async def test_cache_get_returns_none_when_redis_unavailable(self):
        """Cache should return None gracefully when Redis is down."""
        with patch("app.cache.redis_cache.get_redis", new_callable=AsyncMock, return_value=None):
            result = await cache_get("test-key")
            assert result is None

    @pytest.mark.asyncio
    async def test_cache_set_returns_false_when_redis_unavailable(self):
        """Cache set should return False gracefully when Redis is down."""
        with patch("app.cache.redis_cache.get_redis", new_callable=AsyncMock, return_value=None):
            result = await cache_set("test-key", {"data": "value"})
            assert result is False

    @pytest.mark.asyncio
    async def test_cache_delete_returns_false_when_redis_unavailable(self):
        with patch("app.cache.redis_cache.get_redis", new_callable=AsyncMock, return_value=None):
            result = await cache_delete("test-key")
            assert result is False

    @pytest.mark.asyncio
    async def test_cache_get_with_mock_redis(self):
        """Test cache get with a mocked Redis client."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value='{"key": "value"}')

        with patch("app.cache.redis_cache.get_redis", new_callable=AsyncMock, return_value=mock_redis):
            result = await cache_get("test-key")
            assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_cache_set_with_mock_redis(self):
        """Test cache set with a mocked Redis client."""
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(return_value=True)

        with patch("app.cache.redis_cache.get_redis", new_callable=AsyncMock, return_value=mock_redis):
            result = await cache_set("test-key", {"data": 42}, ttl=60)
            assert result is True
