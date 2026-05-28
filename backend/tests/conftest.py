"""
Foresight — Test Fixtures & Configuration
==========================================
Unit tests use SQLite in-memory (fast, isolated, no cloud dependency).
Integration tests use Supabase (marked with @pytest.mark.integration).

Architecture:
  - Each test gets a fresh in-memory SQLite database (created + dropped per test)
  - No session-scoped event_loop override (deprecated in pytest-asyncio 0.24+)
  - Supabase-specific features are tested in integration tests only
"""

import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.database import Base, get_db
from app.main import app

# Use a fresh in-memory SQLite database per test to avoid table-drop race conditions
TEST_DB_URL = "sqlite+aiosqlite://"  # pure in-memory, new db per engine


@pytest_asyncio.fixture
async def db_session():
    """Provide a clean, isolated in-memory database session for each test."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSession() as session:
        yield session

    # Teardown
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    """HTTP test client with database session override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client):
    """Register a test user and return auth headers."""
    resp = await client.post("/api/v1/auth/register", json={
        "email": "test@foresight.ai",
        "username": "testuser",
        "password": "TestPass123!",
        "full_name": "Test User",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def supabase_client():
    """
    Provide a Supabase client for integration tests.
    Only available when SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        pytest.skip("Supabase credentials not configured — skipping integration test")

    from supabase import create_client
    client = create_client(url, key)
    yield client
