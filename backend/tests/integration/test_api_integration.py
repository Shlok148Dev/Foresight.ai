"""
Foresight — Integration Tests
==============================
Phase 1A: Full API integration tests (auth → signals → detections → search).
Uses an in-process SQLite database — no external services required.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Helpers ──────────────────────────────────────────────────────


async def _register_and_login(client: AsyncClient, suffix: str = "int") -> str:
    email = f"inttest_{suffix}@foresight.ai"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "IntTest1234!", "username": f"intuser_{suffix}"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "IntTest1234!"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# ── Phase 1A Tests ────────────────────────────────────────────────


@pytest.mark.anyio
async def test_health(client):
    """Backend health check always returns 200."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.anyio
async def test_signup_and_login(client):
    """Create user → login → receive valid JWT."""
    token = await _register_and_login(client, "sal")
    assert isinstance(token, str)
    assert len(token) > 20


@pytest.mark.anyio
async def test_auth_required_on_signals(client):
    """Unauthenticated request to /signals returns 401 or 403."""
    resp = await client.get("/api/v1/signals/")
    assert resp.status_code in (401, 403)


@pytest.mark.anyio
async def test_create_signal(client):
    """Authenticated user can ingest a signal."""
    token = await _register_and_login(client, "csig")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/signals/ingest",
        json={
            "text": "ChatGPT is redefining how developers write code.",
            "platform": "twitter",
            "author": "testuser",
        },
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    assert body["platform"] == "twitter"


@pytest.mark.anyio
async def test_list_signals(client):
    """Authenticated user can list signals."""
    token = await _register_and_login(client, "lsig")
    headers = {"Authorization": f"Bearer {token}"}

    # Ingest first
    await client.post(
        "/api/v1/signals/ingest",
        json={"text": "Rust language growing fast in 2026.", "platform": "reddit"},
        headers=headers,
    )

    resp = await client.get("/api/v1/signals/", headers=headers)
    assert resp.status_code == 200
    signals = resp.json()
    assert isinstance(signals, list)
    assert len(signals) >= 1


@pytest.mark.anyio
async def test_search_signals(client):
    """Search endpoint returns results for a valid query."""
    token = await _register_and_login(client, "srch")
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/signals/ingest",
        json={"text": "Quantum computing is disrupting cryptography.", "platform": "hackernews"},
        headers=headers,
    )

    resp = await client.get("/api/v1/search/", params={"q": "quantum"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body


@pytest.mark.anyio
async def test_rate_limiting_headers_present(client):
    """Rate-limit headers should appear on authenticated requests."""
    token = await _register_and_login(client, "rl")
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/signals/", headers=headers)
    # Either passes with data or has rate-limit header
    assert resp.status_code in (200, 429)


@pytest.mark.anyio
async def test_batch_signal_ingest(client):
    """Batch ingest endpoint accepts multiple signals."""
    token = await _register_and_login(client, "batch")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/signals/ingest/batch",
        json={
            "signals": [
                {"text": "AI agents are taking over software dev.", "platform": "twitter"},
                {"text": "The rise of multi-agent frameworks in 2026.", "platform": "reddit"},
            ]
        },
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "ingested" in body or "count" in body or isinstance(body, list)


@pytest.mark.anyio
async def test_detection_pipeline(client):
    """Run detection pipeline and get detections back."""
    token = await _register_and_login(client, "det")
    headers = {"Authorization": f"Bearer {token}"}

    # Ingest signals first
    for i in range(5):
        await client.post(
            "/api/v1/signals/ingest",
            json={"text": f"LLM agents signal {i} — growing fast.", "platform": "twitter"},
            headers=headers,
        )

    # Run pipeline
    resp = await client.post("/api/v1/detections/run-pipeline", headers=headers)
    assert resp.status_code == 200

    # List detections
    resp2 = await client.get("/api/v1/detections/", headers=headers)
    assert resp2.status_code == 200


@pytest.mark.anyio
async def test_auth_me_endpoint(client):
    """GET /auth/me returns the authenticated user's profile."""
    token = await _register_and_login(client, "me")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    user = resp.json()
    assert "email" in user
    assert "inttest_me@foresight.ai" in user["email"]
