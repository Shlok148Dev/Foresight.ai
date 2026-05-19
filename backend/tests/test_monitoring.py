"""
Foresight — Monitoring Tests
"""

import pytest


@pytest.mark.asyncio
async def test_prometheus_metrics(client):
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert "foresight_http_requests_total" in resp.text


@pytest.mark.asyncio
async def test_detailed_health(client):
    resp = await client.get("/health/detailed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "system" in data
    assert "cpu_percent" in data["system"]
    assert "memory_used_mb" in data["system"]
