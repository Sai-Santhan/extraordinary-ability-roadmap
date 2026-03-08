# Technical Architecture Document

## [Project Name TBD] — AI-Powered Immigration Roadmap Tool

### Data Portability Hackathon | Track 3: Personal Data, Personal Value

### Team Size: 2 | Status: Building Stage | Deadline: March 9, 2026

------

## 1. System Overview

### 1.1 One-Liner

An AI-powered extraordinary-ability roadmap that aggregates a user's scattered career data — CV, Google Scholar, GitHub, Google Takeout exports, ChatGPT conversation history, and emails — into a unified, user-owned immigration profile, then generates a personalized, evidence-aligned plan to qualify faster for self-sponsored green-card paths like EB-1A and NIW.

### 1.2 Hackathon Alignment

This project targets **Track 3: Personal Data, Personal Value** — "Build services that learn from a user's personal data to create something genuinely valuable for them."

The core thesis: immigrants' career achievements are fragmented across dozens of platforms and file formats. Google Scholar knows their publications. GitHub knows their open-source contributions. Gmail knows their conference invitations and judging requests. LinkedIn knows their roles and endorsements. ChatGPT export history may contain career brainstorming sessions. None of these platforms understand immigration law. Our tool bridges that gap — letting users aggregate their own data, process it through AI that understands USCIS criteria, and receive an actionable roadmap they own and can export.

### 1.3 Data Portability Principles

Every architectural decision is guided by DTI's data portability principles:

- **User-initiated**: Data only enters the system when the user explicitly provides it
- **Transparent processing**: Users see exactly what the AI extracted and can correct it
- **Portable output**: All results export as open formats (JSON, Markdown, PDF, DOCX)
- **No lock-in**: The structured immigration profile follows an open schema the user owns
- **Right to deletion**: One-click data purge removes all stored information
- **GDPR Article 20 aligned**: Structured, machine-readable output in commonly used formats

------

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 16.1.6) (pnpm)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │Onboarding│ │ Evidence  │ │ Criteria │ │ Roadmap  │ │  Export  │ │
│  │(NextStep)│ │ Upload   │ │ Dashboard│ │ Planner  │ │  Center  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  UI: shadcn/ui + Tailwind | Charts: shadcn Charts (Recharts)       │
│  Auth: NextAuth.js v5  (Auth.js) | State: React Query + Zustand    │
└────────────────────────────┬────────────────────────────────────────┘
                             │ REST API + Server-Sent Events (streaming)
┌────────────────────────────┴────────────────────────────────────────┐
│                        BACKEND (FastAPI + Python)                    │
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
│  │  [Takeout/     [into Pydantic  USCIS      time-phased   ] │   │
│  │   exports]      schema]     criteria]    action plan]    ] │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ Prompt       │  │ Confidence   │  │ Data Portability Engine  │ │
│  │ Template     │  │ Scoring      │  │ (Import: Takeout, CSV,   │ │
│  │ Library v1.0 │  │ Engine       │  │  ChatGPT, LinkedIn PDF)  │ │
│  └──────────────┘  └──────────────┘  │ (Export: JSON, MD, DOCX, │ │
│                                       │  PDF)                    │ │
│  ┌──────────────┐  ┌──────────────┐  └──────────────────────────┘ │
│  │ Claude API   │  │ Semantic     │                                │
│  │ (Structured  │  │ Scholar API  │  ┌──────────────────────────┐ │
│  │  Outputs)    │  │ + GitHub API │  │ MCP Server (optional)    │ │
│  └──────────────┘  └──────────────┘  │ Visa bulletins, policy   │ │
│                                       └──────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────────┐
│                        DATA LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ PostgreSQL   │  │ File Storage │  │ USCIS Knowledge Base     │ │
│  │ (Users,      │  │ (Uploaded    │  │ (Curated criteria defs,  │ │
│  │  Profiles,   │  │  docs, temp  │  │  Oct 2024 updates,       │ │
│  │  Evidence,   │  │  processing) │  │  Dhanasar framework,     │ │
│  │  Roadmaps)   │  │              │  │  visa bulletin dates)    │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

------

## 3. Technology Stack

### 3.1 Frontend

| Component  | Choice                           | Rationale                                                    |
| ---------- | -------------------------------- | ------------------------------------------------------------ |
| Framework  | Next.js 16.1.6 (App Router)      | Turbopack default bundler, Cache Components, `proxy.ts` replacing middleware, stable React Compiler |
| UI Library | shadcn/ui + Tailwind CSS         | Consistent design system, accessible components, easy theming |
| Charts     | shadcn/ui Charts (Recharts)      | Native theming, dark mode, 53+ pre-built chart patterns, radar/bar/line/pie |
| Onboarding | NextStepJS                       | Framer Motion animations, cross-page routing, interactive steps, Next.js App Router native |
| Auth       | NextAuth.js v5 (Auth.js)         | Google OAuth + email credentials, JWT sessions, App Router integration |
| State      | React Query + Zustand            | Server state caching + lightweight client state              |
| Streaming  | Server-Sent Events (EventSource) | Real-time analysis progress from backend                     |

### 3.2 Backend

| Component         | Choice                                                       | Rationale                                                    |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Framework         | FastAPI (Python 3.14)                                        | Async support, Pydantic v2 native validation, auto-generated OpenAPI docs |
| LLM               | Claude API (Sonnet 4.5) direct                               | Structured outputs beta, 200K context window, strong reasoning — no LangChain needed for sequential prompts |
| Structured Output | Anthropic Structured Outputs (`anthropic-beta: structured-outputs-2025-11-13`) | Guaranteed-valid JSON matching Pydantic schemas, eliminates parsing failures |
| Scholar Data      | Semantic Scholar API (primary)                               | Free, 214M papers, structured JSON with h-index/citations/venues/co-authors |
| GitHub Data       | GitHub GraphQL API v4                                        | Contributions, stars, PRs, review activity, language breakdown |
| CV Parsing        | PyMuPDF (`pymupdf4llm`)                                      | Fast PDF text extraction → Claude structured parsing         |
| Data Import       | Custom parsers for Google Takeout, ChatGPT export, LinkedIn PDF | MBOX (Gmail), JSON (ChatGPT), PDF (LinkedIn)                 |
| Database          | PostgreSQL + SQLAlchemy                                      | Relational data for users, profiles, evidence, roadmaps      |
| ORM (Frontend)    | Prisma                                                       | Type-safe queries from Next.js API routes                    |
| Export            | `docx` (npm, DOCX), `reportlab` (PDF), native (JSON/Markdown) | Multiple portable formats                                    |

### 3.3 Infrastructure

| Component       | Choice                                         | Rationale                                                    |
| --------------- | ---------------------------------------------- | ------------------------------------------------------------ |
| MCP Server      | FastAPI-MCP (optional)                         | Visa bulletin dates, processing times, curated policy updates |
| File Storage    | Local filesystem (hackathon) → S3 (production) | Uploaded documents, temp processing files                    |
| USCIS Knowledge | Curated JSON/Markdown files in repo            | Criteria definitions, policy updates, Dhanasar framework — injected into Claude context |
| Deployment      | Vercel (frontend) + Railway/Render (backend)   | Fast deployment for hackathon demo                           |

------

## 4. Data Portability Engine

### 4.1 Supported Import Sources

This is the core innovation aligned with the hackathon theme. The tool ingests career data from wherever users already store it.

#### Google Takeout Integration

Users export their Google data via Google Takeout and upload the archive:

- **Gmail (MBOX format)**: Parse for conference invitations, peer review requests, award notifications, media interview requests, speaking engagement confirmations. Use Claude to classify emails by immigration-relevant category.
- **Google Scholar**: Publication list, citation data (if exported via Takeout or linked via Semantic Scholar).
- **Google Calendar (ICS format)**: Extract speaking engagements, conference attendance, committee meetings, judging sessions. Pattern-match event titles and descriptions against immigration-relevant activities.
- **Google Drive metadata**: Identify documents related to awards, certificates, recommendation letters.

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
- Recommendations (potential evidence letters)
- Education and certifications
- Volunteer/board positions

#### Direct File Uploads

- **CV/Resume (PDF/DOCX)**: Primary career data source
- **Publication list (PDF/BibTeX)**: Detailed publication records
- **Award certificates (PDF/images)**: Visual evidence for criterion 1
- **Media coverage (URLs/screenshots)**: Evidence for criterion 3
- **Recommendation letters (PDF)**: Support for multiple criteria

#### API Integrations (User-Linked)

- **Semantic Scholar**: User pastes profile URL → fetch h-index, citations, papers, co-authors
- **GitHub**: User pastes username → fetch contributions, stars, PRs, review activity

### 4.2 Import Processing Pipeline

```
User provides data source (file upload or API link)
  │
  ├─→ [File Type Router]
  │     ├─ MBOX → Gmail parser (email classification via Claude)
  │     ├─ JSON → ChatGPT export parser / Google Takeout parser
  │     ├─ ICS  → Calendar event extractor
  │     ├─ PDF  → PyMuPDF text extraction → Claude structured parsing
  │     ├─ DOCX → python-docx text extraction → Claude structured parsing
  │     └─ URL  → Semantic Scholar API / GitHub GraphQL API
  │
  ├─→ [Claude Structured Extraction]
  │     Input: Raw text + Pydantic schema definition
  │     Output: Guaranteed-valid JSON matching ImmigrationProfile schema
  │     Mode: Anthropic Structured Outputs beta
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

| Format                 | Content                                                      | Use Case                                                     |
| ---------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **JSON** (open schema) | Full structured immigration profile + evidence inventory + roadmap | Machine-readable, portable to other tools, attorney software |
| **Markdown**           | Human-readable profile summary, criteria assessment, action plan | Personal records, version control, sharing                   |
| **PDF**                | Polished report with radar chart, gap analysis, roadmap timeline | Attorney consultations, personal reference                   |
| **DOCX**               | Editable document with all sections                          | Attorney markup, collaborative editing                       |

The JSON export schema is designed to be an open standard that any immigration tool or attorney could consume — directly implementing GDPR Article 20's right to receive personal data in a structured, machine-readable format.

------

## 5. Agentic Pipeline Architecture

### 5.1 Four-Agent Sequential Pipeline

Each agent is a specialized Claude API call with its own prompt template, Pydantic input/output schema, and confidence scoring. The user can review and correct output at each stage (human-in-the-loop).

#### Agent 1: Ingestion Agent

- **Input**: Raw uploaded files and API data
- **Processing**: File parsing, text extraction, data normalization
- **Output**: `RawCareerData` Pydantic model (unstructured text organized by source)
- **User checkpoint**: "We found 12 publications, 3 awards, and 47 relevant emails. Does this look right?"

#### Agent 2: Extraction Agent

- **Input**: `RawCareerData`
- **Processing**: Claude Structured Outputs extract immigration-relevant evidence into typed fields
- **Output**: `ImmigrationProfile` Pydantic model with typed evidence records
- **User checkpoint**: "Here's your structured profile. Review and correct any misclassified items."

#### Agent 3: Assessment Agent

- **Input**: `ImmigrationProfile` + USCIS criteria knowledge base
- **Processing**: Claude scores each evidence item against specific EB-1A/NIW criteria with calibrated confidence
- **Output**: `CriteriaAssessment` Pydantic model with per-criterion scores, confidence %, evidence mapping
- **User checkpoint**: Radar chart + criteria cards with confidence badges. User can dispute scores.

#### Agent 4: Roadmap Agent

- **Input**: `CriteriaAssessment` + user preferences (timeline, risk appetite, time budget)
- **Processing**: Claude generates time-phased action plan weighted by gap severity and feasibility
- **Output**: `ImmigrationRoadmap` Pydantic model with quarterly milestones and specific actions
- **User checkpoint**: Timeline visualization. User can adjust priorities and regenerate.

### 5.2 Streaming Architecture

Each agent streams progress via Server-Sent Events to the frontend:

```python
# Backend: FastAPI SSE endpoint
@app.get("/api/analyze/stream")
async def stream_analysis(profile_id: str):
    async def event_generator():
        yield {"event": "stage", "data": {"stage": "ingestion", "status": "started"}}

        # Agent 1: Ingestion
        async for chunk in ingestion_agent.process(profile_id):
            yield {"event": "progress", "data": chunk}

        yield {"event": "stage", "data": {"stage": "extraction", "status": "started"}}

        # Agent 2: Extraction (with Claude streaming)
        async for chunk in extraction_agent.process(profile_id):
            yield {"event": "progress", "data": chunk}

        # ... continue for assessment and roadmap agents

    return EventSourceResponse(event_generator())
// Frontend: React hook consuming SSE
const useAnalysisStream = (profileId: string) => {
  const [stage, setStage] = useState<AnalysisStage>('idle');
  const [progress, setProgress] = useState<ProgressUpdate[]>([]);

  useEffect(() => {
    const source = new EventSource(`/api/analyze/stream?id=${profileId}`);
    source.addEventListener('stage', (e) => setStage(JSON.parse(e.data)));
    source.addEventListener('progress', (e) => setProgress(prev => [...prev, JSON.parse(e.data)]));
    return () => source.close();
  }, [profileId]);

  return { stage, progress };
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
    data_confidence: int = Field(ge=0, le=100, description="How reliable is the underlying data")
    criteria_match: int = Field(ge=0, le=100, description="How well does evidence match USCIS criteria")
    overall: int = Field(ge=0, le=100, description="Weighted combination")
    reasoning: str = Field(description="2-3 sentence explanation")

class Publication(BaseModel):
    title: str
    venue: str
    year: int
    citation_count: Optional[int] = None
    co_authors: list[str] = []
    doi: Optional[str] = None
    source: EvidenceSource
    confidence: ConfidenceLevel

class Award(BaseModel):
    name: str
    granting_organization: str
    year: int
    scope: str  # "international", "national", "regional", "institutional"
    description: Optional[str] = None
    source: EvidenceSource
    confidence: ConfidenceLevel

class JudgingRole(BaseModel):
    role: str  # "peer reviewer", "program committee", "award judge"
    organization: str
    year: int
    documented: bool  # Has invitation letter/confirmation
    source: EvidenceSource
    confidence: ConfidenceLevel

class MediaCoverage(BaseModel):
    title: str
    outlet: str
    date: Optional[date] = None
    url: Optional[str] = None
    about_person: bool  # vs. merely quoting
    source: EvidenceSource
    confidence: ConfidenceLevel

class LeadershipRole(BaseModel):
    title: str
    organization: str
    start_date: date
    end_date: Optional[date] = None
    is_distinguished_org: bool
    source: EvidenceSource
    confidence: ConfidenceLevel

class ImmigrationProfile(BaseModel):
    """Core schema — the portable, user-owned immigration profile."""
    # Identity
    name: str
    current_visa_status: Optional[str] = None
    country_of_birth: Optional[str] = None
    target_pathway: ImmigrationTarget
    target_timeline_years: int = Field(ge=1, le=10)

    # Career basics
    current_role: Optional[str] = None
    current_employer: Optional[str] = None
    years_experience: Optional[int] = None
    field_of_expertise: str

    # Evidence inventory
    publications: list[Publication] = []
    awards: list[Award] = []
    judging_roles: list[JudgingRole] = []
    media_coverage: list[MediaCoverage] = []
    leadership_roles: list[LeadershipRole] = []

    # Scholar metrics
    h_index: Optional[int] = None
    total_citations: Optional[int] = None
    i10_index: Optional[int] = None

    # GitHub metrics
    github_stars: Optional[int] = None
    github_contributions_last_year: Optional[int] = None
    github_pr_reviews: Optional[int] = None
    notable_repos: list[str] = []

    # Memberships
    selective_memberships: list[str] = []

    # Salary / compensation (optional, user-controlled)
    compensation_percentile: Optional[str] = None

    # Data sources used
    data_sources: list[EvidenceSource] = []
```

### 6.2 Criteria Assessment Output

```python
class CriterionScore(BaseModel):
    criterion_number: int  # 1-10 for EB-1A
    criterion_name: str
    evidence_found: list[str]  # References to specific evidence items
    strength: str  # "strong", "moderate", "weak", "none"
    confidence: ConfidenceLevel
    gaps: list[str]  # What's missing
    priority_actions: list[str]  # Top 2-3 actions to strengthen

class CriteriaAssessment(BaseModel):
    pathway: ImmigrationTarget
    criteria_scores: list[CriterionScore]
    criteria_met_count: int
    criteria_close_count: int  # "moderate" strength
    overall_readiness: str  # "ready to file", "1-2 years", "2-4 years", "significant gaps"
    strongest_criteria: list[int]
    weakest_criteria: list[int]
    recommended_focus: list[int]  # Criteria with best effort-to-impact ratio
```

### 6.3 Roadmap Output

```python
class RoadmapAction(BaseModel):
    action: str
    description: str
    target_criterion: list[int]  # Which criteria this strengthens
    quarter: str  # "Q1 2026", "Q2 2026", etc.
    effort_level: str  # "low", "medium", "high"
    impact_level: str  # "low", "medium", "high"
    specific_opportunities: list[str] = []  # Named conferences, journals, etc.

class QuarterlyMilestone(BaseModel):
    quarter: str
    actions: list[RoadmapAction]
    expected_criteria_improvement: dict[int, str]  # criterion_number → new expected strength

class ImmigrationRoadmap(BaseModel):
    profile_id: str
    pathway: ImmigrationTarget
    timeline_years: int
    milestones: list[QuarterlyMilestone]
    narrative_summary: str  # 3-4 paragraph human-readable roadmap
    disclaimer: str = "This is not legal advice. Consult a qualified immigration attorney."
```

------

## 7. Prompt Template Library

### 7.1 Architecture

```
lib/prompts/
├── __init__.py              # Registry, versioning, template loader
├── extraction/
│   ├── cv_parser.py         # CV text → ImmigrationProfile fields
│   ├── gmail_classifier.py  # Email → immigration-relevant category
│   ├── chatgpt_analyzer.py  # ChatGPT export → career insights
│   ├── scholar_enricher.py  # Scholar data → publications schema
│   └── github_analyzer.py   # GitHub data → contributions schema
├── criteria/
│   ├── eb1a_assessor.py     # Evidence → 10 criteria scoring
│   ├── niw_assessor.py      # Evidence → Dhanasar 3-prong scoring
│   └── o1_assessor.py       # Evidence → O-1 criteria scoring
├── roadmap/
│   ├── gap_analyzer.py      # Criteria gaps → prioritized actions
│   └── plan_generator.py    # Actions → time-phased roadmap
├── interactive/
│   ├── what_if.py           # Hypothetical scenario analysis
│   └── chat_advisor.py      # Conversational Q&A about profile
└── shared/
    ├── uscis_knowledge.py   # Curated criteria definitions + Oct 2024 updates
    ├── confidence_rubric.py # Calibration examples for confidence scoring
    └── base.py              # Base template class with versioning
```

### 7.2 Base Template Pattern

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class PromptTemplate:
    name: str
    version: str
    system_prompt: str
    user_prompt_template: str
    output_schema: type  # Pydantic model class
    temperature: float = 0.2
    max_tokens: int = 4096

    def render_user_prompt(self, **kwargs) -> str:
        return self.user_prompt_template.format(**kwargs)

    def to_api_params(self, **kwargs) -> dict:
        return {
            "model": "claude-sonnet-4-5",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": self.system_prompt,
            "messages": [{"role": "user", "content": self.render_user_prompt(**kwargs)}],
            # Structured outputs beta
            "betas": ["structured-outputs-2025-11-13"],
            "output_format": {
                "type": "json_schema",
                "schema": self.output_schema.model_json_schema()
            }
        }
```

### 7.3 Example: EB-1A Criteria Assessor

```python
eb1a_assessor = PromptTemplate(
    name="eb1a_criteria_assessor",
    version="1.0.0",
    temperature=0.2,
    max_tokens=8192,
    output_schema=CriteriaAssessment,
    system_prompt="""You are an immigration evidence analyst specializing in EB-1A
extraordinary ability petitions. You have deep knowledge of USCIS adjudication
standards, the two-step Kazarian framework, and the October 2024 policy updates.

USCIS EB-1A CRITERIA (updated October 2024):
{uscis_criteria_definitions}

CONFIDENCE CALIBRATION:
- 90-100%: Evidence directly matches USCIS criteria with independent corroboration
  Example: Published peer review invitation letter from Nature journal → Criterion 4
- 70-89%: Evidence is relevant and substantive but may need additional documentation
  Example: Self-reported conference PC membership without invitation letter → Criterion 4
- 40-69%: Evidence is tangentially related or lacks specificity
  Example: Reviewed student papers as teaching assistant → Criterion 4
- 0-39%: No meaningful evidence or evidence too weak
  Example: No judging/review experience found → Criterion 4

IMPORTANT: The October 2024 update clarified that team awards now qualify under
Criterion 1, past memberships count under Criterion 2, and published material
no longer requires demonstrating "the value of the person's work" for Criterion 3.

You must assess ALL 10 criteria, even if evidence is absent. Be honest about gaps.
Meeting 4-5 criteria (not just the minimum 3) is practically essential in 2025-2026
given declining approval rates.""",

    user_prompt_template="""Analyze the following structured immigration profile
against all 10 EB-1A extraordinary ability criteria.

For EACH criterion, provide:
- evidence_found: specific items from the profile that support it
- strength: "strong" | "moderate" | "weak" | "none"
- confidence: data_confidence (0-100), criteria_match (0-100), overall (0-100),
  and reasoning (2-3 sentences)
- gaps: what specific evidence is missing
- priority_actions: top 2-3 concrete actions to strengthen this criterion

PROFILE:
{profile_json}

Assess against the EB-1A pathway. Be calibrated and honest. Do not inflate scores."""
)
```

------

## 8. Synthetic Data Strategy

### 8.1 Purpose

For the hackathon demo, synthetic personas allow showcasing the tool's capabilities without requiring real immigration data (which is sensitive). Synthetic data also enables testing across diverse profiles — researcher, engineer, founder, artist — to demonstrate versatility.

### 8.2 Sources

| Source                               | What It Provides                                             | How to Use                                                   |
| ------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **PersonaHub (HuggingFace)**         | 1B synthetic personas with demographics, interests, backgrounds | Generate realistic user profiles with career histories       |
| **Google Synthetic-Persona-Chat**    | 20K persona-based conversations                              | Simulate ChatGPT export data for the import pipeline         |
| **NVIDIA NeMo Synthetic Data Guide** | Framework for generating synthetic user memory datasets      | Create realistic "memory" datasets that combine career data with personal context |

### 8.3 Demo Personas

Create 3 pre-built synthetic personas that showcase different immigration pathways:

**Persona 1: Dr. Priya Sharma — AI Researcher**

- H-1B holder, India-born, 6 years in U.S.
- Target: EB-1A in 2 years
- Strong: 25 publications, h-index 15, 3 conference PC memberships
- Weak: No awards, no media coverage, no selective memberships
- Data sources: CV, Google Scholar, Gmail (with conference invites)

**Persona 2: Marco Chen — Senior Software Engineer**

- H-1B holder, China-born, 8 years in U.S.
- Target: EB-2 NIW in 3 years
- Strong: 500+ GitHub stars, 3 patents, critical role at FAANG
- Weak: No publications, no judging, limited visibility
- Data sources: CV, GitHub, LinkedIn PDF, Google Takeout

**Persona 3: Amara Okafor — Tech Founder**

- O-1 holder, Nigeria-born, 4 years in U.S.
- Target: EB-1A in 1 year (already strong profile)
- Strong: TechCrunch coverage, YC alum, speaking at 5 conferences, high compensation
- Weak: No scholarly publications, limited judging
- Data sources: CV, media URLs, LinkedIn, ChatGPT export

### 8.4 Synthetic Data Generation Pipeline

```python
# Use PersonaHub to generate base personas
# Enrich with synthetic career data matching immigration criteria
# Generate synthetic Google Takeout archives (MBOX, ICS, JSON)
# Generate synthetic ChatGPT export conversations about career planning
# Pre-process through the full pipeline to cache results for demo speed
```

------

## 9. Authentication & Authorization

### 9.1 Stack

- **NextAuth.js v5** with App Router integration
- **Providers**: Google OAuth (primary) + email/password (Credentials)
- **Session**: JWT strategy (stateless, no session table)
- **Database**: PostgreSQL via Prisma for user records

### 9.2 Authorization Model

```
proxy.ts (Next.js 16)
  ├── Public routes: /, /login, /register, /about
  ├── Protected routes: /dashboard/*, /api/*
  │   → Verify JWT → Extract user_id → Scope all DB queries
  └── API routes: /api/*
      → Forward JWT to FastAPI backend → Backend validates independently
```

### 9.3 Privacy Features

- **Data scope**: Every database query filtered by authenticated user_id
- **Delete account**: Cascading deletion of all user data, uploaded files, generated profiles
- **Session timeout**: JWT expires after 24 hours
- **No cross-user data**: Zero shared state between users
- **Transparent AI disclosure**: UI clearly shows what data is sent to Claude API vs. processed locally

------

## 10. Frontend Architecture

### 10.1 Route Structure

```
app/
├── (public)/
│   ├── page.tsx                # Landing page
│   ├── login/page.tsx
│   └── register/page.tsx
├── (dashboard)/
│   ├── layout.tsx              # Sidebar + header + NextStep provider
│   ├── page.tsx                # Dashboard home / profile overview
│   ├── evidence/
│   │   ├── page.tsx            # Evidence upload & management
│   │   └── [id]/page.tsx       # Individual evidence detail
│   ├── criteria/
│   │   ├── page.tsx            # Criteria radar chart + cards
│   │   └── [criterion]/page.tsx # Deep-dive into single criterion
│   ├── roadmap/
│   │   ├── page.tsx            # Timeline visualization
│   │   └── what-if/page.tsx    # What-if simulator
│   ├── chat/page.tsx           # Conversational AI advisor
│   ├── export/page.tsx         # Export center (JSON, MD, PDF, DOCX)
│   └── settings/page.tsx       # Profile, data management, delete account
├── onboarding/page.tsx         # First-run guided setup
├── api/                        # Route handlers (proxy to FastAPI)
└── proxy.ts                    # Auth checks, API routing
```

### 10.2 Key Visualizations (shadcn Charts)

**Criteria Radar Chart** — centerpiece visualization showing all 10 EB-1A criteria as axes:

```typescript
import { RadarChart, PolarGrid, PolarAngleAxis, Radar } from "recharts";
import { ChartContainer, ChartConfig } from "@/components/ui/chart";

const criteriaData = [
  { criterion: "Awards", score: 72, fullMark: 100 },
  { criterion: "Memberships", score: 15, fullMark: 100 },
  { criterion: "Media", score: 0, fullMark: 100 },
  { criterion: "Judging", score: 85, fullMark: 100 },
  { criterion: "Contributions", score: 68, fullMark: 100 },
  { criterion: "Articles", score: 90, fullMark: 100 },
  { criterion: "Exhibitions", score: 0, fullMark: 100 },
  { criterion: "Leadership", score: 55, fullMark: 100 },
  { criterion: "Salary", score: 78, fullMark: 100 },
  { criterion: "Commercial", score: 0, fullMark: 100 },
];
```

**Additional charts**: Citation trend line chart, evidence completeness stacked bars, roadmap timeline (horizontal bar/Gantt), pathway comparison donut.

### 10.3 NextStepJS Onboarding Flow

```typescript
const onboardingTour: Tour[] = [{
  tour: "firstRun",
  steps: [
    {
      title: "Welcome to [Project Name]",
      content: "We'll help you build a personalized roadmap to strengthen your EB-1A, NIW, or O-1 case using your own career data.",
      // Full-screen overlay, no selector
    },
    {
      title: "Choose Your Immigration Target",
      content: "Select the pathway you're working toward. We'll tailor everything to its specific criteria.",
      selector: "#pathway-selector",
    },
    {
      title: "Bring Your Data",
      content: "Upload your CV, connect Scholar & GitHub, or import Google Takeout and ChatGPT exports. Your data, your terms.",
      selector: "#data-import-zone",
    },
    {
      title: "Watch AI Analyze Your Profile",
      content: "Our AI extracts immigration-relevant evidence from your data in real-time. You can review and correct everything.",
      selector: "#analysis-stream",
    },
    {
      title: "Your Criteria Dashboard",
      content: "This radar chart maps your evidence to each USCIS criterion. Green = strong. Red = needs work. Each score includes a confidence percentage.",
      selector: "#criteria-radar",
    },
    {
      title: "Your Personalized Roadmap",
      content: "A time-phased action plan telling you exactly what to do and which criterion each action strengthens.",
      selector: "#roadmap-timeline",
    },
    {
      title: "Export & Own Your Data",
      content: "Download everything as JSON, PDF, Markdown, or DOCX. Your immigration profile is yours to take anywhere.",
      selector: "#export-center",
    },
  ]
}];
```

------

## 11. Confidence Scoring System

### 11.1 Three-Level Model

| Level                  | Measures                                          | Range  | Source                                                       |
| ---------------------- | ------------------------------------------------- | ------ | ------------------------------------------------------------ |
| **Data Confidence**    | How complete/reliable is the underlying evidence? | 0-100% | Computed from source type, corroboration across sources, documentation quality |
| **Criteria Match**     | How well does evidence match USCIS requirements?  | 0-100% | Assessed by Claude against calibrated examples               |
| **Overall Confidence** | Weighted combination                              | 0-100% | `0.4 * data + 0.6 * criteria_match` (criteria match weighted higher) |

### 11.2 UI Representation

```tsx
<Badge variant={
  confidence > 70 ? "default" :      // Green
  confidence > 40 ? "secondary" :     // Yellow/amber
  "destructive"                        // Red
}>
  {confidence}% confident
</Badge>
```

Each criterion card shows: criterion name/description, confidence badge, evidence items with individual confidence, a "Show AI reasoning" expandable section, and "What would strengthen this" recommendations.

### 11.3 Calibration Anchors (injected into prompts)

Defined in `shared/confidence_rubric.py` with 2-3 examples per criterion per strength level. These ensure Claude's confidence scores are meaningful and consistent across runs.

------

## 12. MCP Server (Optional, Stretch Goal)

A lightweight FastAPI-MCP server exposing 3-4 tools for immigration intelligence:

| Tool                      | Description                                                  | Data Source                       |
| ------------------------- | ------------------------------------------------------------ | --------------------------------- |
| `get_visa_bulletin`       | Current priority dates by category and country               | Pre-curated JSON, updated monthly |
| `get_processing_times`    | USCIS processing times for I-140, I-485                      | Pre-curated JSON                  |
| `get_criteria_definition` | Detailed USCIS criteria text with Oct 2024 updates           | Static markdown knowledge base    |
| `get_policy_updates`      | Recent policy changes, court decisions, approval rate trends | Curated markdown with sources     |

This aligns with the hackathon's MCP awareness (Next.js 16 DevTools MCP, DTI's interoperability focus) and allows any MCP-compatible AI agent to query immigration intelligence.

------

## 13. Security & Compliance

### 13.1 Data Handling

- Uploaded files stored temporarily for processing, deleted after extraction
- Structured profiles stored in PostgreSQL, encrypted at rest
- No data shared between users; all queries scoped to authenticated user
- Claude API receives structured profiles, not raw documents
- Clear UI disclosure: "Your CV text is sent to Anthropic's Claude API for analysis"

### 13.2 Disclaimers (Built into UI and Exports)

- "This tool is not legal advice and does not replace an immigration attorney."
- "AI assessments include confidence scores indicating uncertainty. Verify all findings with qualified counsel."
- "USCIS criteria interpretations are based on publicly available policy guidance as of [date]. Adjudication standards may change."

------

## 14. Development Plan (Hackathon Sprint)

### Phase 1: Core Pipeline

- [ ] Next.js 16 project setup with shadcn/ui, NextAuth, Prisma
- [ ] FastAPI backend with Pydantic models and PostgreSQL
- [ ] CV upload → Claude Structured Output extraction → profile storage
- [ ] Semantic Scholar API integration (user-linked)
- [ ] GitHub GraphQL API integration (user-linked)

### Phase 2: Assessment & Visualization

- [ ] EB-1A criteria assessment prompt template with confidence scoring
- [ ] Criteria radar chart (shadcn Charts)
- [ ] Criteria cards with confidence badges and reasoning
- [ ] Streaming UI for analysis progress

### Phase 3: Roadmap & Data Portability

- [ ] Gap analysis → roadmap generation pipeline
- [ ] Timeline/Gantt visualization
- [ ] Export center: JSON, Markdown, PDF, DOCX
- [ ] Google Takeout import parser (Gmail MBOX, Calendar ICS)

### Phase 4: Polish & Demo

- [ ] NextStepJS onboarding flow
- [ ] Synthetic demo personas (3 pre-built profiles)
- [ ] What-if simulator (stretch)
- [ ] Conversational chat (stretch)
- [ ] Demo video recording
- [ ] Submission page writeup