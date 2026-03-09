# Immigration Empowerment Through Data Portability

**AI-powered immigration roadmap that turns your scattered career data into a personalized strategy for EB-1A, EB-1B, EB-1C, NIW, and O-1 visa pathways.**

[![Data Portability Hackathon](https://img.shields.io/badge/DTI%20Hackathon-Track%203-blue)](https://www.dataportability.dev)
[![Built with Claude](https://img.shields.io/badge/Built%20with-Claude%20API-orange)](https://anthropic.com)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.13-009688)](https://fastapi.tiangolo.com)

---

## The Problem

Immigrants pursuing extraordinary ability visas (EB-1A, EB-1B, EB-1C, NIW, O-1) face a fragmented evidence landscape. Their career achievements are scattered across dozens of platforms:

- **Google Scholar** knows their publications
- **GitHub** knows their open-source contributions
- **Gmail** knows their conference invitations and peer review requests
- **LinkedIn** knows their roles and endorsements
- **ChatGPT exports** may contain career planning conversations

**None of these platforms understand immigration law.** Applicants spend months manually mapping their achievements to USCIS criteria, often missing evidence they already have or misunderstanding what counts.

## The Solution

This tool bridges the gap — letting users **aggregate their own data**, process it through **AI that understands USCIS criteria**, and receive an **actionable, time-phased roadmap** they own and can export.

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
```

Each stage uses Claude API with **structured outputs** to guarantee valid, typed results — streamed to the frontend in real time via SSE.

### Key Features

- **Multi-source data import** — CV/resume, Google Scholar, GitHub, Google Takeout (Gmail, Calendar), ChatGPT exports, LinkedIn PDF, images
- **AI criteria assessment** — Scores evidence against EB-1A/EB-1B/EB-1C/NIW/O-1 criteria with calibrated confidence percentages, grounded by RAG over curated USCIS legal corpus
- **Interactive radar chart** — Visual dashboard mapping your strengths and gaps across USCIS criteria
- **Personalized roadmap** — Quarterly action plan telling you *exactly* what to do and which criterion each action strengthens
- **Full data portability** — Export everything as Markdown, PDF, or DOCX — your immigration profile is yours
- **Guided onboarding** — 6-step wizard recommending the best pathway based on your background
- **Pathway switching** — Change target pathway anytime (30-day cooldown between switches)
- **Privacy-first** — Contact-level PII (emails, phones, addresses, SSNs, DOBs) automatically redacted from stored data and before AI processing. Per-source consent tracking, all data scoped to your account, one-click deletion, transparent AI disclosure

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
├── frontend/          Next.js 16 App Router + shadcn/ui (Base UI) + Tailwind + Zustand
├── backend/           FastAPI + async SQLAlchemy + Pydantic v2 + Claude API + ChromaDB
├── shared/            JSON schemas for data portability (exported from Pydantic models)
└── synthetic-data/    Demo files for seeded personas (CV, Gmail, Scholar, ChatGPT, GitHub)
```

### Frontend

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16.1.6 (App Router, Turbopack) |
| UI Components | shadcn/ui (Base UI, `render` prop — not Radix `asChild`) + Tailwind CSS |
| Charts | Recharts |
| State | Zustand (client) + React Query (server) |
| Auth | Custom JWT stored in Zustand with localStorage |
| Streaming | EventSource (SSE) |
| Theming | Custom ThemeProvider with light/dark mode |

### Backend

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (async, Python 3.13) |
| AI | Claude API (Sonnet 4.5) with Structured Outputs |
| RAG | ChromaDB vector DB with curated USCIS legal corpus |
| ORM | async SQLAlchemy + Pydantic v2 |
| Database | PostgreSQL 16 |
| Auth | python-jose (JWT) + bcrypt |
| Parsing | PyMuPDF (PDF), custom parsers (MBOX, ICS, JSON, LinkedIn PDF, images) |
| Export | python-docx (DOCX), ReportLab (PDF), native (Markdown) |
| Rate Limiting | slowapi |

### Agentic Pipeline

Four sequential agents, each a Claude API call with Pydantic structured output:

1. **Ingestion Agent** — Parses uploaded files (PDF, DOCX, MBOX, ICS, JSON, images) into `RawCareerData` (no LLM call). Contact-level PII is scrubbed before storage.
2. **Extraction Agent** — Uses Claude Structured Outputs to extract typed evidence into `ImmigrationProfile`. Input is PII-scrubbed; prompt instructs Claude to ignore any residual PII.
3. **Assessment Agent** — Scores evidence against USCIS criteria with calibrated confidence + RAG legal context → `CriteriaAssessment`
4. **Roadmap Agent** — Generates time-phased action plan weighted by gap severity + RAG legal context → `ImmigrationRoadmap`

Progress is streamed to the frontend via SSE at `GET /api/analyze/stream/{profile_id}?token=JWT`.

---

## Data Portability

This project is built for **[DTI's Data Portability Hackathon — Track 3: Personal Data, Personal Value](https://www.dataportability.dev)**.

Every architectural decision follows data portability principles:

| Principle | Implementation |
|-----------|---------------|
| **User-initiated** | Data only enters the system when the user explicitly provides it |
| **PII redaction** | Contact-level PII (emails, phones, addresses, SSNs, DOBs) automatically scrubbed from database, uploaded files on disk, and before sending to AI — names and org names preserved for assessment accuracy |
| **Transparent processing** | Users see exactly what the AI extracted and can correct it |
| **Portable output** | All results export as open formats (Markdown, PDF, DOCX) |
| **No lock-in** | The structured immigration profile follows an open JSON schema the user owns |
| **Right to deletion** | One-click data purge via `/api/data/delete` removes all stored information |
| **Consent tracking** | Per-source consent records — users control which data sources are processed |
| **GDPR Article 20** | Structured, machine-readable output in commonly used formats |

### Supported Import Sources

| Source | Format | What It Provides |
|--------|--------|-----------------|
| CV / Resume | PDF, DOCX | Employment history, education, skills, achievements |
| Google Scholar | JSON | Publications, citations, h-index, co-authors |
| GitHub | JSON | Contributions, stars, PRs, review activity |
| Google Takeout | MBOX, ICS, JSON | Conference invitations, peer review requests, calendar events |
| ChatGPT Export | JSON | Career planning discussions, domain expertise evidence |
| LinkedIn | PDF | Roles, endorsements, recommendations, certifications |
| Certificates | PNG, JPG | Award and certificate images |

### Export Formats

| Format | Use Case |
|--------|----------|
| **Markdown** | Human-readable summary for personal records |
| **PDF** | Polished report for attorney consultations |
| **DOCX** | Editable document for collaborative review |

---

## Domain Context

### Immigration Pathways

- **EB-1A (Extraordinary Ability)** — Requires meeting 3 of 10 criteria (practically 4-5 in 2025-2026 given declining approval rates)
- **EB-1B (Outstanding Professor/Researcher)** — For outstanding professors/researchers with a qualifying permanent job offer; employer sponsorship required
- **EB-1C (Multinational Manager/Executive)** — For multinational managers/executives transferred within a corporate group
- **EB-2 NIW (National Interest Waiver)** — Dhanasar 3-prong framework: national importance, well-positioned, benefit outweighs labor cert
- **O-1 (Extraordinary Ability)** — Similar criteria to EB-1A, nonimmigrant visa

### Confidence Scoring

Each evidence item receives a three-level confidence score:

```
Overall = 0.4 × Data Confidence + 0.6 × Criteria Match
```

- **Data Confidence** (0–100%) — How reliable is the source? Corroboration across multiple sources increases confidence.
- **Criteria Match** (0–100%) — How well does the evidence satisfy USCIS requirements? Calibrated against real examples via RAG legal corpus.

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

## Disclaimer

> **This tool is not legal advice and does not replace an immigration attorney.** AI assessments include confidence scores indicating uncertainty. Verify all findings with qualified counsel. USCIS criteria interpretations are based on publicly available policy guidance and may change.

---

## License

Built for the [Data Portability Hackathon](https://www.dataportability.dev) by a team of 2.
