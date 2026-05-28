"""
Foresight — Performance & Security Tests
==========================================
Phase 1C/D: API response time, concurrent load, and security header checks.
"""

import time
import asyncio
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


async def _get_token(client: AsyncClient, tag: str) -> str:
    email = f"perf_{tag}@foresight.ai"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "PerfTest123!", "username": f"perf_{tag}"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "PerfTest123!"},
    )
    return resp.json()["access_token"]


# ── Performance Tests ─────────────────────────────────────────────


@pytest.mark.anyio
async def test_health_response_time(client):
    """Health endpoint must respond in < 200ms."""
    start = time.perf_counter()
    resp = await client.get("/health")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert resp.status_code == 200
    assert elapsed_ms < 200, f"Health check took {elapsed_ms:.1f}ms (limit: 200ms)"


@pytest.mark.anyio
async def test_login_response_time(client):
    """Login endpoint must respond in < 500ms (bcrypt overhead acceptable)."""
    email = "perf_login@foresight.ai"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "PerfTest123!", "username": "perf_login"},
    )
    start = time.perf_counter()
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "PerfTest123!"},
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert resp.status_code == 200
    assert elapsed_ms < 500, f"Login took {elapsed_ms:.1f}ms (limit: 500ms)"


@pytest.mark.anyio
async def test_signals_list_response_time(client):
    """Signals list must respond in < 300ms."""
    token = await _get_token(client, "list_time")
    headers = {"Authorization": f"Bearer {token}"}

    start = time.perf_counter()
    resp = await client.get("/api/v1/signals/", headers=headers)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert resp.status_code == 200
    assert elapsed_ms < 300, f"Signals list took {elapsed_ms:.1f}ms (limit: 300ms)"


@pytest.mark.anyio
async def test_concurrent_requests(client):
    """Handle 10 concurrent signal ingest requests without errors."""
    token = await _get_token(client, "concurrent")
    headers = {"Authorization": f"Bearer {token}"}

    async def ingest(i: int):
        return await client.post(
            "/api/v1/signals/ingest",
            json={"text": f"Concurrent test signal #{i} — AI trend growing.", "platform": "twitter"},
            headers=headers,
        )

    responses = await asyncio.gather(*[ingest(i) for i in range(10)])
    statuses = [r.status_code for r in responses]
    failed = [s for s in statuses if s not in (200, 429)]
    assert not failed, f"Unexpected failures in concurrent test: {failed}"


# ── Security Header Tests ─────────────────────────────────────────


@pytest.mark.anyio
async def test_security_headers_present(client):
    """All OWASP security headers must be present."""
    resp = await client.get("/health")
    headers = resp.headers

    required = [
        "x-content-type-options",
        "x-frame-options",
        "x-xss-protection",
        "referrer-policy",
    ]
    missing = [h for h in required if h not in headers]
    assert not missing, f"Missing security headers: {missing}"


@pytest.mark.anyio
async def test_no_server_banner(client):
    """Server header should not expose version info."""
    resp = await client.get("/health")
    server = resp.headers.get("server", "")
    assert "uvicorn" not in server.lower() or server == "", (
        f"Server banner exposes info: {server}"
    )


@pytest.mark.anyio
async def test_auth_rejects_bad_token(client):
    """Requests with invalid JWT must return 401."""
    headers = {"Authorization": "Bearer this.is.not.a.valid.token"}
    resp = await client.get("/api/v1/signals/", headers=headers)
    assert resp.status_code in (401, 403)


@pytest.mark.anyio
async def test_auth_rejects_no_token(client):
    """Requests with no JWT must return 401 or 403."""
    resp = await client.get("/api/v1/signals/")
    assert resp.status_code in (401, 403)


@pytest.mark.anyio
async def test_input_validation_rejects_short_signal(client):
    """Signal text < 10 chars must be rejected."""
    token = await _get_token(client, "validation")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/signals/ingest",
        json={"text": "short", "platform": "twitter"},
        headers=headers,
    )
    assert resp.status_code == 422 or resp.status_code == 400
