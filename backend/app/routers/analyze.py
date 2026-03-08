import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.auth import decode_token
from app.database import get_db
from app.models.database import ImmigrationProfileDB, User
from app.agents.pipeline import run_pipeline

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.get("/stream/{profile_id}")
async def stream_analysis(
    profile_id: str,
    token: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    # SSE endpoints can't use Authorization headers from EventSource,
    # so we accept the token as a query parameter
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    try:
        payload = decode_token(token)
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

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
