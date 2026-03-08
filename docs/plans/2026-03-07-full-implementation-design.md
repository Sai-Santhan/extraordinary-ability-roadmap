# Full Implementation Design

## Date: 2026-03-07 | Deadline: 2026-03-09

## Decisions

- **Monorepo**: `frontend/`, `backend/`, `shared/` at root
- **Database**: PostgreSQL via Docker
- **Auth**: NextAuth.js v5 credentials provider (email/password), with explicit data consent flows
- **LLM**: Claude Sonnet 4.5 for all 4 agents via Structured Outputs
- **Synthetic data**: Generate actual files (CV PDFs, MBOX, ICS, JSON) for 3 personas
- **Frontend**: Next.js 16 + shadcn/ui + Tailwind + React Query + Zustand + NextStepJS + shadcn Charts
- **Backend**: FastAPI + Pydantic v2 + SQLAlchemy async + PostgreSQL

## Architecture

```
root/
├── frontend/              # Next.js 16 (pnpm)
│   ├── app/
│   │   ├── (public)/      # Landing, login, register
│   │   ├── (dashboard)/   # Evidence, criteria, roadmap, export, chat
│   │   └── onboarding/    # NextStepJS guided setup
│   ├── components/
│   ├── lib/
│   └── prisma/
├── backend/               # FastAPI (uv/pip)
│   ├── app/
│   │   ├── agents/        # 4-agent pipeline
│   │   ├── parsers/       # File format parsers
│   │   ├── prompts/       # Claude prompt templates
│   │   ├── models/        # SQLAlchemy + Pydantic models
│   │   └── routers/       # API endpoints
│   └── tests/
├── shared/                # JSON schemas + TS type generation
│   ├── schemas/
│   └── generate-types.ts
├── synthetic-data/        # Demo persona files
│   ├── priya-sharma/
│   ├── marco-chen/
│   └── amara-okafor/
└── docker-compose.yml     # PostgreSQL + services
```

## Data Consent Flow

1. User uploads file or links API
2. Consent modal appears: lists data types, processing steps, Claude API disclosure
3. User explicitly consents per data source
4. Consent record stored with timestamp
5. Processing begins only after consent
6. All consent viewable/revocable in settings

## Agentic Pipeline

Ingestion -> Extraction -> Assessment -> Roadmap

Each agent: Claude Sonnet 4.5 + Structured Outputs beta + Pydantic schema
Progress streamed via SSE to frontend

## Synthetic Personas

| Persona | Pathway | Files |
|---------|---------|-------|
| Dr. Priya Sharma | EB-1A | CV PDF, Scholar JSON, Gmail MBOX, Calendar ICS |
| Marco Chen | NIW | CV PDF, GitHub JSON, LinkedIn PDF, Google Takeout |
| Amara Okafor | EB-1A | CV PDF, LinkedIn PDF, ChatGPT JSON, media URLs |
