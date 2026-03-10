# Backend — Immigration Empowerment Through Data Portability

FastAPI backend with a four-agent AI pipeline, ChromaDB RAG, PII scrubbing, and multi-format export.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (fully async, Python 3.13) |
| AI | Claude Sonnet 4.5 via `anthropic` >=0.52.0 with Structured Outputs |
| RAG | ChromaDB >=0.5.0 — USCIS legal corpus seeded on startup |
| ORM | async SQLAlchemy 2.0 + asyncpg + Pydantic v2 |
| Database | PostgreSQL 16 (Docker, port 5433) |
| Auth | python-jose (JWT) + passlib[bcrypt] |
| PII | Custom scrubber (emails, phones, SSNs, DOBs, addresses) |
| Parsing | PyMuPDF (PDF), Claude Vision (images), custom (MBOX, ICS, JSON, LinkedIn) |
| Export | python-docx (DOCX), ReportLab (PDF), native (JSON, Markdown) |
| Streaming | sse-starlette (Server-Sent Events) |
| Rate Limiting | slowapi (1 analysis/week, 1 pathway switch/month) |

## Getting Started

```bash
# Prerequisites: Docker running, PostgreSQL started via docker compose up -d

uv sync                               # Create venv and install deps
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000   # Start dev server

# Optional: seed demo personas
python -m app.seed
```

API docs available at `http://localhost:8000/docs` (Swagger UI).

## Running Tests

```bash
.venv/bin/python -m pytest tests/ -v    # Uses SQLite in-memory — no Docker needed
```

## Project Structure

```
app/
├── main.py                    # FastAPI app, lifespan, CORS, routes, startup migrations
├── config.py                  # Pydantic Settings (env vars)
├── auth.py                    # JWT creation/validation, password hashing, get_current_user
├── database.py                # SQLAlchemy async engine, session factory
├── limiter.py                 # slowapi rate limiter setup
├── seed.py                    # Demo persona seeder (3 profiles with synthetic files)
│
├── models/
│   ├── database.py            # SQLAlchemy models: User, ImmigrationProfileDB, EvidenceFile, DataConsent
│   └── schemas.py             # Pydantic models: ImmigrationProfile, CriteriaAssessment, ImmigrationRoadmap, etc.
│
├── routers/
│   ├── auth.py                # POST /register, /login, GET /me
│   ├── onboarding.py          # GET/POST /onboarding/ — 6-step wizard + pathway recommendation
│   ├── profiles.py            # CRUD profiles, PATCH pathway (30-day cooldown)
│   ├── evidence.py            # POST /upload, GET/DELETE evidence files
│   ├── analyze.py             # POST /token/{id}, GET /stream/{id}?token=JWT (SSE)
│   ├── export.py              # GET /export/{id}?format=json|markdown|pdf|docx
│   ├── consent.py             # Per-source consent tracking
│   └── data.py                # DELETE /me (full), DELETE /me/data-only
│
├── agents/
│   ├── base.py                # BaseAgent — Claude API wrapper, structured outputs, prompt injection detection
│   ├── pipeline.py            # Orchestrator — runs 4 agents sequentially, yields SSE events
│   ├── ingestion.py           # Agent 1: file parsing + PII scrubbing (no LLM call)
│   ├── extraction.py          # Agent 2: Claude → ImmigrationProfile
│   ├── assessment.py          # Agent 3: Claude + ChromaDB RAG → CriteriaAssessment
│   └── roadmap.py             # Agent 4: Claude + ChromaDB RAG → ImmigrationRoadmap
│
├── parsers/
│   ├── router.py              # Routes (file_type, source_type) → correct parser
│   ├── pdf_parser.py          # PyMuPDF text extraction
│   ├── mbox_parser.py         # Gmail MBOX parsing
│   ├── ics_parser.py          # Calendar ICS event extraction
│   ├── json_parser.py         # ChatGPT export, Google Takeout, Scholar, GitHub JSON
│   ├── linkedin_parser.py     # LinkedIn PDF/text parsing
│   └── image_parser.py        # Claude Vision API for certificate images
│
├── prompts/
│   ├── shared.py              # USCIS criteria definitions (EB-1A/B/C, NIW, O-1), confidence rubric, pathway notes
│   ├── extraction.py          # Extraction agent prompt templates
│   ├── assessment.py          # Assessment agent prompt templates (pathway-aware)
│   └── roadmap.py             # Roadmap agent prompt templates
│
├── services/
│   ├── vector_db.py           # ChromaDB client wrapper (add_documents, query, get_stats)
│   ├── legal_corpus.py        # Seeds ChromaDB with curated USCIS guidance on startup
│   └── pii_scrubber.py        # PII redaction: scrub_text, scrub_email_headers, scrub_file_on_disk, scrub_json_strings
│
├── export/
│   ├── markdown.py            # Markdown export
│   ├── pdf.py                 # ReportLab PDF generation
│   └── docx_export.py         # python-docx DOCX generation
│
tests/
└── ...                        # pytest + pytest-asyncio (SQLite in-memory)
```

## Agentic Pipeline

Four sequential agents orchestrated by `agents/pipeline.py`:

```
Upload files
    │
    ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ 1. INGESTION     │ ─→ │ 2. EXTRACTION    │ ─→ │ 3. ASSESSMENT    │ ─→ │ 4. ROADMAP       │
│                  │    │                  │    │                  │    │                  │
│ Parse files via  │    │ Claude Structured│    │ Score evidence   │    │ Generate time-   │
│ type-specific    │    │ Outputs →        │    │ vs USCIS criteria│    │ phased action    │
│ parsers          │    │ ImmigrationProfile│   │ + ChromaDB RAG   │    │ plan + ChromaDB  │
│ + PII scrubbing  │    │                  │    │ → CriteriaAssmt  │    │ → ImmigrationRdmp│
│                  │    │ (no raw PII      │    │                  │    │                  │
│ No LLM call      │    │  reaches Claude) │    │ Pathway-specific │    │ Quarterly        │
│                  │    │                  │    │ criteria counts: │    │ milestones with   │
│ → RawCareerData  │    │                  │    │ EB-1A:10 EB-1B:6│    │ effort/impact    │
│                  │    │                  │    │ EB-1C:5 NIW:3   │    │ levels           │
│                  │    │                  │    │ O-1:8           │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘
                              ↑                        ↑                        ↑
                    Structured Outputs         ChromaDB RAG            ChromaDB RAG
                    (guaranteed valid)       (5 legal passages)     (5 legal passages)
```

All progress streamed via SSE to the frontend.

## Key Services

### PII Scrubber (`services/pii_scrubber.py`)

Runs before any data reaches Claude API:

| Redacted | Preserved |
|----------|-----------|
| Email addresses | Person names |
| Phone numbers | Organization names |
| SSN patterns | Dates (non-DOB) |
| Dates of birth | Job titles |
| US street addresses | Publication titles |

### ChromaDB RAG (`services/vector_db.py` + `services/legal_corpus.py`)

On startup, `legal_corpus.py` seeds ChromaDB with curated USCIS policy guidance:
- Pathway-specific criteria definitions and evidence requirements
- Oct 2024 policy updates, Dhanasar framework, threshold guidance
- Each passage tagged with pathway metadata for filtered retrieval
- Assessment and roadmap agents query top-5 relevant passages before each Claude call

## API Endpoints

### Auth
- `POST /api/auth/register` — Create account
- `POST /api/auth/login` — Get JWT token
- `GET /api/auth/me` — Current user info

### Onboarding
- `GET/POST /api/onboarding/` — 6-step wizard data + pathway recommendation

### Profiles
- `GET/POST /api/profiles/` — CRUD immigration profiles
- `PATCH /api/profiles/{id}/pathway` — Switch pathway (30-day cooldown)

### Evidence
- `POST /api/evidence/upload` — Upload evidence files
- `GET /api/evidence/{profile_id}` — List evidence for profile
- `DELETE /api/evidence/{evidence_id}` — Delete evidence file

### Analysis
- `POST /api/analyze/token/{profile_id}` — Get SSE auth token
- `GET /api/analyze/stream/{profile_id}?token=JWT` — SSE stream for pipeline

### Export
- `GET /api/export/{profile_id}?format=json|markdown|pdf|docx` — Export profile

### Privacy & Data
- `GET/POST /api/consent/` — Per-source consent tracking
- `DELETE /api/data/me` — Full account deletion (cascading)
- `DELETE /api/data/me/data-only` — Delete data, keep account

## Database

PostgreSQL 16 via Docker (port 5433). Four tables:

- **users** — authentication, onboarding state, onboarding_data (JSON)
- **immigration_profiles** — per-user analysis profiles with JSON columns for profile_data, raw_career_data, assessment_data, roadmap_data
- **evidence_files** — uploaded files with extracted text, linked to profiles
- **data_consents** — per-source consent records with timestamps

Migrations handled in-app via `_run_migrations()` in `main.py` — checks `information_schema.columns` and issues `ALTER TABLE` for new columns.

## Deployment

Deployed on Railway at [backend-production-95ea4.up.railway.app](https://backend-production-95ea4.up.railway.app). Auto-deploys on push to `main`. Manual deploy: `railway up --detach`.
