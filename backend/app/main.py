import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers.auth import router as auth_router
from app.routers.consent import router as consent_router
from app.routers.evidence import router as evidence_router
from app.routers.profiles import router as profiles_router
from app.routers.analyze import router as analyze_router
from app.routers.export import router as export_router
from app.routers.data import router as data_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    yield


app = FastAPI(
    title="Immigration Roadmap API",
    version="0.1.0",
    lifespan=lifespan,
)

origins = [settings.frontend_url, "http://localhost:3000"]
# Deduplicate while preserving order
origins = list(dict.fromkeys(origins))

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


@app.get("/api/health")
async def health():
    return {"status": "ok"}
