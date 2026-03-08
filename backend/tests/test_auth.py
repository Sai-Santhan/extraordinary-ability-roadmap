import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_register(client):
    r = await client.post("/api/auth/register", json={"email": "new@test.com", "password": "pass1234", "name": "Test User"})
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    assert data["name"] == "Test User"


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/api/auth/register", json={"email": "login@test.com", "password": "pass1234", "name": "Test User"})
    r = await client.post("/api/auth/login", json={"email": "login@test.com", "password": "pass1234"})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={"email": "wrong@test.com", "password": "pass1234", "name": "Test User"})
    r = await client.post("/api/auth/login", json={"email": "wrong@test.com", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_duplicate_register(client):
    await client.post("/api/auth/register", json={"email": "dup@test.com", "password": "pass1234", "name": "Test User"})
    r = await client.post("/api/auth/register", json={"email": "dup@test.com", "password": "pass4567", "name": "Another"})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_register_returns_onboarding_status(client):
    r = await client.post("/api/auth/register", json={"email": "onb@test.com", "password": "pass1234", "name": "Test"})
    assert r.status_code == 201
    data = r.json()
    assert "onboarding_completed" in data
    assert data["onboarding_completed"] is False


@pytest.mark.asyncio
async def test_login_returns_onboarding_status(client):
    await client.post("/api/auth/register", json={"email": "onb2@test.com", "password": "pass1234", "name": "Test"})
    r = await client.post("/api/auth/login", json={"email": "onb2@test.com", "password": "pass1234"})
    assert r.status_code == 200
    assert "onboarding_completed" in r.json()
