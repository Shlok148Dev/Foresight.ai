"""
Foresight — Test Fixtures & Configuration
==========================================
Unit tests use SQLite in-memory (fast, isolated, no cloud dependency).
Integration tests use Supabase (marked with @pytest.mark.integration).

Architecture:
  - conftest overrides get_db to inject a test-local SQLite session
  - All SQLAlchemy ORM models work with SQLite for basic CRUD tests
  - Supabase-specific features are tested in integration tests only
"""

import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.database import Base, get_db
from app.main import app

# SQLite for fast, isolated unit tests (no Supabase connection needed)
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Provide a clean database session for each test."""
    async with TestSession() as session:
        yield session


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
