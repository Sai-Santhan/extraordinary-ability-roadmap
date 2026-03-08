from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.limiter import limiter
from app.models.database import User
from app.models.schemas import UserCreate, UserLogin, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=data.email, hashed_password=hash_password(data.password), name=data.name)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(str(user.id), user.email)
    return TokenResponse(
        access_token=token, user_id=str(user.id), name=user.name,
        onboarding_completed=user.onboarding_completed or False,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(str(user.id), user.email)
    return TokenResponse(
        access_token=token, user_id=str(user.id), name=user.name,
        onboarding_completed=user.onboarding_completed or False,
    )
