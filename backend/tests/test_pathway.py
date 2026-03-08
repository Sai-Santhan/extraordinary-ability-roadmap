"""Tests for pathway switching and rate limiting."""

import pytest

from tests.conftest import auth_headers


@pytest.fixture
async def auth_and_profile(client):
    """Register user, complete onboarding, return (token, profile_id)."""
    r = await client.post("/api/auth/register", json={
        "email": "pathway@test.com", "password": "pass1234", "name": "Pathway User",
    })
    token = r.json()["access_token"]
    headers = auth_headers(token)

    r = await client.post("/api/onboarding/", headers=headers, json={
        "role_type": "researcher",
        "primary_field": "ML",
        "years_experience": 5,
        "qualifications": ["publications"],
        "current_visa": "h1b",
    })
    profile_id = r.json()["profile_id"]
    return token, profile_id


@pytest.mark.asyncio
async def test_switch_pathway(client, auth_and_profile):
    token, profile_id = auth_and_profile
    r = await client.patch(
        f"/api/profiles/{profile_id}/pathway",
        headers=auth_headers(token),
        json={"pathway": "eb1a"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["target_pathway"] == "eb1a"
    assert data["pathway_changed_since_analysis"] is True


@pytest.mark.asyncio
async def test_switch_pathway_rate_limit(client, auth_and_profile):
    token, profile_id = auth_and_profile

    r1 = await client.patch(
        f"/api/profiles/{profile_id}/pathway",
        headers=auth_headers(token),
        json={"pathway": "eb1a"},
    )
    assert r1.status_code == 200

    r2 = await client.patch(
        f"/api/profiles/{profile_id}/pathway",
        headers=auth_headers(token),
        json={"pathway": "niw"},
    )
    assert r2.status_code == 429


@pytest.mark.asyncio
async def test_switch_pathway_invalid(client, auth_and_profile):
    token, profile_id = auth_and_profile
    r = await client.patch(
        f"/api/profiles/{profile_id}/pathway",
        headers=auth_headers(token),
        json={"pathway": "invalid_visa"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_switch_pathway_unauthorized(client, auth_and_profile):
    _, profile_id = auth_and_profile
    r = await client.patch(
        f"/api/profiles/{profile_id}/pathway",
        json={"pathway": "eb1a"},
    )
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_profile_shows_pathway(client, auth_and_profile):
    token, profile_id = auth_and_profile
    r = await client.get(f"/api/profiles/{profile_id}", headers=auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert "target_pathway" in data
    assert "pathway_changed_since_analysis" in data
