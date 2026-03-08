# Immigration Roadmap Tool — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a full-stack AI-powered immigration roadmap tool that ingests career data, scores it against EB-1A/NIW/O-1 criteria, and generates personalized roadmaps.

**Architecture:** Monorepo with `frontend/` (Next.js 16, pnpm), `backend/` (FastAPI, uv), `shared/` (JSON schemas + TS types). PostgreSQL via Docker. 4-agent Claude pipeline with SSE streaming. NextAuth.js v5 credentials auth with explicit data consent.

**Tech Stack:** Next.js 16.1.6, shadcn/ui, Tailwind, React Query, Zustand, NextStepJS, Recharts, FastAPI, Pydantic v2, SQLAlchemy async, PostgreSQL, Claude Sonnet 4.5 Structured Outputs, Prisma

---

## Task 1: Docker + PostgreSQL Setup

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: Create docker-compose.yml**

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: immigration
      POSTGRES_PASSWORD: immigration_dev
      POSTGRES_DB: immigration_roadmap
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

**Step 2: Create .env.example**

```env
# Database
DATABASE_URL=postgresql+asyncpg://immigration:immigration_dev@localhost:5432/immigration_roadmap
DATABASE_URL_PRISMA=postgresql://immigration:immigration_dev@localhost:5432/immigration_roadmap

# Auth
NEXTAUTH_SECRET=change-me-in-production
NEXTAUTH_URL=http://localhost:3000

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Backend
BACKEND_URL=http://localhost:8000
```

**Step 3: Create .gitignore**

```
node_modules/
.next/
__pycache__/
*.pyc
.env
.venv/
*.egg-info/
dist/
.DS_Store
```

**Step 4: Start PostgreSQL and verify**

Run: `docker-compose up -d && sleep 2 && docker-compose ps`
Expected: db service running on port 5432

**Step 5: Commit**

```bash
git add docker-compose.yml .env.example .gitignore
git commit -m "feat: add Docker Compose with PostgreSQL and project config"
```

---

## Task 2: Backend Scaffold — FastAPI + SQLAlchemy + Pydantic Models

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/database.py` (SQLAlchemy ORM models)
- Create: `backend/app/models/schemas.py` (Pydantic schemas — the core data models from README)

**Step 1: Create pyproject.toml**

```toml
[project]
name = "immigration-roadmap-backend"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
    "fastapi[standard]>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "anthropic>=0.52.0",
    "pymupdf>=1.25.0",
    "python-multipart>=0.0.20",
    "python-docx>=1.1.0",
    "sse-starlette>=2.0.0",
    "passlib[bcrypt]>=1.7.4",
    "python-jose[cryptography]>=3.3.0",
    "reportlab>=4.0.0",
    "alembic>=1.15.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2: Create app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://immigration:immigration_dev@localhost:5432/immigration_roadmap"
    anthropic_api_key: str = ""
    nextauth_secret: str = "change-me"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    model_config = {"env_file": "../.env"}


settings = Settings()
```

**Step 3: Create app/database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

**Step 4: Create app/models/database.py — SQLAlchemy ORM models**

```python
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, Boolean, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profiles = relationship("ImmigrationProfileDB", back_populates="user", cascade="all, delete-orphan")
    consents = relationship("DataConsent", back_populates="user", cascade="all, delete-orphan")


class DataConsent(Base):
    __tablename__ = "data_consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String(50), nullable=False)  # "cv", "scholar", "github", etc.
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime, nullable=True)
    processing_description = Column(Text, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="consents")


class ImmigrationProfileDB(Base):
    __tablename__ = "immigration_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    profile_data = Column(JSON, nullable=True)  # Full ImmigrationProfile as JSON
    raw_career_data = Column(JSON, nullable=True)  # RawCareerData as JSON
    assessment_data = Column(JSON, nullable=True)  # CriteriaAssessment as JSON
    roadmap_data = Column(JSON, nullable=True)  # ImmigrationRoadmap as JSON
    status = Column(String(50), default="created")  # created, ingesting, extracting, assessing, roadmapping, complete
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profiles")
    evidence_files = relationship("EvidenceFile", back_populates="profile", cascade="all, delete-orphan")


class EvidenceFile(Base):
    __tablename__ = "evidence_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("immigration_profiles.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, mbox, ics, json, docx
    source_type = Column(String(50), nullable=False)  # cv, gmail, calendar, chatgpt, linkedin, scholar, github
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("ImmigrationProfileDB", back_populates="evidence_files")
```

**Step 5: Create app/models/schemas.py — Pydantic schemas (from README spec)**

This is the full set of Pydantic models: `ImmigrationProfile`, `CriteriaAssessment`, `ImmigrationRoadmap`, `RawCareerData`, plus request/response schemas for the API.

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import date, datetime


# --- Enums ---

class ImmigrationTarget(str, Enum):
    EB1A = "eb1a"
    NIW = "niw"
    O1 = "o1"


class EvidenceSource(str, Enum):
    CV = "cv"
    SCHOLAR = "scholar"
    GITHUB = "github"
    GMAIL = "gmail"
    LINKEDIN = "linkedin"
    CHATGPT_EXPORT = "chatgpt_export"
    CALENDAR = "calendar"
    MANUAL = "manual"


# --- Confidence ---

class ConfidenceLevel(BaseModel):
    data_confidence: int = Field(ge=0, le=100)
    criteria_match: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)
    reasoning: str


# --- Evidence Items ---

class Publication(BaseModel):
    title: str
    venue: str
    year: int
    citation_count: Optional[int] = None
    co_authors: list[str] = []
    doi: Optional[str] = None
    source: EvidenceSource
    confidence: ConfidenceLevel


class Award(BaseModel):
    name: str
    granting_organization: str
    year: int
    scope: str
    description: Optional[str] = None
    source: EvidenceSource
    confidence: ConfidenceLevel


class JudgingRole(BaseModel):
    role: str
    organization: str
    year: int
    documented: bool
    source: EvidenceSource
    confidence: ConfidenceLevel


class MediaCoverage(BaseModel):
    title: str
    outlet: str
    date: Optional[date] = None
    url: Optional[str] = None
    about_person: bool
    source: EvidenceSource
    confidence: ConfidenceLevel


class LeadershipRole(BaseModel):
    title: str
    organization: str
    start_date: date
    end_date: Optional[date] = None
    is_distinguished_org: bool
    source: EvidenceSource
    confidence: ConfidenceLevel


# --- Core Profile ---

class ImmigrationProfile(BaseModel):
    name: str
    current_visa_status: Optional[str] = None
    country_of_birth: Optional[str] = None
    target_pathway: ImmigrationTarget
    target_timeline_years: int = Field(ge=1, le=10)
    current_role: Optional[str] = None
    current_employer: Optional[str] = None
    years_experience: Optional[int] = None
    field_of_expertise: str
    publications: list[Publication] = []
    awards: list[Award] = []
    judging_roles: list[JudgingRole] = []
    media_coverage: list[MediaCoverage] = []
    leadership_roles: list[LeadershipRole] = []
    h_index: Optional[int] = None
    total_citations: Optional[int] = None
    i10_index: Optional[int] = None
    github_stars: Optional[int] = None
    github_contributions_last_year: Optional[int] = None
    github_pr_reviews: Optional[int] = None
    notable_repos: list[str] = []
    selective_memberships: list[str] = []
    compensation_percentile: Optional[str] = None
    data_sources: list[EvidenceSource] = []


# --- Assessment ---

class CriterionScore(BaseModel):
    criterion_number: int
    criterion_name: str
    evidence_found: list[str]
    strength: str  # "strong", "moderate", "weak", "none"
    confidence: ConfidenceLevel
    gaps: list[str]
    priority_actions: list[str]


class CriteriaAssessment(BaseModel):
    pathway: ImmigrationTarget
    criteria_scores: list[CriterionScore]
    criteria_met_count: int
    criteria_close_count: int
    overall_readiness: str
    strongest_criteria: list[int]
    weakest_criteria: list[int]
    recommended_focus: list[int]


# --- Roadmap ---

class RoadmapAction(BaseModel):
    action: str
    description: str
    target_criterion: list[int]
    quarter: str
    effort_level: str
    impact_level: str
    specific_opportunities: list[str] = []


class QuarterlyMilestone(BaseModel):
    quarter: str
    actions: list[RoadmapAction]
    expected_criteria_improvement: dict[int, str]


class ImmigrationRoadmap(BaseModel):
    profile_id: str
    pathway: ImmigrationTarget
    timeline_years: int
    milestones: list[QuarterlyMilestone]
    narrative_summary: str
    disclaimer: str = "This is not legal advice. Consult a qualified immigration attorney."


# --- Raw Career Data (Ingestion output) ---

class RawSourceData(BaseModel):
    source: EvidenceSource
    raw_text: str
    file_name: Optional[str] = None
    metadata: dict = {}


class RawCareerData(BaseModel):
    sources: list[RawSourceData]
    total_files_processed: int
    extraction_notes: list[str] = []


# --- API Request/Response ---

class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str


class ConsentRequest(BaseModel):
    source_type: str
    consent_given: bool
    processing_description: str


class ProfileResponse(BaseModel):
    id: str
    status: str
    profile_data: Optional[ImmigrationProfile] = None
    assessment_data: Optional[CriteriaAssessment] = None
    roadmap_data: Optional[ImmigrationRoadmap] = None
    created_at: datetime
    updated_at: datetime
```

**Step 6: Create app/main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Immigration Roadmap API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

**Step 7: Install dependencies and verify server starts**

Run: `cd backend && uv sync && uv run uvicorn app.main:app --port 8000 &` then `curl http://localhost:8000/api/health`
Expected: `{"status":"ok"}`

**Step 8: Commit**

```bash
git add backend/
git commit -m "feat: scaffold FastAPI backend with SQLAlchemy models and Pydantic schemas"
```

---

## Task 3: Backend Auth — Registration, Login, JWT

**Files:**
- Create: `backend/app/auth.py`
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/auth.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_auth.py`

**Step 1: Create app/auth.py — password hashing + JWT utilities**

```python
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.nextauth_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "email": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

**Step 2: Create app/routers/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.database import User
from app.models.schemas import UserCreate, UserLogin, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=data.email, hashed_password=hash_password(data.password), name=data.name)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(str(user.id), user.email)
    return TokenResponse(access_token=token, user_id=str(user.id), name=user.name)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(str(user.id), user.email)
    return TokenResponse(access_token=token, user_id=str(user.id), name=user.name)
```

**Step 3: Create middleware for auth dependency**

Add to `app/auth.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.database import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

**Step 4: Register router in main.py**

Add to `app/main.py`:
```python
from app.routers.auth import router as auth_router
app.include_router(auth_router)
```

**Step 5: Write test**

```python
# backend/tests/test_auth.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_register_and_login(client):
    # Register
    r = await client.post("/api/auth/register", json={"email": "test@test.com", "password": "pass123", "name": "Test"})
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data

    # Login
    r = await client.post("/api/auth/login", json={"email": "test@test.com", "password": "pass123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
```

**Step 6: Run test**

Run: `cd backend && uv run pytest tests/test_auth.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat: add auth endpoints with JWT, password hashing, and tests"
```

---

## Task 4: Backend — File Upload, Consent, and Parsers

**Files:**
- Create: `backend/app/routers/evidence.py`
- Create: `backend/app/routers/consent.py`
- Create: `backend/app/parsers/__init__.py`
- Create: `backend/app/parsers/pdf_parser.py`
- Create: `backend/app/parsers/mbox_parser.py`
- Create: `backend/app/parsers/ics_parser.py`
- Create: `backend/app/parsers/json_parser.py`
- Create: `backend/app/parsers/linkedin_parser.py`
- Create: `backend/app/parsers/router.py` (dispatches to correct parser by file type)

**Step 1: Create consent router**

```python
# backend/app/routers/consent.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.auth import get_current_user
from app.database import get_db
from app.models.database import User, DataConsent
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
```

**Step 2: Create parsers**

Each parser takes a file path and returns extracted text + metadata.

```python
# backend/app/parsers/pdf_parser.py
import pymupdf

def parse_pdf(file_path: str) -> dict:
    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return {"text": text, "pages": len(doc), "type": "pdf"}
```

```python
# backend/app/parsers/mbox_parser.py
import mailbox
import email.utils

def parse_mbox(file_path: str) -> dict:
    mbox = mailbox.mbox(file_path)
    emails = []
    for message in mbox:
        emails.append({
            "subject": message.get("subject", ""),
            "from": message.get("from", ""),
            "to": message.get("to", ""),
            "date": message.get("date", ""),
            "body": _get_body(message),
        })
    return {"emails": emails, "count": len(emails), "type": "mbox"}

def _get_body(message) -> str:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode("utf-8", errors="replace")
    else:
        payload = message.get_payload(decode=True)
        if payload:
            return payload.decode("utf-8", errors="replace")
    return ""
```

```python
# backend/app/parsers/ics_parser.py
import re

def parse_ics(file_path: str) -> dict:
    with open(file_path, "r") as f:
        content = f.read()
    events = []
    for block in content.split("BEGIN:VEVENT"):
        if "END:VEVENT" not in block:
            continue
        event = {}
        for line in block.split("\n"):
            if line.startswith("SUMMARY:"):
                event["summary"] = line[8:].strip()
            elif line.startswith("DTSTART"):
                event["start"] = line.split(":")[-1].strip()
            elif line.startswith("DTEND"):
                event["end"] = line.split(":")[-1].strip()
            elif line.startswith("DESCRIPTION:"):
                event["description"] = line[12:].strip()
            elif line.startswith("LOCATION:"):
                event["location"] = line[9:].strip()
        if event:
            events.append(event)
    return {"events": events, "count": len(events), "type": "ics"}
```

```python
# backend/app/parsers/json_parser.py
import json

def parse_chatgpt_export(file_path: str) -> dict:
    with open(file_path, "r") as f:
        data = json.load(f)
    conversations = []
    for conv in data if isinstance(data, list) else [data]:
        title = conv.get("title", "Untitled")
        messages = []
        mapping = conv.get("mapping", {})
        for node in mapping.values():
            msg = node.get("message")
            if msg and msg.get("content", {}).get("parts"):
                messages.append({
                    "role": msg.get("author", {}).get("role", "unknown"),
                    "text": " ".join(str(p) for p in msg["content"]["parts"]),
                })
        conversations.append({"title": title, "messages": messages})
    return {"conversations": conversations, "count": len(conversations), "type": "chatgpt"}


def parse_google_takeout_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        data = json.load(f)
    return {"data": data, "type": "google_takeout"}
```

```python
# backend/app/parsers/linkedin_parser.py
import pymupdf

def parse_linkedin_pdf(file_path: str) -> dict:
    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return {"text": text, "type": "linkedin_pdf"}
```

```python
# backend/app/parsers/router.py
from app.parsers.pdf_parser import parse_pdf
from app.parsers.mbox_parser import parse_mbox
from app.parsers.ics_parser import parse_ics
from app.parsers.json_parser import parse_chatgpt_export, parse_google_takeout_json
from app.parsers.linkedin_parser import parse_linkedin_pdf

PARSER_MAP = {
    ("pdf", "cv"): parse_pdf,
    ("pdf", "linkedin"): parse_linkedin_pdf,
    ("mbox", "gmail"): parse_mbox,
    ("ics", "calendar"): parse_ics,
    ("json", "chatgpt_export"): parse_chatgpt_export,
    ("json", "google_takeout"): parse_google_takeout_json,
}


def route_parser(file_type: str, source_type: str, file_path: str) -> dict:
    parser = PARSER_MAP.get((file_type, source_type))
    if not parser:
        # Fallback: try by file type alone
        for (ft, _), p in PARSER_MAP.items():
            if ft == file_type:
                parser = p
                break
    if not parser:
        raise ValueError(f"No parser for file_type={file_type}, source_type={source_type}")
    return parser(file_path)
```

**Step 3: Create evidence upload router**

```python
# backend/app/routers/evidence.py
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.database import User, DataConsent, ImmigrationProfileDB, EvidenceFile
from app.parsers.router import route_parser

router = APIRouter(prefix="/api/evidence", tags=["evidence"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    profile_id: str = Form(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify consent exists for this source type
    consent_result = await db.execute(
        select(DataConsent).where(
            DataConsent.user_id == user.id,
            DataConsent.source_type == source_type,
            DataConsent.consent_given == True,
            DataConsent.revoked_at.is_(None),
        )
    )
    if not consent_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail=f"No consent given for source: {source_type}. Please provide consent before uploading.")

    # Verify profile belongs to user
    profile_result = await db.execute(
        select(ImmigrationProfileDB).where(
            ImmigrationProfileDB.id == profile_id,
            ImmigrationProfileDB.user_id == user.id,
        )
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Save file
    ext = os.path.splitext(file.filename or "file")[1].lstrip(".")
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse file
    try:
        parsed = route_parser(ext, source_type, file_path)
        extracted_text = parsed.get("text", str(parsed))
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail=f"Failed to parse file: {str(e)}")

    # Store evidence record
    evidence = EvidenceFile(
        profile_id=profile.id,
        filename=file.filename or "unknown",
        file_type=ext,
        source_type=source_type,
        file_path=file_path,
        extracted_text=extracted_text[:50000],  # Limit stored text
    )
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)

    return {
        "id": str(evidence.id),
        "filename": evidence.filename,
        "source_type": source_type,
        "extracted_preview": extracted_text[:500],
    }
```

**Step 4: Create profile CRUD router**

```python
# backend/app/routers/profiles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.database import User, ImmigrationProfileDB

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
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat(),
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
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
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
```

**Step 5: Register all routers in main.py**

```python
from app.routers.auth import router as auth_router
from app.routers.consent import router as consent_router
from app.routers.evidence import router as evidence_router
from app.routers.profiles import router as profiles_router

app.include_router(auth_router)
app.include_router(consent_router)
app.include_router(evidence_router)
app.include_router(profiles_router)
```

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: add consent, evidence upload, profile CRUD, and file parsers"
```

---

## Task 5: Backend — Agentic Pipeline (4 Claude Agents + SSE)

**Files:**
- Create: `backend/app/agents/__init__.py`
- Create: `backend/app/agents/base.py`
- Create: `backend/app/agents/ingestion.py`
- Create: `backend/app/agents/extraction.py`
- Create: `backend/app/agents/assessment.py`
- Create: `backend/app/agents/roadmap.py`
- Create: `backend/app/agents/pipeline.py` (orchestrator)
- Create: `backend/app/prompts/__init__.py`
- Create: `backend/app/prompts/extraction.py`
- Create: `backend/app/prompts/assessment.py`
- Create: `backend/app/prompts/roadmap.py`
- Create: `backend/app/prompts/shared.py` (USCIS criteria definitions)
- Create: `backend/app/routers/analyze.py` (SSE endpoint)

**Step 1: Create shared USCIS knowledge base**

```python
# backend/app/prompts/shared.py
USCIS_EB1A_CRITERIA = """
EB-1A EXTRAORDINARY ABILITY CRITERIA (Updated October 2024):

1. AWARDS: Receipt of lesser nationally or internationally recognized prizes or awards for excellence in the field. (Oct 2024 update: team awards now qualify.)

2. MEMBERSHIPS: Membership in associations that require outstanding achievements of their members, as judged by recognized experts. (Oct 2024 update: past memberships count.)

3. PUBLISHED MATERIAL: Published material about the beneficiary in professional or major trade publications or other major media. (Oct 2024 update: no longer requires demonstrating "the value of the person's work.")

4. JUDGING: Participation as a judge of the work of others in the same or an allied field, either individually or on a panel.

5. ORIGINAL CONTRIBUTIONS: Evidence of original scientific, scholarly, artistic, athletic, or business-related contributions of major significance in the field.

6. SCHOLARLY ARTICLES: Authorship of scholarly articles in professional or major trade publications or other major media.

7. EXHIBITIONS: Evidence of display of work at artistic exhibitions or showcases (primarily for arts fields).

8. LEADING/CRITICAL ROLE: Performance in a leading or critical role for organizations or establishments that have a distinguished reputation.

9. HIGH SALARY: Evidence that the beneficiary has commanded a high salary or significantly high remuneration relative to others in the field.

10. COMMERCIAL SUCCESS: Evidence of commercial successes in the performing arts.

PRACTICAL NOTE: While USCIS requires meeting 3 of 10 criteria, declining approval rates in 2025-2026 mean practically meeting 4-5 criteria is advisable.
"""

CONFIDENCE_RUBRIC = """
CONFIDENCE CALIBRATION:
- 90-100%: Evidence directly matches USCIS criteria with independent corroboration
  Example: Published peer review invitation letter from Nature journal -> Criterion 4
- 70-89%: Evidence is relevant and substantive but may need additional documentation
  Example: Self-reported conference PC membership without invitation letter -> Criterion 4
- 40-69%: Evidence is tangentially related or lacks specificity
  Example: Reviewed student papers as teaching assistant -> Criterion 4
- 0-39%: No meaningful evidence or evidence too weak
  Example: No judging/review experience found -> Criterion 4
"""

NIW_DHANASAR_FRAMEWORK = """
NIW (EB-2 National Interest Waiver) — Dhanasar Framework:

Prong 1: The proposed endeavor has both substantial merit and national importance.
Prong 2: The beneficiary is well-positioned to advance the proposed endeavor.
Prong 3: On balance, it would be beneficial to the United States to waive the job offer and labor certification requirements.
"""
```

**Step 2: Create prompt templates**

```python
# backend/app/prompts/extraction.py
EXTRACTION_SYSTEM = """You are a career data extraction specialist. Given raw text from career documents (CVs, publications, emails, etc.), extract structured immigration-relevant information.

Be thorough but accurate. If information is ambiguous, note it in the confidence reasoning. Only extract what is clearly stated or strongly implied."""

EXTRACTION_USER = """Extract a structured immigration profile from the following raw career data.

RAW DATA:
{raw_text}

Extract all: publications, awards, judging roles, media coverage, leadership roles, memberships, GitHub metrics, scholarly metrics, compensation info, and basic career details.

For each evidence item, assess confidence:
- data_confidence: How reliable is this data? (0-100)
- criteria_match: How well would this match USCIS criteria? (0-100)
- overall: Weighted combination (0.4 * data + 0.6 * criteria_match)
- reasoning: 2-3 sentences explaining the score

{confidence_rubric}"""
```

```python
# backend/app/prompts/assessment.py
ASSESSMENT_SYSTEM = """You are an immigration evidence analyst specializing in EB-1A extraordinary ability petitions. You have deep knowledge of USCIS adjudication standards, the two-step Kazarian framework, and the October 2024 policy updates.

{uscis_criteria}

{confidence_rubric}

IMPORTANT: The October 2024 update clarified that team awards now qualify under Criterion 1, past memberships count under Criterion 2, and published material no longer requires demonstrating "the value of the person's work" for Criterion 3.

You must assess ALL 10 criteria, even if evidence is absent. Be honest about gaps. Meeting 4-5 criteria (not just the minimum 3) is practically essential in 2025-2026 given declining approval rates."""

ASSESSMENT_USER = """Analyze the following structured immigration profile against all 10 EB-1A extraordinary ability criteria.

For EACH criterion, provide:
- evidence_found: specific items from the profile that support it
- strength: "strong" | "moderate" | "weak" | "none"
- confidence: data_confidence (0-100), criteria_match (0-100), overall (0-100), and reasoning (2-3 sentences)
- gaps: what specific evidence is missing
- priority_actions: top 2-3 concrete actions to strengthen this criterion

PROFILE:
{profile_json}

Assess against the {pathway} pathway. Be calibrated and honest. Do not inflate scores."""
```

```python
# backend/app/prompts/roadmap.py
ROADMAP_SYSTEM = """You are an immigration strategy advisor specializing in building evidence portfolios for extraordinary ability petitions. You create concrete, time-phased action plans that prioritize high-impact, achievable actions.

Your plans must be:
- Specific: Name actual conferences, journals, organizations where possible
- Time-bound: Organized by quarter
- Prioritized: Focus on criteria with best effort-to-impact ratio
- Realistic: Consider the person's current career stage and field"""

ROADMAP_USER = """Based on the following criteria assessment, generate a personalized immigration roadmap.

ASSESSMENT:
{assessment_json}

PROFILE SUMMARY:
- Name: {name}
- Field: {field}
- Target: {pathway}
- Timeline: {timeline_years} years
- Current strongest criteria: {strongest}
- Criteria needing most work: {weakest}
- Recommended focus areas: {focus}

Generate a quarterly action plan covering {timeline_years} years. For each action:
- Specify which criterion it strengthens
- Rate effort (low/medium/high) and impact (low/medium/high)
- Suggest specific opportunities (named conferences, journals, organizations)

End with a 3-4 paragraph narrative summary of the strategy.

IMPORTANT: Include this disclaimer: "This is not legal advice. Consult a qualified immigration attorney." """
```

**Step 3: Create agent base class and implementations**

```python
# backend/app/agents/base.py
from typing import AsyncGenerator
import anthropic
import json

from app.config import settings


class BaseAgent:
    def __init__(self, name: str, system_prompt: str, user_prompt_template: str, output_schema: type):
        self.name = name
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.output_schema = output_schema
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def run(self, **kwargs) -> dict:
        user_prompt = self.user_prompt_template.format(**kwargs)

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=8192,
            temperature=0.2,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            headers={"anthropic-beta": "structured-outputs-2025-11-13"},
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": self.output_schema.__name__,
                    "schema": self.output_schema.model_json_schema(),
                },
            },
        )

        text = response.content[0].text
        return json.loads(text)

    async def run_streaming(self, **kwargs) -> AsyncGenerator[dict, None]:
        """Yields progress events while running."""
        yield {"agent": self.name, "status": "started"}
        try:
            result = await self.run(**kwargs)
            yield {"agent": self.name, "status": "completed", "result": result}
        except Exception as e:
            yield {"agent": self.name, "status": "error", "error": str(e)}
```

```python
# backend/app/agents/ingestion.py
from app.models.schemas import RawCareerData, RawSourceData, EvidenceSource
from app.parsers.router import route_parser


class IngestionAgent:
    """No LLM call — parses files and assembles raw career data."""

    async def run(self, evidence_files: list[dict]) -> RawCareerData:
        sources = []
        notes = []

        for ef in evidence_files:
            try:
                parsed = route_parser(ef["file_type"], ef["source_type"], ef["file_path"])
                text = parsed.get("text", str(parsed))
                sources.append(RawSourceData(
                    source=EvidenceSource(ef["source_type"]),
                    raw_text=text[:30000],  # Limit per source for context window
                    file_name=ef["filename"],
                    metadata=parsed,
                ))
            except Exception as e:
                notes.append(f"Failed to parse {ef['filename']}: {str(e)}")

        return RawCareerData(
            sources=sources,
            total_files_processed=len(evidence_files),
            extraction_notes=notes,
        )
```

```python
# backend/app/agents/extraction.py
from app.agents.base import BaseAgent
from app.models.schemas import ImmigrationProfile
from app.prompts.extraction import EXTRACTION_SYSTEM, EXTRACTION_USER
from app.prompts.shared import CONFIDENCE_RUBRIC


class ExtractionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="extraction",
            system_prompt=EXTRACTION_SYSTEM,
            user_prompt_template=EXTRACTION_USER,
            output_schema=ImmigrationProfile,
        )

    async def run(self, raw_career_data_json: str) -> dict:
        return await super().run(
            raw_text=raw_career_data_json,
            confidence_rubric=CONFIDENCE_RUBRIC,
        )
```

```python
# backend/app/agents/assessment.py
from app.agents.base import BaseAgent
from app.models.schemas import CriteriaAssessment
from app.prompts.assessment import ASSESSMENT_SYSTEM, ASSESSMENT_USER
from app.prompts.shared import USCIS_EB1A_CRITERIA, CONFIDENCE_RUBRIC


class AssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="assessment",
            system_prompt=ASSESSMENT_SYSTEM.format(
                uscis_criteria=USCIS_EB1A_CRITERIA,
                confidence_rubric=CONFIDENCE_RUBRIC,
            ),
            user_prompt_template=ASSESSMENT_USER,
            output_schema=CriteriaAssessment,
        )

    async def run(self, profile_json: str, pathway: str = "EB-1A") -> dict:
        return await super().run(profile_json=profile_json, pathway=pathway)
```

```python
# backend/app/agents/roadmap.py
from app.agents.base import BaseAgent
from app.models.schemas import ImmigrationRoadmap
from app.prompts.roadmap import ROADMAP_SYSTEM, ROADMAP_USER


class RoadmapAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="roadmap",
            system_prompt=ROADMAP_SYSTEM,
            user_prompt_template=ROADMAP_USER,
            output_schema=ImmigrationRoadmap,
        )

    async def run(self, assessment_json: str, name: str, field: str,
                  pathway: str, timeline_years: int, strongest: str,
                  weakest: str, focus: str) -> dict:
        return await super().run(
            assessment_json=assessment_json,
            name=name, field=field, pathway=pathway,
            timeline_years=timeline_years, strongest=strongest,
            weakest=weakest, focus=focus,
        )
```

**Step 4: Create pipeline orchestrator + SSE endpoint**

```python
# backend/app/agents/pipeline.py
import json
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.ingestion import IngestionAgent
from app.agents.extraction import ExtractionAgent
from app.agents.assessment import AssessmentAgent
from app.agents.roadmap import RoadmapAgent
from app.models.database import ImmigrationProfileDB, EvidenceFile


async def run_pipeline(profile_id: str, db: AsyncSession) -> AsyncGenerator[dict, None]:
    # Load profile and evidence files
    result = await db.execute(
        select(ImmigrationProfileDB).where(ImmigrationProfileDB.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        yield {"event": "error", "data": "Profile not found"}
        return

    evidence_result = await db.execute(
        select(EvidenceFile).where(EvidenceFile.profile_id == profile_id)
    )
    evidence_files = evidence_result.scalars().all()

    if not evidence_files:
        yield {"event": "error", "data": "No evidence files uploaded"}
        return

    ef_dicts = [
        {"file_type": ef.file_type, "source_type": ef.source_type,
         "file_path": ef.file_path, "filename": ef.filename}
        for ef in evidence_files
    ]

    # Agent 1: Ingestion
    yield {"event": "stage", "data": {"stage": "ingestion", "status": "started"}}
    profile.status = "ingesting"
    await db.commit()

    ingestion_agent = IngestionAgent()
    raw_data = await ingestion_agent.run(ef_dicts)
    profile.raw_career_data = raw_data.model_dump(mode="json")
    await db.commit()
    yield {"event": "stage", "data": {"stage": "ingestion", "status": "completed", "files_processed": raw_data.total_files_processed}}

    # Agent 2: Extraction
    yield {"event": "stage", "data": {"stage": "extraction", "status": "started"}}
    profile.status = "extracting"
    await db.commit()

    extraction_agent = ExtractionAgent()
    profile_data = await extraction_agent.run(raw_career_data_json=raw_data.model_dump_json())
    profile.profile_data = profile_data
    await db.commit()
    yield {"event": "stage", "data": {"stage": "extraction", "status": "completed"}}

    # Agent 3: Assessment
    yield {"event": "stage", "data": {"stage": "assessment", "status": "started"}}
    profile.status = "assessing"
    await db.commit()

    assessment_agent = AssessmentAgent()
    pathway = profile_data.get("target_pathway", "eb1a")
    assessment_data = await assessment_agent.run(
        profile_json=json.dumps(profile_data),
        pathway=pathway.upper().replace("_", "-"),
    )
    profile.assessment_data = assessment_data
    await db.commit()
    yield {"event": "stage", "data": {"stage": "assessment", "status": "completed"}}

    # Agent 4: Roadmap
    yield {"event": "stage", "data": {"stage": "roadmap", "status": "started"}}
    profile.status = "roadmapping"
    await db.commit()

    roadmap_agent = RoadmapAgent()
    roadmap_data = await roadmap_agent.run(
        assessment_json=json.dumps(assessment_data),
        name=profile_data.get("name", "Applicant"),
        field=profile_data.get("field_of_expertise", "Technology"),
        pathway=pathway.upper().replace("_", "-"),
        timeline_years=profile_data.get("target_timeline_years", 2),
        strongest=str(assessment_data.get("strongest_criteria", [])),
        weakest=str(assessment_data.get("weakest_criteria", [])),
        focus=str(assessment_data.get("recommended_focus", [])),
    )
    profile.roadmap_data = roadmap_data
    profile.status = "complete"
    await db.commit()
    yield {"event": "stage", "data": {"stage": "roadmap", "status": "completed"}}
    yield {"event": "complete", "data": {"profile_id": profile_id}}
```

```python
# backend/app/routers/analyze.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.database import User, ImmigrationProfileDB
from app.agents.pipeline import run_pipeline

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.get("/stream/{profile_id}")
async def stream_analysis(
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
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
            yield {"event": event.get("event", "message"), "data": json.dumps(event.get("data", {}))}

    return EventSourceResponse(event_generator())
```

**Step 5: Register analyze router in main.py**

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: add 4-agent Claude pipeline with SSE streaming and prompt templates"
```

---

## Task 6: Backend — Export Engine (JSON, Markdown, PDF, DOCX)

**Files:**
- Create: `backend/app/routers/export.py`
- Create: `backend/app/export/__init__.py`
- Create: `backend/app/export/markdown.py`
- Create: `backend/app/export/pdf.py`
- Create: `backend/app/export/docx.py`

**Step 1: Create exporters** — each takes profile/assessment/roadmap dicts and returns bytes/string.

Markdown exporter generates a human-readable report. PDF uses reportlab. DOCX uses python-docx. JSON is native.

**Step 2: Create export router**

Endpoint: `GET /api/export/{profile_id}?format=json|markdown|pdf|docx`

Returns file download with appropriate Content-Type and immigration disclaimer header.

**Step 3: Commit**

```bash
git add backend/
git commit -m "feat: add export engine for JSON, Markdown, PDF, and DOCX"
```

---

## Task 7: Backend — Data Deletion Endpoint

**Files:**
- Create: `backend/app/routers/data.py`

Single endpoint: `DELETE /api/data/me` — cascading deletion of all user data (profile, evidence files on disk, consents). Returns confirmation.

**Commit**

```bash
git add backend/
git commit -m "feat: add complete user data deletion endpoint"
```

---

## Task 8: Shared Schemas — JSON Schema Export + TypeScript Generation

**Files:**
- Create: `shared/schemas/immigration_profile.json`
- Create: `shared/schemas/criteria_assessment.json`
- Create: `shared/schemas/immigration_roadmap.json`
- Create: `shared/generate_schemas.py` (run from backend to export Pydantic → JSON Schema)
- Create: `shared/package.json`
- Create: `shared/generate-types.ts`
- Create: `shared/types/index.ts` (generated output)

**Step 1: Create Python script that exports Pydantic models to JSON Schema files**

```python
# shared/generate_schemas.py
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.models.schemas import ImmigrationProfile, CriteriaAssessment, ImmigrationRoadmap

for model in [ImmigrationProfile, CriteriaAssessment, ImmigrationRoadmap]:
    path = f"schemas/{model.__name__}.json"
    with open(os.path.join(os.path.dirname(__file__), path), "w") as f:
        json.dump(model.model_json_schema(), f, indent=2)
    print(f"Wrote {path}")
```

**Step 2: Generate TypeScript types from JSON Schema using json-schema-to-typescript**

```bash
cd shared && pnpm add -D json-schema-to-typescript && pnpm exec json2ts -i schemas/ -o types/
```

**Step 3: Commit**

```bash
git add shared/
git commit -m "feat: add shared JSON schemas and TypeScript type generation from Pydantic"
```

---

## Task 9: Frontend Scaffold — Next.js 16 + shadcn/ui + Tailwind + Auth

**Files:**
- Create: `frontend/` via `pnpm create next-app`
- Configure: shadcn/ui, Tailwind, NextAuth.js v5, React Query, Zustand

**Step 1: Scaffold Next.js**

```bash
cd /path/to/repo && pnpm create next-app frontend --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --turbopack
```

**Step 2: Install dependencies**

```bash
cd frontend && pnpm add next-auth@beta @tanstack/react-query zustand nextstepjs recharts @radix-ui/react-dialog @radix-ui/react-slot class-variance-authority clsx tailwind-merge lucide-react framer-motion
```

**Step 3: Initialize shadcn/ui**

```bash
cd frontend && pnpm dlx shadcn@latest init -d
```

**Step 4: Add shadcn components**

```bash
pnpm dlx shadcn@latest add button card input label dialog badge tabs chart textarea separator avatar dropdown-menu sheet toast form select
```

**Step 5: Set up NextAuth.js v5 with credentials provider**

Create `frontend/auth.ts`, `frontend/app/api/auth/[...nextauth]/route.ts`

**Step 6: Set up React Query provider and Zustand store**

Create `frontend/lib/providers.tsx`, `frontend/lib/store.ts`, `frontend/lib/api.ts` (API client)

**Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Next.js 16 with shadcn/ui, NextAuth, React Query, Zustand"
```

---

## Task 10: Frontend — Landing Page + Auth Pages

**Files:**
- Create: `frontend/app/(public)/page.tsx` — landing page
- Create: `frontend/app/(public)/login/page.tsx`
- Create: `frontend/app/(public)/register/page.tsx`
- Create: `frontend/app/(public)/layout.tsx`

**Step 1: Build landing page**

Hero section: "Turn Your Career Data Into an Immigration Roadmap"
Features grid: Data aggregation, AI analysis, Criteria scoring, Personalized roadmap
CTA: "Get Started" → register

**Step 2: Build login/register pages**

Email + password forms using shadcn/ui Input, Button, Card. Registration includes name field. Both call backend API, store JWT in NextAuth session. Show data handling notice on register page.

**Step 3: Commit**

```bash
git add frontend/
git commit -m "feat: add landing page, login, and registration with data handling notices"
```

---

## Task 11: Frontend — Dashboard Layout + Data Consent Flow

**Files:**
- Create: `frontend/app/(dashboard)/layout.tsx` — sidebar, header, NextStep provider
- Create: `frontend/components/sidebar.tsx`
- Create: `frontend/components/consent-modal.tsx`
- Create: `frontend/app/(dashboard)/page.tsx` — dashboard home

**Step 1: Dashboard layout**

Sidebar with nav: Evidence, Criteria, Roadmap, Export, Chat, Settings. Header with user avatar + logout. Responsive.

**Step 2: Consent modal component**

Reusable modal that:
- Displays data source name and icon
- Lists what data will be accessed
- Explains processing steps (local parsing + Claude API)
- Has explicit "I consent" / "Cancel" buttons
- Calls `/api/consent` on approval
- Shows consent timestamp after approval

**Step 3: Dashboard home**

Overview cards: profile status, criteria met count, next action item. Quick links to upload evidence, view criteria, see roadmap.

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: add dashboard layout with sidebar, consent modal, and overview"
```

---

## Task 12: Frontend — Evidence Upload Page

**Files:**
- Create: `frontend/app/(dashboard)/evidence/page.tsx`
- Create: `frontend/components/file-upload-zone.tsx`
- Create: `frontend/components/evidence-card.tsx`
- Create: `frontend/components/analysis-stream.tsx`

**Step 1: Evidence upload page**

Grid of upload zones by source type: CV/Resume, Google Scholar, GitHub, Gmail (MBOX), Calendar (ICS), ChatGPT Export, LinkedIn PDF. Each zone triggers consent modal before allowing upload.

**Step 2: File upload component**

Drag-and-drop zone using shadcn/ui. Shows accepted file types. Uploads to `/api/evidence/upload`. Shows progress and extracted preview.

**Step 3: Analysis stream component**

Connects to SSE `/api/analyze/stream/{id}`. Shows 4-stage progress: Ingestion → Extraction → Assessment → Roadmap. Each stage shows spinner while active, checkmark when done.

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: add evidence upload page with consent-gated file uploads and analysis streaming"
```

---

## Task 13: Frontend — Criteria Dashboard (Radar Chart + Cards)

**Files:**
- Create: `frontend/app/(dashboard)/criteria/page.tsx`
- Create: `frontend/components/criteria-radar-chart.tsx`
- Create: `frontend/components/criterion-card.tsx`
- Create: `frontend/components/confidence-badge.tsx`

**Step 1: Criteria radar chart**

Full-width Recharts RadarChart with all 10 EB-1A criteria as axes. Color-coded fill by strength. Responsive. Uses shadcn Chart container.

**Step 2: Criterion cards**

Grid of 10 cards, each showing: criterion name, strength badge (strong/moderate/weak/none), confidence percentage with color badge (green >70, amber 40-70, red <40), evidence items found, gaps identified, "Show AI Reasoning" expandable, priority actions.

**Step 3: Confidence badge component**

Reusable badge: green variant for >70%, amber for 40-70%, red for <40%.

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: add criteria dashboard with radar chart, criterion cards, and confidence badges"
```

---

## Task 14: Frontend — Roadmap Timeline Page

**Files:**
- Create: `frontend/app/(dashboard)/roadmap/page.tsx`
- Create: `frontend/components/roadmap-timeline.tsx`
- Create: `frontend/components/roadmap-action-card.tsx`

**Step 1: Roadmap timeline**

Horizontal timeline visualization showing quarterly milestones. Each quarter is a column with action cards. Actions color-coded by effort/impact level. Each action shows which criteria it targets.

**Step 2: Narrative summary section**

Below the timeline: the 3-4 paragraph AI-generated strategy narrative. Immigration disclaimer prominently displayed.

**Step 3: Commit**

```bash
git add frontend/
git commit -m "feat: add roadmap timeline visualization with quarterly milestones"
```

---

## Task 15: Frontend — Export Center + Settings

**Files:**
- Create: `frontend/app/(dashboard)/export/page.tsx`
- Create: `frontend/app/(dashboard)/settings/page.tsx`

**Step 1: Export center**

4 export buttons: JSON, Markdown, PDF, DOCX. Each calls `/api/export/{id}?format=X` and triggers download. Preview section shows what will be exported. Immigration disclaimer included.

**Step 2: Settings page**

- Profile info (name, email)
- Active consents list with revoke buttons
- Data deletion button ("Delete all my data") with confirmation dialog
- Processing transparency log

**Step 3: Commit**

```bash
git add frontend/
git commit -m "feat: add export center and settings page with consent management and data deletion"
```

---

## Task 16: Frontend — NextStepJS Onboarding Flow

**Files:**
- Create: `frontend/components/onboarding-tour.tsx`
- Modify: `frontend/app/(dashboard)/layout.tsx` — add NextStep provider

**Step 1: Define onboarding tour**

7-step tour from the spec: Welcome, Choose pathway, Bring your data (with consent emphasis), Watch AI analyze, Criteria dashboard, Roadmap, Export & own your data.

**Step 2: Trigger on first login**

Check localStorage flag. Show tour on first dashboard visit. "Skip" and "Next" buttons.

**Step 3: Commit**

```bash
git add frontend/
git commit -m "feat: add NextStepJS onboarding tour for first-time users"
```

---

## Task 17: Synthetic Data — Generate Demo Persona Files

**Files:**
- Create: `synthetic-data/generate.py`
- Create: `synthetic-data/priya-sharma/cv.pdf`
- Create: `synthetic-data/priya-sharma/scholar.json`
- Create: `synthetic-data/priya-sharma/gmail.mbox`
- Create: `synthetic-data/priya-sharma/calendar.ics`
- Create: `synthetic-data/marco-chen/cv.pdf`
- Create: `synthetic-data/marco-chen/github.json`
- Create: `synthetic-data/marco-chen/linkedin.pdf`
- Create: `synthetic-data/amara-okafor/cv.pdf`
- Create: `synthetic-data/amara-okafor/linkedin.pdf`
- Create: `synthetic-data/amara-okafor/chatgpt-export.json`
- Create: `synthetic-data/amara-okafor/media-urls.json`

**Step 1: Create Python generation script**

Uses reportlab for PDF generation, builds MBOX files programmatically, creates realistic ICS calendar entries, generates ChatGPT export JSON structure. All data matches persona specs from README §8.3.

**Step 2: Run generator**

```bash
cd synthetic-data && python generate.py
```

**Step 3: Verify files parse correctly through backend parsers**

**Step 4: Commit**

```bash
git add synthetic-data/
git commit -m "feat: generate synthetic demo files for 3 personas (Priya, Marco, Amara)"
```

---

## Task 18: Seed Script — Load Synthetic Personas into DB

**Files:**
- Create: `backend/app/seed.py`

Script that:
1. Creates 3 demo user accounts (one per persona)
2. Gives consent for each data source
3. Creates profiles
4. Copies synthetic files to uploads directory
5. Creates evidence file records
6. Optionally runs the full pipeline for each persona (pre-caches results)

Run: `cd backend && uv run python -m app.seed`

**Commit**

```bash
git add backend/app/seed.py
git commit -m "feat: add seed script to load synthetic personas into database"
```

---

## Task 19: Integration — Connect Frontend to Backend

**Files:**
- Modify: `frontend/lib/api.ts` — all API calls
- Create: `frontend/lib/hooks.ts` — React Query hooks for each endpoint
- Modify: all dashboard pages to use real data

**Step 1: API client**

Axios or fetch wrapper that attaches JWT from NextAuth session. Base URL from env.

**Step 2: React Query hooks**

`useProfile`, `useAssessment`, `useRoadmap`, `useConsents`, `useAnalysisStream` (SSE), `useExport`.

**Step 3: Wire up all pages to use real data instead of placeholders**

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: connect all frontend pages to backend API with React Query hooks"
```

---

## Task 20: Polish + Final Testing

**Step 1: Run full demo flow end-to-end with each persona**
**Step 2: Fix any UI/UX issues**
**Step 3: Verify all exports work**
**Step 4: Verify data deletion works**
**Step 5: Update CLAUDE.md with actual dev commands**

**Commit**

```bash
git add -A
git commit -m "feat: polish UI, fix integration issues, update documentation"
```

---

## Execution Order

Tasks 1-8 are backend. Tasks 9-16 are frontend. Task 17-18 are synthetic data. Task 19 integrates. Task 20 polishes. Tasks 1-8 and 9-16 can run in parallel (two developers or two agents).

**Critical path**: Task 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 (backend) and Task 9 → 10 → 11 → 12 → 13 → 14 → 15 → 16 (frontend) converge at Task 19.
