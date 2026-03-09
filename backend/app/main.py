import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.limiter import limiter
from app.routers.auth import router as auth_router
from app.routers.consent import router as consent_router
from app.routers.evidence import router as evidence_router
from app.routers.profiles import router as profiles_router
from app.routers.analyze import router as analyze_router
from app.routers.export import router as export_router
from app.routers.data import router as data_router
from app.routers.onboarding import router as onboarding_router

logger = logging.getLogger(__name__)


def _init_vector_db():
    """Seed the RAG vector database with immigration law corpus on first run."""
    try:
        from app.services.legal_corpus import seed_corpus
        seed_corpus()
    except Exception as e:
        logger.warning(f"Vector DB initialization skipped: {e}")


async def _run_migrations():
    """Add columns that create_all can't add to existing tables."""
    from sqlalchemy import text
    from app.database import engine

    migrations = [
        ("users", "onboarding_completed", "ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT FALSE"),
        ("users", "onboarding_data", "ALTER TABLE users ADD COLUMN onboarding_data JSON"),
        ("immigration_profiles", "target_pathway", "ALTER TABLE immigration_profiles ADD COLUMN target_pathway VARCHAR(10)"),
        ("immigration_profiles", "pathway_changed_since_analysis", "ALTER TABLE immigration_profiles ADD COLUMN pathway_changed_since_analysis BOOLEAN DEFAULT FALSE"),
        ("immigration_profiles", "last_pathway_switch", "ALTER TABLE immigration_profiles ADD COLUMN last_pathway_switch TIMESTAMPTZ"),
        ("immigration_profiles", "last_analysis_run", "ALTER TABLE immigration_profiles ADD COLUMN last_analysis_run TIMESTAMPTZ"),
    ]
    async with engine.begin() as conn:
        for table, column, ddl in migrations:
            exists = await conn.execute(text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = :table AND column_name = :column"
            ), {"table": table, "column": column})
            if not exists.scalar():
                logger.info(f"Migration: adding {table}.{column}")
                await conn.execute(text(ddl))


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        await _run_migrations()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    _init_vector_db()
    yield


app = FastAPI(
    title="Immigration Roadmap API",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
    settings.frontend_url,
    "http://localhost:3000",
    "https://immigration-roadmap.com",
    "https://www.immigration-roadmap.com",
]
origins = list(dict.fromkeys(origins))

# NOTE: Starlette executes middlewares in reverse order of addition.
# The LAST added middleware runs OUTERMOST (processes requests first).
# We add security headers FIRST (inner), then CORS LAST (outer),
# so CORS headers are always present — even on error responses.


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(consent_router)
app.include_router(evidence_router)
app.include_router(profiles_router)
app.include_router(analyze_router)
app.include_router(export_router)
app.include_router(data_router)
app.include_router(onboarding_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/health/db")
async def health_db():
    from sqlalchemy import text
    from app.database import async_session
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": str(e)},
        )
