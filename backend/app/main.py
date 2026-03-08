import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
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

origins = [settings.frontend_url, "http://localhost:3000"]
origins = list(dict.fromkeys(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


app.include_router(auth_router)
app.include_router(consent_router)
app.include_router(evidence_router)
app.include_router(profiles_router)
app.include_router(analyze_router)
app.include_router(export_router)
app.include_router(data_router)
app.include_router(onboarding_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
