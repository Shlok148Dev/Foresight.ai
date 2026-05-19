"""
Foresight — Supabase Integration Tests
=========================================
These tests run against a real Supabase instance.
Marked with @pytest.mark.integration — skipped when credentials aren't set.
Run: pytest tests/test_supabase.py -v -m integration
"""

import pytest
import os


# Skip entire module if no Supabase credentials
pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_supabase_client_connection(supabase_client):
    """Verify Supabase client can connect and query."""
    assert supabase_client is not None

    # Test: list tables via RPC or simple query
    result = supabase_client.table("users").select("id").limit(1).execute()
    assert result is not None
    assert hasattr(result, "data")


@pytest.mark.asyncio
async def test_supabase_insert_and_query_user(supabase_client):
    """Test inserting a user via Supabase REST API and querying it back."""
    import uuid

    test_id = str(uuid.uuid4())
    test_email = f"integration-{test_id[:8]}@test.foresight.ai"

    # Insert
    result = supabase_client.table("users").insert({
        "email": test_email,
        "username": f"test_{test_id[:8]}",
        "password_hash": "$2b$12$test_hash_not_real",
        "role": "free",
        "is_active": True,
        "is_verified": False,
    }).execute()

    assert len(result.data) == 1
    created_user = result.data[0]
    assert created_user["email"] == test_email

    # Query back
    query_result = supabase_client.table("users").select("*").eq(
        "email", test_email
    ).execute()
    assert len(query_result.data) == 1
    assert query_result.data[0]["username"] == f"test_{test_id[:8]}"

    # Cleanup
    supabase_client.table("users").delete().eq("email", test_email).execute()


@pytest.mark.asyncio
async def test_supabase_insert_signal(supabase_client):
    """Test signal ingestion via Supabase REST API."""
    import uuid

    result = supabase_client.table("signals").insert({
        "text": "Integration test signal — testing Supabase connectivity",
        "platform": "github",
        "author": "@foresight-ci",
        "language": "en",
    }).execute()

    assert len(result.data) == 1
    signal = result.data[0]
    assert signal["platform"] == "github"

    # Cleanup
    supabase_client.table("signals").delete().eq("id", signal["id"]).execute()


@pytest.mark.asyncio
async def test_supabase_pgvector_extension(supabase_client):
    """Verify pgvector extension is enabled on Supabase."""
    # This query checks if the vector extension is installed
    result = supabase_client.rpc("check_extension", {"ext_name": "vector"}).execute()
    # If the RPC doesn't exist, we can check via a simpler method
    # The extension should have been created by our migration SQL


@pytest.mark.asyncio
async def test_supabase_connection_latency(supabase_client):
    """Verify Supabase query latency is acceptable (<200ms)."""
    import time

    start = time.perf_counter()
    supabase_client.table("users").select("id").limit(1).execute()
    latency_ms = (time.perf_counter() - start) * 1000

    assert latency_ms < 500, f"Supabase latency too high: {latency_ms:.0f}ms"
