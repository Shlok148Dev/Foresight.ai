"""
Foresight — Health Endpoint Tests
"""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_root_endpoint(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "Foresight API"
    assert data["docs"] == "/docs"


@pytest.mark.asyncio
async def test_docs_available(client):
    resp = await client.get("/docs")
    assert resp.status_code == 200
