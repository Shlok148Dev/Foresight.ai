"""
Foresight — Authentication Tests
Covers: register, login, token refresh, profile, edge cases
"""

import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "new@foresight.ai", "username": "newuser",
        "password": "SecureP@ss1", "full_name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {"email": "dup@foresight.ai", "username": "dup1", "password": "SecureP@ss1"}
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json={
        **payload, "username": "dup2"
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    await client.post("/api/v1/auth/register", json={
        "email": "a@foresight.ai", "username": "samename", "password": "SecureP@ss1"
    })
    resp = await client.post("/api/v1/auth/register", json={
        "email": "b@foresight.ai", "username": "samename", "password": "SecureP@ss1"
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "weak@foresight.ai", "username": "weakuser", "password": "short"
    })
    assert resp.status_code == 422  # Pydantic validation


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "not-an-email", "username": "badmail", "password": "SecureP@ss1"
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login@foresight.ai", "username": "loginuser", "password": "SecureP@ss1"
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "login@foresight.ai", "password": "SecureP@ss1"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@foresight.ai", "username": "wrongpw", "password": "SecureP@ss1"
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "wrong@foresight.ai", "password": "WrongPassword"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "noone@foresight.ai", "password": "Whatever123"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_profile(client, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@foresight.ai"
    assert data["username"] == "testuser"
    assert data["role"] == "free"


@pytest.mark.asyncio
async def test_profile_no_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 403  # No bearer token


@pytest.mark.asyncio
async def test_profile_invalid_token(client):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_flow(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "refresh@foresight.ai", "username": "refreshuser", "password": "SecureP@ss1"
    })
    refresh = reg.json()["refresh_token"]
    resp = await client.post(f"/api/v1/auth/refresh?refresh_token={refresh}")
    assert resp.status_code == 200
    assert "access_token" in resp.json()
