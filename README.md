# Immigration Empowerment Through Data Portability

**AI-powered immigration roadmap that turns your scattered career data into a personalized strategy for EB-1A, EB-1B, EB-1C, NIW, and O-1 visa pathways.**

[![Data Portability Hackathon](https://img.shields.io/badge/DTI%20Hackathon-Track%203-blue)](https://www.dataportability.dev)
[![Built with Claude](https://img.shields.io/badge/Built%20with-Claude%20API-orange)](https://anthropic.com)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.13-009688)](https://fastapi.tiangolo.com)

---

## The Problem

**1.8 million skilled immigrants** are stuck in the U.S. green card backlog. An Indian-born applicant filing EB-2 today faces an estimated **134-year wait**. Self-sponsored paths like EB-1A and NIW exist — they're faster and don't require employer sponsorship — but the criteria are opaque and strategic planning costs **$5,000–$15,000** in attorney consultations.

Meanwhile, immigrants' career achievements are scattered across dozens of platforms:

- **Google Scholar** knows their publications and citations
- **GitHub** knows their open-source contributions and code reviews
- **Gmail** knows their conference invitations and peer review requests
- **LinkedIn** knows their roles and endorsements
- **ChatGPT exports** may contain career planning conversations

**None of these platforms understand immigration law.** Applicants spend months manually mapping their achievements to USCIS criteria, often missing evidence they already have.

## The Solution

This tool bridges the gap — letting users **aggregate their own career data**, process it through **AI that understands USCIS criteria** (augmented with a RAG knowledge base of curated legal guidance), and receive an **actionable, time-phased roadmap** they fully own and can export.

### How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. INGEST   │ ──→ │  2. EXTRACT  │ ──→ │  3. ASSESS   │ ──→ │  4. ROADMAP  │
│              │     │              │     │              │     │              │
│ Parse CV,    │     │ Structure    │     │ Score against│     │ Generate     │
│ Scholar,     │     │ into typed   │     │ USCIS        │     │ quarterly    │
│ GitHub,      │     │ evidence     │     │ criteria     │     │ action plan  │
│ Takeout      │     │ records      │     │ with AI+RAG  │     │ with gaps    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
     PII scrubbed          Claude              ChromaDB              Claude
     before storage     Structured           legal corpus         Structured
                         Outputs              augmented             Outputs
```

Each stage uses Claude API with **Anthropic Structured Outputs** to guarantee valid, typed results — streamed to the frontend in real time via Server-Sent Events.

### Key Features

- **Multi-source data import** — CV/resume, Google Scholar, GitHub, Google Takeout (Gmail MBOX, Calendar ICS), ChatGPT exports, LinkedIn, certificate images (via Claude Vision)
- **5 immigration pathways** — EB-1A (10 criteria), EB-1B (6 criteria), EB-1C (5 criteria), NIW/Dhanasar (3 prongs), O-1 (8 criteria)
- **RAG-augmented assessment** — Evidence scored against USCIS criteria using ChromaDB vector store seeded with curated legal guidance, Oct 2024 policy updates, and Dhanasar framework
- **Calibrated confidence scoring** — Three-level model (data confidence, criteria match, weighted overall) with anchored calibration examples in every prompt
- **Interactive radar chart** — Visual dashboard mapping strengths and gaps across all pathway criteria
- **Personalized roadmap** — Quarterly action plan with effort/impact levels, specific opportunities (named conferences, journals, programs), and target criterion mapping
- **Full data portability** — Export everything as JSON, Markdown, PDF, or DOCX
- **Guided onboarding** — 6-step wizard that recommends the best pathway based on your background
- **Privacy-first architecture** — Contact-level PII (emails, phones, SSNs, DOBs, addresses) automatically scrubbed before AI processing; per-source consent tracking; all data scoped to authenticated user; one-click deletion (full account or data-only); prompt injection detection

---

## Live Demo

- **Frontend**: [immigration-roadmap.com](https://immigration-roadmap.com)
- **Backend API**: [backend-production-95ea4.up.railway.app](https://backend-production-95ea4.up.railway.app/api/health)

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (for PostgreSQL)
- [Node.js 22+](https://nodejs.org/) with [pnpm](https://pnpm.io/)
- [Python 3.13+](https://www.python.org/) with [uv](https://docs.astral.sh/uv/)
- [Anthropic API key](https://console.anthropic.com/)

### 1. Clone & configure

```bash
git clone https://github.com/Sai-Santhan/extraordinary-ability-roadmap.git
cd immigration-empowerment-through-data-portability
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

### 2. Start the database

```bash
docker compose up -d
```

### 3. Start the backend

```bash
cd backend
uv sync                   # Create venv and install deps
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 4. Start the frontend

```bash
cd frontend
pnpm install
pnpm dev                  # Opens on http://localhost:3000
```

### 5. (Optional) Seed demo data

```bash
cd backend
python -m app.seed
```

This creates three demo personas you can log in with immediately:

| Email | Password | Persona | Target Pathway |
|-------|----------|---------|----------------|
| `priya@demo.com` | `demo1234` | Dr. Priya Sharma — AI researcher, 25 publications, h-index 15 | EB-1A |
| `marco@demo.com` | `demo1234` | Marco Chen — Senior SWE, 500+ GitHub stars, 3 patents | NIW |
| `amara@demo.com` | `demo1234` | Amara Okafor — Tech founder, YC alum, TechCrunch coverage | EB-1A |

---

## Architecture

```
immigration-empowerment-through-data-portability/
├── frontend/          Next.js 16 App Router + shadcn/ui (Base UI) + Tailwind v4 + Zustand
├── backend/           FastAPI + async SQLAlchemy + Pydantic v2 + Claude API + ChromaDB
├── shared/            JSON schemas for data portability (exported from Pydantic models)
└── synthetic-data/    Demo files for seeded personas (CV, Gmail, Scholar, ChatGPT, GitHub)
```

### Frontend

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16.1.6 (App Router, Turbopack) |
| UI Components | shadcn/ui (Base UI `@base-ui/react` 1.2.0, `render` prop — not Radix `asChild`) |
| Styling | Tailwind CSS v4 |
| Charts | Recharts 2.15.4 |
| Animations | Framer Motion 12.35.1 |
| State | Zustand 5.0.11 (client) + React Query 5.90.21 (server) |
| Auth | Custom JWT stored in Zustand with localStorage persistence |
| Streaming | EventSource (SSE) — token passed as query param |
| Theming | next-themes (light/dark mode) |
| Toasts | Sonner 2.0.7 |

### Backend

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (fully async, Python 3.13) |
| AI | Claude Sonnet 4.5 with Anthropic Structured Outputs (`anthropic` >=0.52.0) |
| RAG | ChromaDB >=0.5.0 — seeded with curated USCIS legal corpus on startup |
| ORM | async SQLAlchemy 2.0 + asyncpg + Pydantic v2 |
| Database | PostgreSQL 16 (Docker, port 5433) |
| Auth | python-jose (JWT) + passlib[bcrypt] |
| PII Protection | Custom scrubber — redacts emails, phones, SSNs, DOBs, addresses |
| Parsing | PyMuPDF (PDF), Claude Vision (images), custom parsers (MBOX, ICS, JSON, LinkedIn) |
| Export | python-docx (DOCX), ReportLab (PDF), native (JSON, Markdown) |
| Rate Limiting | slowapi (1 analysis/week, 1 pathway switch/month) |
| Streaming | sse-starlette (Server-Sent Events) |

### Agentic Pipeline

Four sequential agents, each a Claude API call with Pydantic structured output:

1. **Ingestion Agent** — Parses uploaded files (PDF, MBOX, ICS, JSON, images) via type-specific parsers into `RawCareerData`. No LLM call. Contact-level PII is scrubbed before storage.
2. **Extraction Agent** — Uses Claude Structured Outputs to extract typed evidence into `ImmigrationProfile`. Input is PII-scrubbed.
3. **Assessment Agent** — Scores evidence against USCIS criteria with calibrated confidence. Augmented with ChromaDB RAG (5 relevant legal passages per pathway). Outputs `CriteriaAssessment`.
4. **Roadmap Agent** — Generates time-phased action plan weighted by gap severity and feasibility. RAG-augmented. Outputs `ImmigrationRoadmap`.

Progress is streamed to the frontend via SSE at `GET /api/analyze/stream/{profile_id}?token=JWT`.

---

## Data Portability

This project is built for **[DTI's Data Portability Hackathon — Track 3: Personal Data, Personal Value](https://www.dataportability.dev)**.

Every architectural decision follows data portability principles:

| Principle | Implementation |
|-----------|---------------|
| **User-initiated** | Data only enters the system when the user explicitly provides it |
| **Per-source consent** | DataConsent table tracks explicit consent for each data source type |
| **PII redaction** | Contact-level PII (emails, phones, SSNs, DOBs, addresses) automatically scrubbed from database, uploaded files, and before AI processing — names and org names preserved for assessment accuracy |
| **Transparent processing** | Users see exactly what the AI extracted; confidence scores explain reasoning |
| **Portable output** | All results export as JSON, Markdown, PDF, DOCX |
| **No lock-in** | The structured immigration profile follows an open JSON schema the user owns |
| **Right to deletion** | One-click data purge — full account deletion or data-only deletion |
| **GDPR Article 20** | Structured, machine-readable output in commonly used formats |

### Supported Import Sources

| Source | Format | What It Provides |
|--------|--------|-----------------|
| CV / Resume | PDF, text | Employment history, education, skills, achievements |
| Google Scholar | JSON | Publications, citations, h-index, co-authors |
| GitHub | JSON | Contributions, stars, PRs, review activity |
| Google Takeout — Gmail | MBOX | Conference invitations, peer review requests, award notifications |
| Google Takeout — Calendar | ICS | Speaking engagements, conference attendance, committee meetings |
| ChatGPT Export | JSON | Career planning discussions, domain expertise evidence |
| LinkedIn | PDF, text | Roles, endorsements, recommendations, certifications |
| Certificates / Awards | PNG, JPG | Award certificates, recommendation letters (via Claude Vision) |

### Export Formats

| Format | Use Case |
|--------|----------|
| **JSON** | Machine-readable, portable to other tools, attorney software |
| **Markdown** | Human-readable summary for personal records |
| **PDF** | Polished report for attorney consultations |
| **DOCX** | Editable document for collaborative review |

---

## Domain Context

### Immigration Pathways Supported

| Pathway | Criteria | Key Requirement |
|---------|----------|----------------|
| **EB-1A** (Extraordinary Ability) | 3 of 10 criteria (practically 4-5 in 2025-2026) | Self-petitioned, no employer needed |
| **EB-1B** (Outstanding Researcher) | 2 of 6 criteria | Employer-sponsored, academic/research focus |
| **EB-1C** (Multinational Manager) | Organizational/managerial criteria | Intracompany transfer |
| **NIW** (National Interest Waiver) | Dhanasar 3-prong test | Self-petitioned, national importance |
| **O-1** (Extraordinary Ability Visa) | 3 of 8 criteria | Nonimmigrant, employer/agent sponsor |

### Confidence Scoring

Each evidence item receives a three-level confidence score:

```
Overall = 0.4 × Data Confidence + 0.6 × Criteria Match
```

- **Data Confidence** (0–100%) — How reliable is the source? Corroboration across multiple sources increases confidence.
- **Criteria Match** (0–100%) — How well does the evidence satisfy USCIS requirements? Calibrated against anchored examples via RAG legal corpus.

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Get current user info |

### Core Pipeline
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/onboarding/` | Onboarding wizard + pathway recommendation |
| GET/POST | `/api/profiles/` | CRUD immigration profiles |
| PATCH | `/api/profiles/{id}/pathway` | Switch pathway (30-day cooldown) |
| POST | `/api/evidence/upload` | Upload evidence files |
| GET | `/api/evidence/{id}` | List evidence for profile |
| POST | `/api/analyze/token/{id}` | Get SSE auth token |
| GET | `/api/analyze/stream/{id}?token=JWT` | SSE stream for pipeline |
| GET | `/api/export/{id}?format=json\|markdown\|pdf\|docx` | Export profile |

### Privacy & Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/consent/` | Per-source consent tracking |
| DELETE | `/api/data/me` | Full account deletion |
| DELETE | `/api/data/me/data-only` | Delete data, keep account |

---

## Running Tests

```bash
cd backend
.venv/bin/python -m pytest tests/ -v    # Uses SQLite in-memory — no Docker needed
```

---

## Environment Variables

Create `.env` from the example:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (async) | `postgresql+asyncpg://immigration:immigration_dev@localhost:5433/immigration_roadmap` |
| `ANTHROPIC_API_KEY` | Claude API key for the agentic pipeline | *(required)* |
| `NEXTAUTH_SECRET` | JWT signing secret | `change-me-in-production` |
| `BACKEND_URL` | Backend API URL | `http://localhost:8000` |
| `FRONTEND_URL` | Frontend URL (for CORS) | `http://localhost:3000` |

---

## Deployment

| Component | Platform | URL |
|-----------|----------|-----|
| Frontend | Railway | [immigration-roadmap.com](https://immigration-roadmap.com) |
| Backend  | Railway | [backend-production-95ea4.up.railway.app](https://backend-production-95ea4.up.railway.app) |
| Database | Railway PostgreSQL | Internal networking |

Auto-deploy on push to `main`. Manual backend deploy: `railway up --detach`.

---

## Disclaimer

> **This tool is not legal advice and does not replace an immigration attorney.** AI assessments include confidence scores indicating uncertainty. Verify all findings with qualified counsel. USCIS criteria interpretations are based on publicly available policy guidance and may change.

---

## License

Built for the [Data Portability Hackathon](https://www.dataportability.dev) by a team of 2.
