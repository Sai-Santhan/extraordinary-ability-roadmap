import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.auth import create_sse_token, decode_sse_token, get_current_user
from app.database import get_db
from app.models.database import ImmigrationProfileDB, User
from app.agents.pipeline import run_pipeline

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("/token/{profile_id}")
async def get_sse_token(
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

    # Rate limit: 1 analysis per week
    now = datetime.now(timezone.utc)
    if profile.last_analysis_run:
        last_run = profile.last_analysis_run
        if last_run.tzinfo is None:
            last_run = last_run.replace(tzinfo=timezone.utc)
        time_since = now - last_run
        if time_since < timedelta(days=7):
            retry_after = last_run + timedelta(days=7)
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "You can only run analysis once per week",
                    "retry_after": retry_after.isoformat(),
                    "limit_type": "analysis",
                },
            )

    # Mark analysis start time and clear pathway changed flag
    profile.last_analysis_run = now
    profile.pathway_changed_since_analysis = False
    await db.commit()

    token = create_sse_token(str(user.id), profile_id)
    return {"sse_token": token}


@router.get("/stream/{profile_id}")
async def stream_analysis(
    profile_id: str,
    token: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    try:
        user_id = decode_sse_token(token, profile_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    result = await db.execute(
        select(ImmigrationProfileDB).where(
            ImmigrationProfileDB.id == profile_id,
            ImmigrationProfileDB.user_id == user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Profile not found")

    async def event_generator():
        async for event in run_pipeline(profile_id, db):
            yield {
                "event": event.get("event", "message"),
                "data": json.dumps(event.get("data", {})),
            }

    return EventSourceResponse(event_generator())
