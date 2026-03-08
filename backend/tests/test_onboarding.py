import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_onboarding_status_initial(client, auth_token):
    r = await client.get("/api/onboarding/", headers=auth_headers(auth_token))
    assert r.status_code == 200
    data = r.json()
    assert data["completed"] is False
    assert data["recommended_pathway"] is None


@pytest.mark.asyncio
async def test_complete_onboarding(client, auth_token):
    r = await client.post("/api/onboarding/", headers=auth_headers(auth_token), json={
        "role_type": "researcher",
        "primary_field": "Machine Learning",
        "years_experience": 8,
        "qualifications": ["publications", "awards"],
        "current_visa": "h1b",
    })
    assert r.status_code == 201
    data = r.json()
    assert "recommended_pathway" in data
    assert "recommendations" in data
    assert "profile_id" in data
    assert len(data["recommendations"]) == 5
    # With publications + awards, eb1a should score highest
    assert data["recommended_pathway"] in ["eb1a", "o1"]


@pytest.mark.asyncio
async def test_onboarding_eb1c_recommendation(client, auth_token):
    r = await client.post("/api/onboarding/", headers=auth_headers(auth_token), json={
        "role_type": "executive",
        "primary_field": "Finance",
        "years_experience": 15,
        "qualifications": ["multinational", "managerial"],
        "current_visa": "l1",
    })
    assert r.status_code == 201
    assert r.json()["recommended_pathway"] == "eb1c"


@pytest.mark.asyncio
async def test_onboarding_eb1b_recommendation(client, auth_token):
    r = await client.post("/api/onboarding/", headers=auth_headers(auth_token), json={
        "role_type": "researcher",
        "primary_field": "Biology",
        "years_experience": 5,
        "qualifications": ["publications", "job_offer"],
        "current_visa": "f1",
    })
    assert r.status_code == 201
    assert r.json()["recommended_pathway"] == "eb1b"


@pytest.mark.asyncio
async def test_onboarding_status_after_completion(client, auth_token):
    await client.post("/api/onboarding/", headers=auth_headers(auth_token), json={
        "role_type": "researcher",
        "primary_field": "ML",
        "years_experience": 5,
        "qualifications": ["publications"],
        "current_visa": "h1b",
    })
    r = await client.get("/api/onboarding/", headers=auth_headers(auth_token))
    assert r.status_code == 200
    data = r.json()
    assert data["completed"] is True
    assert data["recommended_pathway"] is not None
