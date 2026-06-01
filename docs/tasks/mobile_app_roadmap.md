# Mobile App Roadmap

## Purpose

MellyTrade mobile development starts as a PWA / mobile-first frontend shell,
then can later become a native wrapper or Expo app **after** the web demo is
stable. The mobile surface stays strictly read-only and dry-run: it never
connects to live broker execution and never exposes order/buy/sell/execute
controls.

## Current Task

**MOBILE-APP-003 — Vercel mobile frontend deploy runbooks (Draft PR / In progress):**

- docs-only Render backend + Vercel frontend hosted-demo runbooks
- hosted mobile demo smoke checklist (TEMPLATE / NOT EXECUTED until run)
- no platform config (`render.yaml`/`vercel.json`) and no deploy performed

MOBILE-APP-001 (mobile PWA shell, `/mobile` route) is **Done** (merged via #245).
MOBILE-APP-002 (iPad/iPhone smoke checklist) is **Done** (merged via #246).

## Recommended Phases

**Phase 1 — PWA / mobile shell:**

- `/mobile` route
- responsive layout (375px → tablet/desktop)
- safety badges
- Melly Pet assistant
- Vercel-compatible frontend

**Phase 2 — Hosted mobile demo:**

- Vercel frontend
- Render backend
- CORS smoke
- iPad/iPhone test
- screenshots / evidence pack

**Phase 3 — Mobile app wrapper decision:**

- Expo
- Capacitor
- Tauri mobile
- native shell
- keep backend read-only

**Phase 4 — Native app prototype:**

- app icon
- splash screen
- Melly Pet onboarding
- safe API base URL handling
- no broker credentials in the mobile app

## Safety Rules

- no live trading
- no broker execution
- no credentials in the mobile app
- no order / buy / sell / execute controls
- read-only / dry-run by default
- live orders blocked

## Task Status

| Task | Title | Status |
|---|---|---|
| MOBILE-APP-001 | Mobile PWA shell (`/mobile`) | Done (#245) |
| MOBILE-APP-002 | iPad/iPhone smoke checklist | Done (#246) |
| MOBILE-APP-003 | Vercel mobile frontend deploy checklist | Draft PR / In progress |
| MOBILE-APP-004 | Melly Pet mobile onboarding polish | Planned |
| MOBILE-APP-005 | App icon / favicon / PWA icon pipeline | Planned |
| MOBILE-APP-006 | Expo / native wrapper decision | Planned |
| MOBILE-APP-007 | Native prototype, only after safety review | Planned |
