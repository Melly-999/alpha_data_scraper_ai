# Mobile AI Roadmap

**Track:** MellyTrade Mobile AI
**First run:** MOBILE-AI-000 (docs-only)

This roadmap defines the MellyTrade Mobile AI workstream: an AI chart-review,
paper game-plan, risk-coach, and setup-journal experience delivered first as a
PWA inside the existing `alpha_data_scraper_ai` repo under `/mobile`.

Related docs:

- Architecture decision: `docs/mobile/mobile_app_architecture_decision.md`
- Context / history snapshot: `docs/mobile/mobile_ai_context_snapshot.md`
- Workspace setup: `docs/mobile/mobile_ai_workspace_setup.md`
- Existing mobile roadmap: `docs/tasks/mobile_app_roadmap.md`

## Product vision (one line)

MellyTrade Mobile should feel like a premium mobile trading terminal, an AI
risk coach, a paper/simulation-only trading companion, a setup journal, and a
mobile portfolio/showcase app — **not** a signal-selling app and **not** a
live trading execution app.

Planned feature set:

- AI Chart Review
- Paper Game Plan
- Mobile Watchlist
- Setup Journal
- Safety Score
- FOMO Guard / No FOMO mode
- Weekly Review
- Before/After Review
- Melly Pet trading/risk coach
- Existing Monte Carlo Simulation Snapshot (reuse existing concept; do not
  build a new Monte Carlo engine)
- Future subscription/paywall strategy
- Future PWA → Capacitor/Expo/native path

## Required safety copy

The following phrases must appear in mobile product copy and in the relevant
docs across this track:

- Analysis only. Not financial advice.
- Paper plan only. No live orders.
- Human review required.
- Max simulated risk 1%.
- Wait for confirmation. Do not chase.
- No broker execution.
- No guaranteed profit.
- No wallet/private keys.
- No AI provider keys in frontend.

## Standing safety posture (every phase)

- autotrade=false
- dry_run=true
- read_only=true
- live_orders_blocked=true
- max risk ≤ 1%
- no live trading
- no broker execution
- no wallet/private keys
- no investment advice claims
- no profit guarantees
- human review required
- paper/simulation only
- no buy/sell/order/execute controls
- no AI provider keys in frontend

---

## Phases

### MOBILE-AI-000 — Architecture decision, workspace setup, and roadmap update

- **Purpose:** establish the Mobile AI direction, record the architecture
  decision, preserve context, define workspace setup, and create this ordered
  plan.
- **Scope:** documentation only.
- **Likely files to change:** `docs/mobile/*.md`, `docs/tasks/mobile_ai_roadmap.md`,
  `docs/tasks/mobile_app_roadmap.md` (small additive section),
  `docs/tasks/mellytrade_master_roadmap.md` (small additive entry).
- **Implementation type:** docs-only.
- **Validation:** `python scripts/validate_safety_config.py`; static safety
  scan of changed docs.
- **Safety constraints:** no runtime code, no providers, no upload, no env
  vars, no config/workflow/package/Docker/deployment changes.
- **Stop conditions:** any runtime/frontend/backend/config/secret file would be
  modified; any execution control would be added.

### MOBILE-AI-001 — Mobile AI safety contract and product vision

- **Purpose:** write the explicit safety contract and product vision for the
  mobile surface.
- **Scope:** documentation only.
- **Likely files to change:** `docs/mobile/mobile_ai_safety_contract.md`.
- **Implementation type:** docs-only.
- **Validation:** static safety scan; confirm required safety copy present.
- **Safety constraints:** no runtime changes; contract must encode the
  standing safety posture above.
- **Stop conditions:** any execution surface implied or any provider key
  referenced as required at runtime.

### MOBILE-AI-002 — Mobile AI benchmark and MVP screen plan

- **Purpose:** benchmark the inspiration category and define the MVP screen map.
- **Scope:** documentation only.
- **Likely files to change:** `docs/mobile/mobile_ai_mvp_screen_plan.md`.
- **Implementation type:** docs-only.
- **Validation:** static safety scan.
- **Safety constraints:** screen plan must be read-only/mock; no order controls
  in any wireframe.
- **Stop conditions:** any screen specifies live execution or broker login.

### MOBILE-AI-003 — Frontend-only AI Chart Review mock on `/mobile`

- **Purpose:** expand the existing `/mobile` page with static/mock sections
  that demonstrate the full product vision.
- **Scope:** frontend-only, static/mock data only. **This is the recommended
  next implementation PR after the docs-only MOBILE-AI-000 run.**
- **Likely files to change:** `frontend/src/pages/MobileAppPage.tsx` and
  supporting presentational components/styles under `frontend/src/`.
- **Implementation type:** frontend-only.
- **Validation:** frontend build/lint; confirm no new endpoints, no upload, no
  provider keys, mock data only; existing safety badges preserved.
- **Safety constraints:** static/mock only; no backend endpoints; no upload; no
  AI provider keys; keep READ ONLY / DRY RUN / LIVE ORDERS BLOCKED /
  HUMAN REVIEW REQUIRED badges; no buy/sell/order/execute controls.
- **Stop conditions:** any backend call, upload, provider key, or execution
  control is introduced.

MOBILE-AI-003 must expand `/mobile` with these static/mock sections:

- AI Chart Review
- Paper Game Plan
- Safety Score
- Watchlist
- Setup Journal preview
- Before/After Review preview
- FOMO Guard / No FOMO mode
- Weekly Report preview
- Monte Carlo Simulation Snapshot
- Melly Pet Coach

No backend endpoints or upload functionality should be added in MOBILE-AI-003.

### MOBILE-AI-004 — Setup Journal mock

- **Purpose:** flesh out the Setup Journal as a mock UX (entries, tags,
  before/after notes).
- **Scope:** frontend-only, mock data only.
- **Likely files to change:** `frontend/src/` journal components/styles.
- **Implementation type:** frontend-only.
- **Validation:** frontend build/lint; mock data only; no endpoints.
- **Safety constraints:** no persistence to a live broker; no execution; mock
  only; required safety copy retained.
- **Stop conditions:** any backend write or execution surface added.

### MOBILE-AI-005 — FOMO Guard + Melly Pet Risk Coach

- **Purpose:** add the FOMO Guard / No FOMO mode and the Melly Pet risk-coach
  interactions as mock UX.
- **Scope:** frontend-only, mock data only.
- **Likely files to change:** `frontend/src/` Melly Pet / FOMO Guard
  components/styles.
- **Implementation type:** frontend-only.
- **Validation:** frontend build/lint; mock data only.
- **Safety constraints:** coach gives risk discipline copy only — "Wait for
  confirmation. Do not chase." — never trade signals or execution prompts.
- **Stop conditions:** any signal-selling or execution language introduced.

### MOBILE-AI-006 — Backend schemas only

- **Purpose:** define backend request/response schemas for future mobile AI
  features without wiring any endpoint.
- **Scope:** backend schema definitions only (no routes, no execution).
- **Likely files to change:** `app/schemas/` (new mobile AI schema module).
- **Implementation type:** backend schema-only.
- **Validation:** schema unit tests; confirm no new routes;
  `python scripts/validate_safety_config.py`.
- **Safety constraints:** schemas describe analysis/paper-plan data only; no
  order/execution fields; no broker credentials.
- **Stop conditions:** any route or execution field is added.

### MOBILE-AI-007A — Screenshot upload safety contract and retention policy

- **Purpose:** define the safety, privacy, and retention contract for a future
  screenshot upload analysis endpoint **before** any endpoint is built.
- **Scope:** documentation only.
- **Status:** planned / this PR.
- **Likely files to change:**
  `docs/mobile/mobile_ai_screenshot_upload_safety_contract.md`,
  `docs/mobile/mobile_ai_image_privacy_retention_policy.md`,
  `docs/tasks/mobile_ai_roadmap.md`.
- **Implementation type:** docs-only.
- **Validation:** `python scripts/validate_safety_config.py`; static safety
  scan of changed docs.
- **Safety constraints:** no runtime code, no endpoint, no upload UI, no
  provider keys, no storage, no image-processing dependencies.
- **Stop conditions:** any runtime/endpoint/dependency change is attempted.

### MOBILE-AI-007B — Screenshot upload analysis endpoint

- **Purpose:** add a backend endpoint to accept a chart screenshot for analysis
  (paper/analysis only).
- **Scope:** backend endpoint.
- **Status:** future.
- **Prerequisite:** MOBILE-AI-007A merged (safety contract + retention policy
  approved).
- **Likely files to change:** `app/api/routes/`, `app/services/`,
  `app/schemas/`, plus tests.
- **Implementation type:** backend endpoint (high safety review).
- **Validation:** endpoint tests; `tests/app/test_openapi_forbidden_paths.py`;
  `tests/app/test_safety_invariants.py`; safety config validation.
- **Safety constraints:** analysis-only output; no order placement; no broker
  call; MIME/size limits; no images stored without an approved retention
  policy; no provider keys in frontend; no secrets in responses.
- **Stop conditions:** endpoint exposes any execution or broker action, stores
  images before retention approval, or requires frontend provider keys.

> The endpoint implementation moved from MOBILE-AI-007 to **MOBILE-AI-007B**.
> Do not build the upload endpoint before the MOBILE-AI-007A safety contract
> and retention policy are merged.

### MOBILE-AI-008 — AI provider integration

- **Purpose:** wire a backend-only AI provider for chart-review analysis.
- **Scope:** backend AI integration (server-side only).
- **Prerequisite:** upload endpoint safety, privacy, and retention reviewed;
  no frontend keys.
- **Likely files to change:** `app/services/`, backend config for env-based
  keys, plus tests.
- **Implementation type:** AI integration.
- **Validation:** mocked-provider tests; confirm keys are env-only and
  server-side; safety config validation.
- **Safety constraints:** provider keys are backend env vars only; **no AI
  provider keys in frontend**; no live trading; analysis only.
- **Stop conditions:** any provider key reaches the frontend or any execution
  path is created.


### MOBILE-AI-009 — Smart alerts

- **Purpose:** add paper/analysis smart alerts (e.g., watchlist conditions,
  review reminders).
- **Scope:** backend + frontend, analysis/notification only.
- **Likely files to change:** `app/services/`, `app/api/routes/`,
  `frontend/src/`, plus tests.
- **Implementation type:** backend endpoint + frontend.
- **Validation:** tests; safety config validation.
- **Safety constraints:** alerts are informational only; never auto-execute;
  human review required.
- **Stop conditions:** any alert triggers an order or execution.

### MOBILE-AI-010 — Subscription/paywall strategy

- **Purpose:** document the subscription/paywall strategy and gating model.
- **Scope:** documentation first (strategy), implementation deferred.
- **Likely files to change:** `docs/mobile/mobile_ai_subscription_strategy.md`.
- **Implementation type:** docs-only (strategy phase).
- **Validation:** static safety scan.
- **Safety constraints:** no profit guarantees; no investment advice;
  paper/simulation framing only.
- **Stop conditions:** copy implies guaranteed returns or financial advice.

### MOBILE-AI-011 — Capacitor/Expo/native wrapper research

- **Purpose:** research the native wrapper path (Capacitor / Expo / RN) and the
  conditions that justify a separate project.
- **Scope:** documentation / research.
- **Likely files to change:** `docs/mobile/mobile_ai_native_wrapper_research.md`.
- **Implementation type:** native research.
- **Validation:** static safety scan.
- **Safety constraints:** no native packages added in this phase; research
  only.
- **Stop conditions:** any native package or build pipeline is added prematurely.

### MOBILE-AI-012 — App Store / Google Play readiness checklist

- **Purpose:** prepare a store-readiness checklist (privacy, disclaimers,
  review guidelines, safety copy).
- **Scope:** documentation / checklist.
- **Likely files to change:** `docs/mobile/mobile_ai_store_readiness.md`.
- **Implementation type:** native research / docs.
- **Validation:** static safety scan.
- **Safety constraints:** disclaimers must state analysis-only / not financial
  advice / paper only; no store files committed in this phase.
- **Stop conditions:** store config/credentials committed to the repo.

---

## Recommended first implementation order

1. MOBILE-AI-000 — docs-only roadmap, workspace setup, and architecture decision
2. MOBILE-AI-003 — frontend-only `/mobile` mock expansion
3. MOBILE-AI-004 — Setup Journal mock
4. MOBILE-AI-005 — FOMO Guard + Melly Pet Risk Coach
5. MOBILE-AI-006 — backend schemas only
6. MOBILE-AI-007A — screenshot upload safety contract + retention policy (docs-only)
7. MOBILE-AI-007B — screenshot upload analysis endpoint (after 007A merged)
8. MOBILE-AI-008 — AI provider integration
9. MOBILE-AI-009 — smart alerts
10. MOBILE-AI-010 — subscription/paywall strategy
11. MOBILE-AI-011/012 — native wrapper and app store readiness

**Do not start with screenshot upload or AI provider integration. Build the
mobile UX mock first.**

MOBILE-AI-003 is the recommended next implementation PR after this docs-only
run. It should expand the existing `/mobile` page with static/mock sections
only — no backend endpoints and no upload functionality.
