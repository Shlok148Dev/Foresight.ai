"""
Foresight — Detections API Tests
===================================
Tests for detection CRUD endpoints.
"""

import pytest
import pytest_asyncio


@pytest.mark.asyncio
async def test_list_detections_requires_auth(client):
    """Detections endpoint requires authentication."""
    resp = await client.get("/api/v1/detections/")
    assert resp.status_code == 403  # No auth header


@pytest.mark.asyncio
async def test_list_detections_empty(client, auth_headers):
    """Empty detection list returns proper structure."""
    resp = await client.get("/api/v1/detections/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["detections"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_detection_not_found(client, auth_headers):
    """Getting non-existent detection returns 404."""
    resp = await client.get(
        "/api/v1/detections/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_detection_invalid_id(client, auth_headers):
    """Invalid UUID format returns 400."""
    resp = await client.get("/api/v1/detections/not-a-uuid", headers=auth_headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_stage_summary(client, auth_headers):
    """Stage summary returns all stages with counts."""
    resp = await client.get("/api/v1/detections/stages/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "stages" in data
    assert "total" in data
    # All stages should be present
    for stage in ["embryonic", "emerging", "accelerating", "peaking", "declining"]:
        assert stage in data["stages"]


@pytest.mark.asyncio
async def test_run_pipeline_empty(client, auth_headers):
    """Running pipeline with no signals returns zero detections."""
    resp = await client.post(
        "/api/v1/detections/run-pipeline?window_hours=24",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["detections_created"] == 0
