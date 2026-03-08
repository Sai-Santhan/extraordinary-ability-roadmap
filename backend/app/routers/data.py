import os

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.database import EvidenceFile, ImmigrationProfileDB, User

router = APIRouter(prefix="/api/data", tags=["data"])


@router.delete("/me")
async def delete_all_user_data(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Delete uploaded files from disk
    profiles_result = await db.execute(
        select(ImmigrationProfileDB).where(ImmigrationProfileDB.user_id == user.id)
    )
    profiles = profiles_result.scalars().all()

    for profile in profiles:
        evidence_result = await db.execute(
            select(EvidenceFile).where(EvidenceFile.profile_id == profile.id)
        )
        for ef in evidence_result.scalars().all():
            if ef.file_path and os.path.exists(ef.file_path):
                os.remove(ef.file_path)

    # Delete user (cascades to profiles, evidence, consents)
    await db.delete(user)
    await db.commit()

    return {"status": "all data deleted", "message": "Your account and all associated data have been permanently removed."}
