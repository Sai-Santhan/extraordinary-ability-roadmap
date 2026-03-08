from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.database import User

security = HTTPBearer()

SECRET_KEY = settings.nextauth_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "email": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def create_sse_token(user_id: str, profile_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=60)
    return jwt.encode(
        {"sub": user_id, "profile_id": profile_id, "purpose": "sse", "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_sse_token(token: str, profile_id: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("purpose") != "sse":
        raise ValueError("Invalid token purpose")
    if payload.get("profile_id") != profile_id:
        raise ValueError("Token not valid for this profile")
    return payload["sub"]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload["sub"]
    except (JWTError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
