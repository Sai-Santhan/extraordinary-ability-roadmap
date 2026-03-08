from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.database import ImmigrationProfileDB, User

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.post("/")
async def create_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = ImmigrationProfileDB(user_id=user.id, status="created")
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return {"id": str(profile.id), "status": profile.status}


@router.get("/")
async def list_profiles(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImmigrationProfileDB).where(ImmigrationProfileDB.user_id == user.id)
    )
    profiles = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "status": p.status,
            "profile_data": p.profile_data,
            "assessment_data": p.assessment_data,
            "roadmap_data": p.roadmap_data,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in profiles
    ]


@router.get("/{profile_id}")
async def get_profile(
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImmigrationProfileDB).where(
            ImmigrationProfileDB.id == profile_id,
            ImmigrationProfileDB.user_id == user.id,
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "id": str(profile.id),
        "status": profile.status,
        "profile_data": profile.profile_data,
        "assessment_data": profile.assessment_data,
        "roadmap_data": profile.roadmap_data,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImmigrationProfileDB).where(
            ImmigrationProfileDB.id == profile_id,
            ImmigrationProfileDB.user_id == user.id,
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    await db.delete(profile)
    await db.commit()
    return {"status": "deleted"}
