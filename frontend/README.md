# Frontend — Immigration Empowerment Through Data Portability

Next.js 16 App Router frontend with shadcn/ui, Recharts visualizations, and real-time SSE streaming.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16.1.6 (App Router, Turbopack) |
| UI | shadcn/ui (Base UI `@base-ui/react` 1.2.0) + Tailwind CSS v4 |
| Charts | Recharts 2.15.4 (radar chart, bar charts) |
| Animations | Framer Motion 12.35.1 |
| State | Zustand 5.0.11 (auth + analysis stores) + React Query 5.90.21 |
| Auth | Custom JWT stored in Zustand with localStorage persistence |
| Streaming | EventSource (SSE) for real-time pipeline progress |
| Theming | next-themes (light/dark mode) |
| Toasts | Sonner 2.0.7 |
| Icons | Lucide React 0.577.0 |

## Getting Started

```bash
pnpm install
pnpm dev          # http://localhost:3000
pnpm build        # Production build (includes TypeScript checks)
```

Requires the backend running at `http://localhost:8000` (configurable via `NEXT_PUBLIC_BACKEND_URL`).

## Project Structure

```
src/
├── app/
│   ├── (public)/                 # Public routes (no auth required)
│   │   ├── page.tsx              # Landing page with features and CTA
│   │   ├── login/page.tsx        # Login form
│   │   └── register/page.tsx     # Registration form
│   ├── (dashboard)/              # Protected routes (auth + onboarding required)
│   │   ├── layout.tsx            # Dashboard wrapper with sidebar, auth checks, onboarding redirect
│   │   ├── page.tsx              # Dashboard overview (profile status, quick actions, readiness)
│   │   └── dashboard/
│   │       ├── evidence/page.tsx # Evidence upload & management (7 source types)
│   │       ├── criteria/page.tsx # Criteria radar chart + criterion cards
│   │       ├── roadmap/page.tsx  # Quarterly milestones with actions
│   │       ├── export/page.tsx   # Export center (JSON, Markdown, PDF, DOCX)
│   │       └── settings/page.tsx # Account settings, consent tracking, data deletion
│   ├── onboarding/page.tsx       # 6-step wizard with pathway recommendation
│   ├── layout.tsx                # Root layout with providers
│   └── globals.css               # Global styles
├── components/
│   ├── ui/                       # shadcn/ui primitives (Base UI based)
│   │   ├── button.tsx, card.tsx, dialog.tsx, sidebar.tsx, badge.tsx, etc.
│   ├── dashboard-sidebar.tsx     # Navigation sidebar
│   ├── criteria-radar-chart.tsx  # Recharts radar chart for criteria scores
│   ├── criterion-card.tsx        # Individual criterion detail card
│   ├── consent-modal.tsx         # Per-source consent interface
│   ├── confirm-modal.tsx         # Confirmation dialogs
│   └── theme-provider.tsx        # Light/dark mode provider
└── lib/
    ├── store.ts                  # Zustand stores (auth + analysis)
    ├── api.ts                    # API client with JWT auth
    ├── providers.tsx             # React Query + theme providers
    └── utils.ts                  # Utility functions
```

## Key Architecture Decisions

### shadcn/ui with Base UI (not Radix)

This project uses `@base-ui/react` 1.2.0, not Radix primitives. Component composition uses the `render` prop pattern:

```tsx
// Correct — Base UI pattern
<DialogTrigger render={<Button />}>Open</DialogTrigger>

// Wrong — Radix pattern (do NOT use)
<DialogTrigger asChild><Button>Open</Button></DialogTrigger>
```

### Custom JWT Auth (not NextAuth)

Authentication is fully custom — NextAuth v5 is in `package.json` but unused. Auth state lives in a Zustand store with localStorage persistence:

```typescript
useAuthStore: {
  token, userId, userName, onboardingCompleted,
  setAuth, clearAuth, isAuthenticated
}
```

The `apiClient` utility reads the token from the store and attaches it as a Bearer header. For SSE connections (EventSource can't send headers), the backend provides a short-lived SSE-specific JWT token passed as a query parameter.

### Analysis State

Pipeline progress is tracked in a separate Zustand store:

```typescript
useAnalysisStore: {
  currentProfileId,
  stages: { ingestion, extraction, assessment, roadmap },  // each: 'idle' | 'running' | 'completed' | 'error'
  setStage, reset
}
```

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Landing page |
| `/login` | Login form |
| `/register` | Registration form |
| `/onboarding` | 6-step wizard → pathway recommendation |
| `/` (dashboard) | Profile overview, quick actions |
| `/dashboard/evidence` | Upload CV, Scholar, GitHub, Gmail, ChatGPT, LinkedIn, images |
| `/dashboard/criteria` | Radar chart + criterion cards with confidence scores |
| `/dashboard/roadmap` | Quarterly milestones with specific actions |
| `/dashboard/export` | Download JSON, Markdown, PDF, DOCX |
| `/dashboard/settings` | Account settings, consent tracking, data deletion |

## Deployment

Deployed on Railway at [immigration-roadmap.com](https://immigration-roadmap.com). Auto-deploys on push to `main`.
