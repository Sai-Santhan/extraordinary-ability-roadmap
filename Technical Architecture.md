# Technical Architecture Document

## Immigration Roadmap — AI-Powered Immigration Planning Tool

### Data Portability Hackathon | Track 3: Personal Data, Personal Value

### Team Size: 2 | Deadline: March 9, 2026

------

## 1. System Overview

### 1.1 One-Liner

An AI-powered extraordinary-ability roadmap that aggregates a user's scattered career data — CV, Google Scholar, GitHub, Google Takeout exports, ChatGPT conversation history, and LinkedIn PDF — into a unified, user-owned immigration profile, then generates a personalized, evidence-aligned plan to qualify faster for self-sponsored green-card paths like EB-1A, EB-1B, EB-1C, NIW, and O-1.

### 1.2 Hackathon Alignment

This project targets **Track 3: Personal Data, Personal Value** — "Build services that learn from a user's personal data to create something genuinely valuable for them."

The core thesis: immigrants' career achievements are fragmented across dozens of platforms and file formats. Google Scholar knows their publications. GitHub knows their open-source contributions. Gmail knows their conference invitations and judging requests. LinkedIn knows their roles and endorsements. ChatGPT export history may contain career brainstorming sessions. None of these platforms understand immigration law. Our tool bridges that gap — letting users aggregate their own data, process it through AI that understands USCIS criteria, and receive an actionable roadmap they own and can export.

### 1.3 Data Portability Principles

Every architectural decision is guided by DTI's data portability principles:

- **User-initiated**: Data only enters the system when the user explicitly provides it
- **PII redaction**: Contact-level PII (emails, phones, addresses, SSNs, DOBs) automatically scrubbed from database, uploaded files on disk, and before sending to AI — names and org names preserved for assessment accuracy
- **Transparent processing**: Users see exactly what the AI extracted and can correct it
- **Portable output**: All results export as open formats (Markdown, PDF, DOCX)
- **No lock-in**: The structured immigration profile follows an open JSON schema the user owns
- **Right to deletion**: One-click data purge removes all stored information
- **GDPR Article 20 aligned**: Structured, machine-readable output in commonly used formats

------

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 16.1.6) (pnpm)            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │Onboarding│ │ Evidence  │ │ Criteria │ │ Roadmap  │ │  Export  │ │
│  │(Custom)  │ │ Upload   │ │ Dashboard│ │ Planner  │ │  Center  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  UI: shadcn/ui (Base UI) + Tailwind | Charts: Recharts             │
│  Auth: Custom JWT + Zustand | State: React Query + Zustand         │
└────────────────────────────┬────────────────────────────────────────┘
                             │ REST API + Server-Sent Events (streaming)
┌────────────────────────────┴────────────────────────────────────────┐
│                        BACKEND (FastAPI + Python 3.13)              │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              AGENTIC PIPELINE (Orchestrator)                 │   │
│  │                                                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │ Ingestion│→ │Extraction│→ │Assessment│→ │ Roadmap  │  │   │
│  │  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │   │
│  │       ↓              ↓             ↓             ↓        │   │
│  │  [Parse files]  [Structure]  [Score vs    [Generate     ] │   │
│  │  [PDF, MBOX,   [into Pydantic  USCIS      time-phased   ] │   │
│  │   ICS, JSON]    schema]     criteria]    action plan]    ] │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ Prompt       │  │ Confidence   │  │ Data Portability Engine  │ │
│  │ Template     │  │ Scoring      │  │ (Import: CV, Takeout,    │ │
│  │ Library      │  │ Engine       │  │  ChatGPT, LinkedIn PDF,  │ │
│  └──────────────┘  └──────────────┘  │  Scholar, GitHub)        │ │
│                                       │ (Export: MD, PDF, DOCX)  │ │
│  ┌──────────────┐  ┌──────────────┐  └──────────────────────────┘ │
│  │ Claude API   │  │ ChromaDB     │                                │
│  │ (Structured  │  │ Vector DB    │                                │
│  │  Outputs)    │  │ (Legal RAG)  │                                │
│  └──────────────┘  └──────────────┘                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────────┐
│                        DATA LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ PostgreSQL   │  │ File Storage │  │ USCIS Knowledge Base     │ │
│  │ (Users,      │  │ (Uploaded    │  │ (Curated criteria defs,  │ │
│  │  Profiles,   │  │  docs, temp  │  │  Oct 2024 updates,       │ │
│  │  Evidence,   │  │  processing) │  │  Dhanasar framework —    │ │
│  │  Consents)   │  │              │  │  seeded into ChromaDB)   │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

------

## 3. Technology Stack

### 3.1 Frontend

| Component  | Choice                           | Rationale                                                    |
| ---------- | -------------------------------- | ------------------------------------------------------------ |
| Framework  | Next.js 16.1.6 (App Router)      | Turbopack default bundler, stable React Compiler             |
| UI Library | shadcn/ui (Base UI) + Tailwind CSS | Accessible components via `@base-ui/react`, `render` prop pattern (not Radix `asChild`) |
| Charts     | Recharts                         | Radar chart for criteria, bar/line for trends                |
| Auth       | Custom JWT + Zustand             | JWT stored in Zustand with localStorage persistence; SSE endpoints accept token as query parameter |
| State      | React Query + Zustand            | Server state caching + lightweight client state              |
| Streaming  | Server-Sent Events (EventSource) | Real-time analysis progress from backend                     |

### 3.2 Backend

| Component         | Choice                                                       | Rationale                                                    |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Framework         | FastAPI (Python 3.13)                                        | Async support, Pydantic v2 native validation, auto-generated OpenAPI docs |
| LLM               | Claude API (Sonnet 4.5) direct                               | Structured outputs, 200K context window, strong reasoning — no LangChain needed for sequential prompts |
| Structured Output | Anthropic Structured Outputs                                 | Guaranteed-valid JSON matching Pydantic schemas, eliminates parsing failures |
| RAG               | ChromaDB vector database                                     | Legal corpus (EB-1A/B/C, NIW, O-1 USCIS guidance) seeded at startup, queried by Assessment & Roadmap agents |
| CV Parsing        | PyMuPDF (`pymupdf4llm`)                                      | Fast PDF text extraction → Claude structured parsing         |
| Data Import       | Custom parsers for Google Takeout, ChatGPT export, LinkedIn PDF, images | MBOX (Gmail), ICS (Calendar), JSON (ChatGPT/Scholar), PDF (LinkedIn/CV), PNG/JPG (certificates) |
| Database          | PostgreSQL 16 + async SQLAlchemy                             | Relational data for users, profiles, evidence, consents      |
| Auth              | python-jose (JWT) + bcrypt                                   | Stateless JWT auth, 24h expiry                               |
| Export            | python-docx (DOCX), ReportLab (PDF), native (Markdown)      | Multiple portable formats                                    |
| Rate Limiting     | slowapi                                                      | Per-endpoint rate limits on auth and analysis                 |

### 3.3 Infrastructure

| Component       | Choice                                         | Rationale                                                    |
| --------------- | ---------------------------------------------- | ------------------------------------------------------------ |
| File Storage    | Local filesystem (hackathon) → S3 (production) | Uploaded documents, temp processing files                    |
| USCIS Knowledge | ChromaDB vector DB seeded from curated legal corpus | Criteria definitions, Oct 2024 policy updates, Dhanasar framework — queried via RAG at inference time |
| Deployment      | Railway (frontend + backend + PostgreSQL) | Fast deployment, auto-deploy from GitHub push                |

------

## 4. Data Portability Engine

### 4.1 Supported Import Sources

This is the core innovation aligned with the hackathon theme. The tool ingests career data from wherever users already store it.

#### Google Takeout Integration

Users export their Google data via Google Takeout and upload the archive:

- **Gmail (MBOX format)**: Parse for conference invitations, peer review requests, award notifications, media interview requests, speaking engagement confirmations. Use Claude to classify emails by immigration-relevant category.
- **Google Scholar**: Publication list, citation data (via Semantic Scholar API or JSON export).
- **Google Calendar (ICS format)**: Extract speaking engagements, conference attendance, committee meetings, judging sessions.

#### ChatGPT Export (JSON)

Users export their ChatGPT conversation history. Parse for:

- Career planning discussions (evidence of strategic thinking about professional development)
- Technical discussions that reveal domain expertise
- Writing assistance for publications or grant applications
- Immigration-related research conversations

#### LinkedIn PDF Export

Users download their LinkedIn profile as PDF. Extract:

- Employment history with titles, dates, company names
- Skills and endorsements
- Recommendations
- Education and certifications

#### Direct File Uploads

- **CV/Resume (PDF/DOCX)**: Primary career data source
- **Award certificates (PDF/images)**: Visual evidence via image parser
- **Media coverage (URLs/screenshots)**: Evidence for published material criterion

#### API Integrations (User-Linked)

- **Semantic Scholar**: User provides profile data → fetch h-index, citations, papers, co-authors
- **GitHub**: User provides username → fetch contributions, stars, PRs, review activity

### 4.2 Import Processing Pipeline

```
User provides data source (file upload or API link)
  │
  ├─→ [File Type Router] (backend/app/parsers/router.py)
  │     ├─ MBOX → mbox_parser.py (email classification via Claude)
  │     ├─ JSON → json_parser.py (ChatGPT export / Google Scholar)
  │     ├─ ICS  → ics_parser.py (calendar event extraction)
  │     ├─ PDF  → pdf_parser.py (PyMuPDF text extraction → Claude)
  │     ├─ IMG  → image_parser.py (PNG/JPG certificate extraction)
  │     └─ URL  → Semantic Scholar API / GitHub API
  │
  ├─→ [PII Scrubbing] (backend/app/services/pii_scrubber.py)
  │     Regex-based redaction of contact-level PII before storage and AI processing:
  │     - Email addresses → [EMAIL REDACTED]
  │     - Phone numbers → [PHONE REDACTED]
  │     - SSN/ID numbers → [ID REDACTED]
  │     - Physical addresses → [ADDRESS REDACTED]
  │     - Dates of birth → [DOB REDACTED]
  │     Names and organization names are preserved for assessment accuracy.
  │     Applied at: file upload (disk + DB), pipeline ingestion, mbox/image parsers.
  │
  ├─→ [Claude Structured Extraction]
  │     Input: PII-scrubbed raw text + Pydantic schema definition
  │     Output: Guaranteed-valid JSON matching ImmigrationProfile schema
  │     Mode: Anthropic Structured Outputs
  │
  ├─→ [Evidence Deduplication]
  │     Same publication found in CV + Scholar + Gmail invitation
  │     → Merge into single evidence record with multiple source confirmations
  │     → Higher data confidence when corroborated across sources
  │
  └─→ [Store in PostgreSQL]
        Structured evidence records linked to user profile
        Each record tagged with: source, extraction confidence, criterion mapping
```

### 4.3 Export Formats (Data Portability Output)

All outputs are user-owned and portable:

| Format       | Content                                                      | Use Case                                         |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------ |
| **Markdown** | Human-readable profile summary, criteria assessment, action plan | Personal records, version control, sharing       |
| **PDF**      | Polished report with assessment and roadmap                  | Attorney consultations, personal reference        |
| **DOCX**     | Editable document with all sections                          | Attorney markup, collaborative editing            |

The open JSON schema in `shared/schemas/` is designed so any immigration tool or attorney could consume the structured data — implementing GDPR Article 20's right to receive personal data in a structured, machine-readable format.

------

## 5. Agentic Pipeline Architecture

### 5.1 Four-Agent Sequential Pipeline

Each agent is a specialized step with its own prompt template, Pydantic input/output schema, and confidence scoring. Progress is streamed to the frontend via SSE.

#### Agent 1: Ingestion Agent

- **Input**: Raw uploaded files and API data
- **Processing**: File parsing via type-specific parsers (no LLM call), text extraction, data normalization
- **PII scrubbing**: Contact-level PII (emails, phones, addresses, SSNs, DOBs) is redacted from raw text before storage and before passing to the Extraction Agent. Names and organization names are preserved.
- **Output**: `RawCareerData` Pydantic model (unstructured text organized by source, PII-scrubbed)

#### Agent 2: Extraction Agent

- **Input**: `RawCareerData` (PII-scrubbed)
- **Processing**: Claude Structured Outputs extract immigration-relevant evidence into typed fields. Prompt includes PRIVACY instructions as defense-in-depth to ignore any residual PII.
- **Output**: `ImmigrationProfile` Pydantic model with typed evidence records (publications, awards, judging roles, etc.)

#### Agent 3: Assessment Agent

- **Input**: `ImmigrationProfile` + RAG context from ChromaDB legal corpus
- **Processing**: Claude scores each evidence item against specific EB-1A/EB-1B/EB-1C/NIW/O-1 criteria with calibrated confidence
- **Output**: `CriteriaAssessment` Pydantic model with per-criterion scores, confidence %, evidence mapping

#### Agent 4: Roadmap Agent

- **Input**: `CriteriaAssessment` + RAG context from ChromaDB legal corpus + user preferences
- **Processing**: Claude generates time-phased action plan weighted by gap severity and feasibility
- **Output**: `ImmigrationRoadmap` Pydantic model with quarterly milestones and specific actions

### 5.2 Streaming Architecture

The pipeline orchestrator (`backend/app/agents/pipeline.py`) runs all four agents sequentially and yields SSE events to the frontend:

```python
# Backend: FastAPI SSE endpoint
@router.get("/api/analyze/stream/{profile_id}")
async def stream_analysis(profile_id: str, token: str):
    # Token passed as query param (EventSource can't send headers)
    async def event_generator():
        yield {"event": "stage", "data": {"stage": "ingestion", "status": "started"}}
        # Agent 1: Ingestion (file parsing, no LLM)
        async for chunk in ingestion_agent.process(profile_id):
            yield {"event": "progress", "data": chunk}
        # Agent 2: Extraction (Claude Structured Outputs)
        # Agent 3: Assessment (Claude + ChromaDB RAG)
        # Agent 4: Roadmap (Claude + ChromaDB RAG)
    return EventSourceResponse(event_generator())
```

```typescript
// Frontend: React hook consuming SSE
const useAnalysisStream = (profileId: string) => {
  const token = useAuthStore((s) => s.token);
  useEffect(() => {
    const source = new EventSource(
      `/api/analyze/stream/${profileId}?token=${token}`
    );
    source.addEventListener("stage", (e) => setStage(JSON.parse(e.data)));
    source.addEventListener("progress", (e) =>
      setProgress((prev) => [...prev, JSON.parse(e.data)])
    );
    return () => source.close();
  }, [profileId, token]);
};
```

------

## 6. Data Models (Pydantic Schemas)

### 6.1 Core Immigration Profile

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import date

class ImmigrationTarget(str, Enum):
    EB1A = "eb1a"
    EB1B = "eb1b"
    EB1C = "eb1c"
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

class ConfidenceLevel(BaseModel):
    data_confidence: int = Field(ge=0, le=100)
    criteria_match: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)
    reasoning: str

class ImmigrationProfile(BaseModel):
    """Core schema — the portable, user-owned immigration profile."""
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
    github_stars: Optional[int] = None
    notable_repos: list[str] = []
    selective_memberships: list[str] = []
    compensation_percentile: Optional[str] = None
    data_sources: list[EvidenceSource] = []
```

Exported JSON schemas live in `shared/schemas/` (generated via `shared/generate_schemas.py`):
- `RawCareerData.json`
- `ImmigrationProfile.json`
- `CriteriaAssessment.json`
- `ImmigrationRoadmap.json`

------

## 7. Prompt Template Library

### 7.1 Architecture

```
backend/app/prompts/
├── extraction.py      # EXTRACTION_SYSTEM & EXTRACTION_USER prompts (includes PRIVACY instructions)
├── assessment.py      # ASSESSMENT_SYSTEM & ASSESSMENT_USER prompts
├── roadmap.py         # ROADMAP_SYSTEM & ROADMAP_USER prompts
└── shared.py          # CONFIDENCE_RUBRIC, THRESHOLD_GUIDANCE,
                       # PATHWAY_REGISTRY, PATHWAY_NOTES
```

Each agent has a system prompt (persona + criteria knowledge + calibration examples) and a user prompt template (profile data + instructions). The Extraction agent includes PRIVACY instructions as defense-in-depth to ignore any residual PII that wasn't caught by the regex scrubber. The Assessment and Roadmap agents augment their prompts with RAG context from the ChromaDB legal corpus.

### 7.2 Shared Constants

- **CONFIDENCE_RUBRIC**: Calibration anchors for consistent confidence scoring across runs
- **THRESHOLD_GUIDANCE**: Minimum scores per criterion strength level
- **PATHWAY_REGISTRY**: Maps pathway codes to display names (EB-1A, EB-1B, EB-1C, NIW, O-1)
- **PATHWAY_NOTES**: Per-pathway context injected into prompts

------

## 8. Synthetic Data Strategy

### 8.1 Purpose

For the hackathon demo, synthetic personas allow showcasing the tool's capabilities without requiring real immigration data (which is sensitive).

### 8.2 Demo Personas

Three pre-built synthetic personas in `synthetic-data/` with realistic career artifacts:

**Persona 1: Dr. Priya Sharma — AI Researcher**

- H-1B holder, India-born, 6 years in U.S.
- Target: EB-1A in 2 years
- Strong: 25 publications, h-index 15, 3 conference PC memberships
- Weak: No awards, no media coverage, no selective memberships
- Synthetic data: CV (PDF), Google Scholar (JSON), Gmail (MBOX), Calendar (ICS)

**Persona 2: Marco Chen — Senior Software Engineer**

- H-1B holder, China-born, 8 years in U.S.
- Target: EB-2 NIW in 3 years
- Strong: 500+ GitHub stars, 3 patents, critical role at FAANG
- Weak: No publications, no judging, limited visibility
- Synthetic data: CV (PDF), GitHub (JSON)

**Persona 3: Amara Okafor — Tech Founder**

- O-1 holder, Nigeria-born, 4 years in U.S.
- Target: EB-1A in 1 year (already strong profile)
- Strong: TechCrunch coverage, YC alum, speaking at 5 conferences, high compensation
- Weak: No scholarly publications, limited judging
- Synthetic data: CV (PDF), ChatGPT export (JSON), media URLs

Seeded via `python -m app.seed` (creates user accounts with `demo1234` password).

------

## 9. Authentication & Authorization

### 9.1 Stack

- **Backend**: python-jose (JWT creation/validation) + raw bcrypt (password hashing)
- **Frontend**: Zustand store (`useAuthStore`) with localStorage persistence
- **Session**: JWT strategy (stateless, 24h expiry)
- **SSE**: Token passed as query parameter (`?token=JWT`) since EventSource can't send headers

### 9.2 Authorization Model

```
Frontend (Next.js App Router)
  ├── Public routes: /, /login, /register
  ├── Protected routes: /dashboard/*, /onboarding
  │   → Zustand auth guard → redirect to /login if no token
  └── API calls: apiClient utility
      → Attaches JWT as Bearer token → FastAPI backend validates independently

Backend (FastAPI)
  ├── Auth endpoints: /api/auth/register, /api/auth/login
  ├── Protected endpoints: all /api/* except auth and health
  │   → Depends(get_current_user) → Extract user_id from JWT → Scope all DB queries
  └── Rate limiting: slowapi per-endpoint limits (e.g., 10/min for login, 5/min for register)
```

### 9.3 Privacy Features

- **PII redaction**: Contact-level PII (emails, phones, addresses, SSNs, DOBs) automatically scrubbed at three layers: (1) at file parse time (mbox headers, image parser prompt), (2) in the pipeline before DB storage and Claude API calls, (3) via extraction prompt instructions as defense-in-depth. Names and organization names are preserved for immigration assessment accuracy.
- **Data scope**: Every database query filtered by authenticated user_id
- **Consent tracking**: Per-source consent records via `/api/consent/` endpoints
- **Delete account**: Cascading deletion of all user data via `/api/data/delete`
- **Session timeout**: JWT expires after 24 hours
- **No cross-user data**: Zero shared state between users
- **Transparent AI disclosure**: UI clearly shows what data is sent to Claude API

------

## 10. Frontend Architecture

### 10.1 Route Structure

```
src/app/
├── (public)/
│   ├── page.tsx                # Landing page
│   ├── login/page.tsx
│   └── register/page.tsx
├── (dashboard)/
│   ├── layout.tsx              # Sidebar + header
│   ├── dashboard/
│   │   ├── page.tsx            # Dashboard home / profile overview
│   │   ├── evidence/page.tsx   # Evidence upload & management
│   │   ├── criteria/page.tsx   # Criteria radar chart + cards
│   │   ├── roadmap/page.tsx    # Timeline visualization
│   │   ├── export/page.tsx     # Export center (Markdown, PDF, DOCX)
│   │   └── settings/page.tsx   # Profile, pathway switching, data deletion
│   └── onboarding/page.tsx     # First-run 6-step guided setup
├── icon.svg                    # Branded compass-star favicon
├── opengraph-image.tsx         # Dynamic OG image (next/og ImageResponse)
└── layout.tsx                  # Root layout with metadata + ThemeProvider
```

### 10.2 Onboarding Flow

Custom 6-step wizard (not NextStepJS):

1. **Role selection** — researcher, engineer, executive, entrepreneur, other
2. **Field of expertise** — free text input
3. **Years of experience** — numeric input
4. **Qualifications checklist** — publications, managerial experience, multinational transfers, job offers, awards
5. **Current visa status** — H-1B, F-1/OPT, L-1, B-1/B-2, J-1, TN, none, other
6. **Results** — Pathway match scores with recommended pathway

### 10.3 Key Visualizations

**Criteria Radar Chart** — Centerpiece visualization showing criteria as axes with confidence-weighted scores. Color-coded by strength (green = strong, amber = moderate, red = weak).

**Additional displays**: Evidence completeness indicators, roadmap timeline with quarterly milestones, pathway comparison scores.

### 10.4 Pathway Switching

Users can switch their target pathway (EB-1A, EB-1B, EB-1C, NIW, O-1) from the Settings page. A **30-day cooldown** is enforced between switches. Switching sets `pathway_changed_since_analysis = true`, prompting re-analysis.

------

## 11. Confidence Scoring System

### 11.1 Three-Level Model

| Level                  | Measures                                          | Range  | Source                                                       |
| ---------------------- | ------------------------------------------------- | ------ | ------------------------------------------------------------ |
| **Data Confidence**    | How complete/reliable is the underlying evidence? | 0-100% | Computed from source type, corroboration across sources, documentation quality |
| **Criteria Match**     | How well does evidence match USCIS requirements?  | 0-100% | Assessed by Claude against calibrated examples + RAG legal context |
| **Overall Confidence** | Weighted combination                              | 0-100% | `0.4 * data + 0.6 * criteria_match` (criteria match weighted higher) |

### 11.2 Calibration

Defined in `backend/app/prompts/shared.py` (`CONFIDENCE_RUBRIC` and `THRESHOLD_GUIDANCE`) with calibrated examples per criterion per strength level. Injected into Assessment and Roadmap agent prompts to ensure consistent scoring across runs.

------

## 12. Security & Compliance

### 12.1 Data Handling

- **PII scrubbing**: Contact-level PII (emails, phones, addresses, SSNs, DOBs) is automatically redacted from uploaded files on disk, extracted text in the database, and raw career data before it reaches the Claude API. The PII scrubber (`backend/app/services/pii_scrubber.py`) uses regex-based detection. A migration script (`backend/app/migrations/scrub_existing_pii.py`) handles retroactive scrubbing of existing data.
- Uploaded files are scrubbed on disk after parsing (text/JSON overwritten with redacted content; PDFs converted to scrubbed `.txt`)
- Structured profiles stored in PostgreSQL, encrypted at rest (Railway managed)
- No data shared between users; all queries scoped to authenticated user
- Per-source consent tracking (users explicitly consent to each data source being processed)
- Clear UI disclosure: "Your data is sent to Anthropic's Claude API for analysis"

### 12.2 Disclaimers (Built into UI and Exports)

- "This tool is not legal advice and does not replace an immigration attorney."
- "AI assessments include confidence scores indicating uncertainty. Verify all findings with qualified counsel."
- "USCIS criteria interpretations are based on publicly available policy guidance as of [date]. Adjudication standards may change."

------

## 13. Backend API Endpoints

| Router      | Endpoints                                              | Purpose                                    |
| ----------- | ------------------------------------------------------ | ------------------------------------------ |
| `auth`      | POST `/api/auth/register`, `/api/auth/login`           | User registration and JWT issuance         |
| `onboarding`| POST `/api/onboarding/`                                | Pathway recommendation from questionnaire  |
| `profiles`  | GET/PATCH `/api/profiles/{id}`                         | Profile CRUD, pathway switching             |
| `evidence`  | POST `/api/evidence/upload`                            | Multipart file upload                       |
| `analyze`   | GET `/api/analyze/stream/{profile_id}?token=JWT`       | SSE pipeline streaming                      |
| `export`    | GET `/api/export/{profile_id}/{format}`                | Generate Markdown/PDF/DOCX                  |
| `consent`   | GET/POST `/api/consent/`                               | Per-source consent tracking                 |
| `data`      | DELETE `/api/data/`                                    | Full data deletion (GDPR/CCPA)              |
| `health`    | GET `/api/health`, `/api/health/db`                    | Liveness + database connectivity check      |

------

## 14. RAG: Legal Corpus & Vector Database

The Assessment and Roadmap agents use **Retrieval-Augmented Generation** to ground their outputs in actual USCIS guidance:

- **Vector DB**: ChromaDB (embedded, no external service)
- **Corpus**: Curated immigration law text covering EB-1A, EB-1B, EB-1C, NIW, and O-1 criteria definitions, October 2024 USCIS policy updates, the Dhanasar framework, and visa bulletin context
- **Seeding**: `backend/app/services/legal_corpus.py` seeds the corpus at startup
- **Querying**: `backend/app/services/vector_db.py` provides the RAG query interface
- **Usage**: Assessment and Roadmap agents query relevant legal context before generating their Claude API calls

------

## 15. Database Schema

### Core Tables

| Table                  | Key Columns                                                                 |
| ---------------------- | --------------------------------------------------------------------------- |
| `users`                | id (UUID), email, hashed_password, name, onboarding_completed, onboarding_data |
| `immigration_profiles` | id, user_id (FK), profile_data (JSON), raw_career_data (JSON), assessment_data (JSON), roadmap_data (JSON), target_pathway, status, pathway_changed_since_analysis |
| `evidence_files`       | id, profile_id (FK), filename, file_type, source_type, file_path, extracted_text |
| `data_consents`        | id, user_id (FK), source_type, consent_given, consent_timestamp, revoked_at |

### Migrations

SQLAlchemy `create_all` handles new tables. For existing tables, a startup migration in `backend/app/main.py` (`_run_migrations()`) checks `information_schema.columns` and adds missing columns via `ALTER TABLE`.

------

## 16. Deployment

| Service  | Platform | URL                                              |
| -------- | -------- | ------------------------------------------------ |
| Frontend | Railway  | `https://immigration-roadmap.com`                |
| Backend  | Railway  | `https://backend-production-95ea4.up.railway.app`|
| Database | Railway  | PostgreSQL 16 (internal networking)              |

Auto-deploy on push to `main` branch. Backend uses `railway up` for manual deploys when needed.
