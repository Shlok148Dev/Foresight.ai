"""
Foresight — Database Connection & Session Management
=====================================================
Hybrid architecture:
  1. SQLAlchemy async engine → Supabase PostgreSQL (direct connection)
     Used for all ORM queries (models, relationships, complex joins)
  2. Supabase Python client → Supabase REST API
     Used for Supabase-specific features (Auth, Storage, Realtime, Edge Functions)

Connection: Uses Supabase's Supavisor connection pooler (port 6543)
for efficient connection management on the free tier.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, Optional
import os
import logging

logger = logging.getLogger("foresight.db")

# ── Configuration ────────────────────────────────────────────────

# Direct PostgreSQL connection via Supabase Supavisor pooler
# Project: fvrzkwfmtbfipnlrvlwq | Region: ap-northeast-1
# Format: postgresql+asyncpg://postgres.[project-id]:[password]@[region].pooler.supabase.com:6543/postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres.fvrzkwfmtbfipnlrvlwq:YOUR-PASSWORD@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres",
)

# Pool tuned for Supabase free tier (max 60 connections via pooler)
# - pool_size=5: conservative for free tier
# - max_overflow=5: burst up to 10 total
# - pool_pre_ping=True: validates connections (important for cloud DBs)
# - pool_recycle=300: recycle connections every 5 min (prevents Supavisor timeouts)
POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "5"))

engine = create_async_engine(
    DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Supabase Client (REST API) ──────────────────────────────────

_supabase_client = None


def get_supabase():
    """
    Get the Supabase Python client for REST API operations.
    Uses the service role key for full admin access from the backend.

    Usage:
        sb = get_supabase()
        result = sb.table("signals").select("*").execute()
        # or
        sb.auth.admin.list_users()
    """
    global _supabase_client

    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if url and key:
            try:
                from supabase import create_client, Client
                _supabase_client = create_client(url, key)
                logger.info("Supabase client initialized successfully")
            except ImportError:
                logger.warning("supabase-py not installed — Supabase REST client unavailable")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                return None
        else:
            logger.info("Supabase credentials not set — running in local-only mode")
            return None

    return _supabase_client


# ── Base Model ───────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# ── Dependency Injection ─────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.
    Automatically commits on success and rolls back on error.

    Usage:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Lifecycle ────────────────────────────────────────────────────

async def init_db() -> None:
    """
    Initialize the database connection and create tables if needed.
    For Supabase: tables are typically created via the SQL editor or migrations,
    but this still works for local development and testing.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database initialized (pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW})")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    # Initialize Supabase client (non-blocking, optional)
    get_supabase()


async def close_db() -> None:
    """Dispose engine. Called at application shutdown."""
    await engine.dispose()
    logger.info("Database connections closed")
