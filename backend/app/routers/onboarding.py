from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.database import ImmigrationProfileDB, User
from app.models.schemas import (
    OnboardingRequest,
    OnboardingResponse,
    PathwayRecommendation,
)

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


def compute_pathway_scores(data: OnboardingRequest) -> list[PathwayRecommendation]:
    qualifications = set(data.qualifications)
    scores = {
        "eb1a": 20,
        "eb1b": 20,
        "eb1c": 20,
        "niw": 20,
        "o1": 30,
    }

    if data.role_type == "executive" and "multinational" in qualifications:
        scores["eb1c"] += 50
    if data.role_type == "researcher" and "job_offer" in qualifications:
        scores["eb1b"] += 50
    if "publications" in qualifications and "awards" in qualifications:
        scores["eb1a"] += 50
    if "publications" in qualifications and "awards" not in qualifications:
        scores["niw"] += 40

    if "publications" in qualifications:
        scores["eb1a"] += 10
        scores["niw"] += 10
    if "awards" in qualifications:
        scores["eb1a"] += 10
        scores["o1"] += 15
    if "managerial" in qualifications:
        scores["eb1c"] += 15
    if "job_offer" in qualifications:
        scores["eb1b"] += 10
    if data.years_experience >= 10:
        scores["eb1a"] += 10
        scores["eb1c"] += 10

    explanations = {
        "eb1a": "Extraordinary ability pathway for individuals with sustained acclaim",
        "eb1b": "Outstanding researcher/professor pathway requiring a permanent job offer",
        "eb1c": "Multinational manager/executive transfer pathway",
        "niw": "National Interest Waiver for advanced-degree professionals",
        "o1": "Extraordinary ability non-immigrant visa for temporary work",
    }

    recommendations = []
    for pathway, score in scores.items():
        capped_score = min(score, 100)
        recommendations.append(
            PathwayRecommendation(
                recommended=pathway,
                match_score=capped_score,
                explanation=explanations[pathway],
            )
        )

    recommendations.sort(key=lambda r: r.match_score, reverse=True)
    return recommendations


@router.get("/")
async def get_onboarding_status(
    user: User = Depends(get_current_user),
):
    recommended_pathway = None
    if user.onboarding_data and isinstance(user.onboarding_data, dict):
        recommended_pathway = user.onboarding_data.get("recommended_pathway")

    return {
        "completed": user.onboarding_completed,
        "data": user.onboarding_data,
        "recommended_pathway": recommended_pathway,
    }


@router.post("/", response_model=OnboardingResponse, status_code=201)
async def complete_onboarding(
    data: OnboardingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recommendations = compute_pathway_scores(data)
    recommended_pathway = recommendations[0].recommended

    user.onboarding_data = {
        **data.model_dump(),
        "recommended_pathway": recommended_pathway,
    }
    user.onboarding_completed = True

    profile = ImmigrationProfileDB(
        user_id=user.id,
        status="created",
        target_pathway=recommended_pathway,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return OnboardingResponse(
        recommended_pathway=recommended_pathway,
        recommendations=recommendations,
        profile_id=str(profile.id),
    )
