"""
Foresight — Signal API Tests
Covers: ingest, list, get-by-id, pagination, filtering, edge cases
"""

import pytest


@pytest.mark.asyncio
async def test_ingest_signal(client, auth_headers):
    resp = await client.post("/api/v1/signals/ingest", json={
        "text": "AI agents are disrupting traditional workflows across industries",
        "platform": "twitter",
        "author": "@techleader",
        "url": "https://twitter.com/techleader/status/123",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["platform"] == "twitter"
    assert "id" in data
    assert data["author"] == "@techleader"


@pytest.mark.asyncio
async def test_ingest_signal_minimal(client, auth_headers):
    resp = await client.post("/api/v1/signals/ingest", json={
        "text": "This is a minimal signal with just text and platform",
        "platform": "reddit",
    }, headers=auth_headers)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_ingest_signal_text_too_short(client, auth_headers):
    resp = await client.post("/api/v1/signals/ingest", json={
        "text": "short", "platform": "twitter"
    }, headers=auth_headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_ingest_signal_invalid_platform(client, auth_headers):
    resp = await client.post("/api/v1/signals/ingest", json={
        "text": "A valid length signal text here for testing",
        "platform": "nonexistent_platform"
    }, headers=auth_headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_ingest_signal_no_auth(client):
    resp = await client.post("/api/v1/signals/ingest", json={
        "text": "Signal without authentication should fail",
        "platform": "twitter"
    })
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_signals(client, auth_headers):
    # Ingest 3 signals
    for i in range(3):
        await client.post("/api/v1/signals/ingest", json={
            "text": f"Test signal number {i} with enough text length",
            "platform": "twitter",
        }, headers=auth_headers)

    resp = await client.get("/api/v1/signals/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 3
    assert len(data["signals"]) >= 3
    assert "limit" in data
    assert "offset" in data


@pytest.mark.asyncio
async def test_list_signals_pagination(client, auth_headers):
    for i in range(5):
        await client.post("/api/v1/signals/ingest", json={
            "text": f"Pagination test signal number {i} here",
            "platform": "reddit",
        }, headers=auth_headers)

    resp = await client.get("/api/v1/signals/?limit=2&offset=0", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["signals"]) <= 2
    assert data["limit"] == 2
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_list_signals_filter_platform(client, auth_headers):
    await client.post("/api/v1/signals/ingest", json={
        "text": "Discord signal for filter testing purposes",
        "platform": "discord",
    }, headers=auth_headers)

    resp = await client.get("/api/v1/signals/?platform=discord", headers=auth_headers)
    assert resp.status_code == 200
    for s in resp.json()["signals"]:
        assert s["platform"] == "discord"


@pytest.mark.asyncio
async def test_get_signal_by_id(client, auth_headers):
    create = await client.post("/api/v1/signals/ingest", json={
        "text": "Signal for get-by-id test with enough text",
        "platform": "github",
    }, headers=auth_headers)
    signal_id = create.json()["id"]

    resp = await client.get(f"/api/v1/signals/{signal_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == signal_id


@pytest.mark.asyncio
async def test_get_signal_not_found(client, auth_headers):
    resp = await client.get(
        "/api/v1/signals/00000000-0000-0000-0000-000000000000",
        headers=auth_headers
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_signal_invalid_id(client, auth_headers):
    resp = await client.get("/api/v1/signals/not-a-uuid", headers=auth_headers)
    assert resp.status_code == 400
