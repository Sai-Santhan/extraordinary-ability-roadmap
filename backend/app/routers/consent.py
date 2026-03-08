from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.database import DataConsent, User
from app.models.schemas import ConsentRequest

router = APIRouter(prefix="/api/consent", tags=["consent"])


@router.post("/")
async def give_consent(
    data: ConsentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    consent = DataConsent(
        user_id=user.id,
        source_type=data.source_type,
        consent_given=data.consent_given,
        consent_timestamp=datetime.now(timezone.utc) if data.consent_given else None,
        processing_description=data.processing_description,
    )
    db.add(consent)
    await db.commit()
    return {"status": "consent recorded", "source_type": data.source_type}


@router.get("/")
async def list_consents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DataConsent).where(DataConsent.user_id == user.id, DataConsent.revoked_at.is_(None))
    )
    consents = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "source_type": c.source_type,
            "consent_given": c.consent_given,
            "consent_timestamp": c.consent_timestamp.isoformat() if c.consent_timestamp else None,
            "processing_description": c.processing_description,
        }
        for c in consents
    ]


@router.delete("/{source_type}")
async def revoke_consent(
    source_type: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DataConsent).where(
            DataConsent.user_id == user.id,
            DataConsent.source_type == source_type,
            DataConsent.revoked_at.is_(None),
        )
    )
    consent = result.scalar_one_or_none()
    if not consent:
        raise HTTPException(status_code=404, detail="No active consent found")
    consent.revoked_at = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "consent revoked"}
