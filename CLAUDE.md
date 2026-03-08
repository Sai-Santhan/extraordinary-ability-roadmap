# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered immigration roadmap tool for the **Data Portability Hackathon (Track 3: Personal Data, Personal Value)**. Aggregates scattered career data (CV, Google Scholar, GitHub, Google Takeout, ChatGPT exports, LinkedIn PDF) into a unified immigration profile, scores evidence against EB-1A/NIW/O-1 criteria, and generates a personalized multi-year roadmap.

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

**Backend**: FastAPI + async SQLAlchemy + Pydantic v2 + Claude API (Sonnet 4.5 Structured Outputs) + PostgreSQL 16

**Auth**: JWT-based (python-jose + raw bcrypt). Token stored in Zustand with localStorage persistence. SSE endpoints accept token as query parameter (EventSource can't send headers).

**Important**: shadcn/ui uses Base UI (`@base-ui/react`), NOT Radix. Use `render` prop instead of `asChild` for component composition (e.g., `<DialogTrigger render={<Button />}>` not `<DialogTrigger asChild>`).

## Agentic Pipeline

Four sequential agents, each a Claude API call with Pydantic structured output:
1. **Ingestion Agent** — file parsing, text extraction → `RawCareerData`
2. **Extraction Agent** — Claude Structured Outputs → `ImmigrationProfile`
3. **Assessment Agent** — scores evidence vs USCIS criteria → `CriteriaAssessment`
4. **Roadmap Agent** — generates time-phased action plan → `ImmigrationRoadmap`

Progress streamed to frontend via SSE at `GET /api/analyze/stream/{profile_id}?token=JWT`.

## Key Domain Context

- EB-1A requires meeting 3 of 10 criteria (practically 4-5 in 2025-2026)
- October 2024 USCIS policy updates changed criteria interpretation
- Confidence scoring: 0.4 * data_confidence + 0.6 * criteria_match
- All outputs exportable as JSON, Markdown, PDF, DOCX
- Immigration disclaimer required in UI and exports

## Demo Personas (seeded via `python -m app.seed`)

| Email | Password | Persona | Pathway |
|-------|----------|---------|---------|
| priya@demo.com | demo1234 | Dr. Priya Sharma (AI researcher) | EB-1A |
| marco@demo.com | demo1234 | Marco Chen (senior SWE) | NIW |
| amara@demo.com | demo1234 | Amara Okafor (tech founder) | EB-1A |

## Environment Variables

Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` for the AI pipeline to work. Database defaults work with docker-compose (port 5433).
