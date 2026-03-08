"""Shared test fixtures for all test modules."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.models.database import User  # noqa: F401 — ensure models registered

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


from app.main import app  # noqa: E402

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Reset rate limiter storage between tests
    from app.limiter import limiter
    try:
        limiter.reset()
    except Exception:
        if hasattr(limiter, "_storage") and hasattr(limiter._storage, "reset"):
            limiter._storage.reset()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_token(client):
    """Register a user and return the JWT token."""
    r = await client.post("/api/auth/register", json={
        "email": "test@test.com", "password": "pass1234", "name": "Test User",
    })
    assert r.status_code == 201, f"Registration failed: {r.text}"
    return r.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
