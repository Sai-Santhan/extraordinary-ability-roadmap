# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered immigration roadmap tool for the **Data Portability Hackathon (Track 3: Personal Data, Personal Value)**. Aggregates scattered career data (CV, Google Scholar, GitHub, Google Takeout, ChatGPT exports, LinkedIn PDF, images) into a unified immigration profile, scores evidence against EB-1A/EB-1B/EB-1C/NIW/O-1 criteria using RAG-augmented AI, and generates a personalized multi-year roadmap.

## Development Commands

### Prerequisites
- Docker (for PostgreSQL)
- Node.js 22+ with pnpm
- Python 3.13+ with uv (backend venv)

### Database
```bash
docker compose up -d          # Start PostgreSQL on port 5433
docker compose down           # Stop database
```

### Backend (FastAPI)
```bash
cd backend
source .venv/bin/activate     # Or: .venv/bin/python
pip install -e ".[dev]"       # Install deps (first time)
uvicorn app.main:app --reload --port 8000   # Start dev server
python -m app.seed            # Seed demo personas (priya@demo.com, marco@demo.com, amara@demo.com / demo1234)
```

### Frontend (Next.js 16)
```bash
cd frontend
pnpm install                  # Install deps (first time)
pnpm dev                      # Start dev server on port 3000
pnpm build                    # Production build (also runs TypeScript checks)
```

### Backend Tests
```bash
cd backend
.venv/bin/python -m pytest tests/ -v    # Uses SQLite in-memory (no Docker needed)
```

## Architecture

**Monorepo**: `frontend/` (Next.js 16 + pnpm), `backend/` (FastAPI + SQLAlchemy), `shared/` (JSON schemas), `synthetic-data/` (demo files)

**Frontend**: Next.js 16.1.6 App Router + shadcn/ui (Base UI, not Radix) + Tailwind CSS + Zustand + React Query + Recharts

**Backend**: FastAPI + async SQLAlchemy + Pydantic v2 + Claude API (Sonnet 4.5 Structured Outputs) + ChromaDB (RAG) + PostgreSQL 16

**Auth**: Custom JWT-based (python-jose + raw bcrypt). Token stored in Zustand with localStorage persistence. SSE endpoints accept token as query parameter (EventSource can't send headers). No NextAuth — it's in package.json but unused.

**Important**: shadcn/ui uses Base UI (`@base-ui/react`), NOT Radix. Use `render` prop instead of `asChild` for component composition (e.g., `<DialogTrigger render={<Button />}>` not `<DialogTrigger asChild>`).

## Agentic Pipeline

Four sequential agents, each a Claude API call with Pydantic structured output:
1. **Ingestion Agent** — file parsing via type-specific parsers (no LLM), text extraction → `RawCareerData`
2. **Extraction Agent** — Claude Structured Outputs → `ImmigrationProfile`
3. **Assessment Agent** — scores evidence vs USCIS criteria + ChromaDB RAG → `CriteriaAssessment`
4. **Roadmap Agent** — generates time-phased action plan + ChromaDB RAG → `ImmigrationRoadmap`

Pipeline orchestrator: `backend/app/agents/pipeline.py`. Progress streamed to frontend via SSE at `GET /api/analyze/stream/{profile_id}?token=JWT`.

## Key Backend Paths

- **Parsers**: `backend/app/parsers/` — pdf, json, linkedin, mbox, ics, image parsers + router
- **Agents**: `backend/app/agents/` — ingestion, extraction, assessment, roadmap + pipeline orchestrator
- **Prompts**: `backend/app/prompts/` — extraction, assessment, roadmap templates + shared constants
- **Services**: `backend/app/services/` — vector_db (ChromaDB client), legal_corpus (USCIS guidance seeder)
- **Export**: `backend/app/export/` — markdown, pdf (ReportLab), docx (python-docx)
- **Routers**: `backend/app/routers/` — auth, onboarding, profiles, evidence, analyze, export, consent, data

## Key Frontend Paths

- **Pages**: `src/app/(public)/` (landing, login, register), `src/app/(dashboard)/` (all dashboard pages + onboarding)
- **Auth store**: `src/lib/` — Zustand useAuthStore, apiClient utility
- **Components**: `src/components/` — dashboard-sidebar, theme-provider, ui/ (shadcn)

## Key Domain Context

- EB-1A requires meeting 3 of 10 criteria (practically 4-5 in 2025-2026)
- October 2024 USCIS policy updates changed criteria interpretation
- Confidence scoring: 0.4 * data_confidence + 0.6 * criteria_match
- All outputs exportable as Markdown, PDF, DOCX
- Immigration disclaimer required in UI and exports
- Pathway switching has a 30-day cooldown

## Database Migrations

SQLAlchemy `create_all` only creates new tables. For adding columns to existing tables, `_run_migrations()` in `backend/app/main.py` runs on startup — checks `information_schema.columns` and issues `ALTER TABLE` if needed. Add new migrations there when adding columns to existing tables.

## Demo Personas (seeded via `python -m app.seed`)

| Email | Password | Persona | Pathway |
|-------|----------|---------|---------|
| priya@demo.com | demo1234 | Dr. Priya Sharma (AI researcher) | EB-1A |
| marco@demo.com | demo1234 | Marco Chen (senior SWE) | NIW |
| amara@demo.com | demo1234 | Amara Okafor (tech founder) | EB-1A |

## Deployment

- **Frontend**: Railway at `immigration-roadmap.com`
- **Backend**: Railway at `backend-production-95ea4.up.railway.app`
- **Database**: Railway PostgreSQL (internal networking)
- Auto-deploy on push to `main`. Use `railway up --detach` for manual backend deploys.

## Environment Variables

Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` for the AI pipeline to work. Database defaults work with docker-compose (port 5433). `FRONTEND_URL` must be set on Railway for CORS.
