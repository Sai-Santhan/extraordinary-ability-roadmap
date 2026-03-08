import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.models.database import User  # noqa: F401 — ensure models are registered on Base

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


# Import app after setting up overrides
from app.main import app  # noqa: E402

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_register(client):
    r = await client.post("/api/auth/register", json={"email": "test@test.com", "password": "pass123", "name": "Test User"})
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    assert data["name"] == "Test User"


@pytest.mark.asyncio
async def test_login(client):
    # Register first
    await client.post("/api/auth/register", json={"email": "test@test.com", "password": "pass123", "name": "Test User"})
    # Login
    r = await client.post("/api/auth/login", json={"email": "test@test.com", "password": "pass123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={"email": "test@test.com", "password": "pass123", "name": "Test User"})
    r = await client.post("/api/auth/login", json={"email": "test@test.com", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_duplicate_register(client):
    await client.post("/api/auth/register", json={"email": "test@test.com", "password": "pass123", "name": "Test User"})
    r = await client.post("/api/auth/register", json={"email": "test@test.com", "password": "pass456", "name": "Another"})
    assert r.status_code == 400
