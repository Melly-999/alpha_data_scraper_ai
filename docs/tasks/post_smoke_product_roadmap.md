# Post-Smoke Product Roadmap

## Current status
- local backend/frontend smoke passed
- read-only safety posture preserved
- Supabase audit writer hardening merged
- signal decision write client merged
- RiskManager frontend read-only hardening merged
- Graphify refreshed

## Next recommended product tasks

### P0 - immediate polish

#### 1. Audit Feed UI / Terminal event rail
- Goal: make audit events visible in the terminal shell as a first-class read-only stream.
- Changed areas: frontend terminal layout, audit feed widgets, backend read-only event feed endpoints if needed.
- Acceptance criteria: audit events render in chronological order, degraded states are explicit, no mutation controls are introduced.
- Validation commands: `py -3.11 scripts/validate_safety_config.py`; frontend build; local GET-only smoke.
- Safety notes: keep `read_only=true`, do not add POST/PUT/PATCH/DELETE flows.

#### 2. Demo mode / seeded data polish
- Goal: provide deterministic demo content for walkthroughs and screenshots.
- Changed areas: demo seed data, fallback fixtures, frontend copy and empty states.
- Acceptance criteria: demo views are stable across runs and do not require secrets or live services.
- Validation commands: safety config validation; frontend smoke; demo-mode walkthrough.
- Safety notes: demo assets must remain non-live and non-executable.

#### 3. Dashboard status banner for degraded services
- Goal: surface service health and fallback mode state immediately on load.
- Changed areas: terminal header/banner, health summary cards, backend health payload display.
- Acceptance criteria: users can see when MT5, Supabase, or news dependencies are degraded.
- Validation commands: local smoke; manual GET of `/health` and `/api/health`.
- Safety notes: health display only, no broker or execution controls.

#### 4. Better runbook screenshots/checklist
- Goal: document the safe startup flow and expected terminal states.
- Changed areas: docs, screenshot capture instructions, onboarding notes.
- Acceptance criteria: a new contributor can reproduce the read-only smoke path from docs alone.
- Validation commands: follow the runbook; confirm screenshots match current terminal states.
- Safety notes: document only approved GET-only workflows.

#### 5. Browser UI smoke checklist
- Goal: make UI verification repeatable for local browser checks.
- Changed areas: docs, smoke checklist, optional test harness notes.
- Acceptance criteria: checklist covers terminal page, Risk Manager page, safety badges, and degraded states.
- Validation commands: browser navigation to terminal and Risk Manager routes.
- Safety notes: verify visibility only; no click paths that trigger mutation.

### P1 - useful local product

#### 1. Watchlist improvements
- Goal: improve symbol tracking and persistent watchlist readability.
- Changed areas: watchlist UI, local state persistence, symbol metadata display.
- Acceptance criteria: watchlist entries are easy to add, remove, and review without affecting execution paths.
- Validation commands: frontend build; browser smoke on watchlist views.
- Safety notes: read-only by default, no broker or order hooks.

#### 2. Scanner explanation panel
- Goal: explain why a symbol appears in scanner output.
- Changed areas: scanner UI, reason labels, signal explanation copy.
- Acceptance criteria: each signal row includes human-readable rationale and confidence context.
- Validation commands: local smoke; browser verification of scanner detail panels.
- Safety notes: explanations only, no hidden trade action buttons.

#### 3. Risk policy read-only explainability
- Goal: surface the active policy thresholds in a clear audit-friendly view.
- Changed areas: risk page copy, safety badges, policy summary cards.
- Acceptance criteria: thresholds are visible and cannot be edited from the frontend.
- Validation commands: static check of `RiskManagerPage.tsx`; browser UI smoke.
- Safety notes: no save controls, no emergency stop mutation, no broker calls.

#### 4. Broker cards polish
- Goal: improve the read-only broker status cards and degraded states.
- Changed areas: broker cards, status copy, fallback state styling.
- Acceptance criteria: cards show availability and limitations without suggesting execution.
- Validation commands: browser smoke on broker status area.
- Safety notes: preserve GET-only broker status behavior.

#### 5. Export local report markdown/PDF
- Goal: let users export local read-only reports for review and sharing.
- Changed areas: report generation, print styles, file export helpers.
- Acceptance criteria: export works from read-only data only and excludes secrets.
- Validation commands: report generation test; manual export preview.
- Safety notes: export must not include credentials, account IDs, or live order details.

### P2 - closed beta foundation

#### 1. Auth / private access
- Goal: add gated access before broader beta distribution.
- Changed areas: auth layer, session management, route guards.
- Acceptance criteria: only authorized users can access beta views.
- Validation commands: auth flow tests and unauthorized-access checks.
- Safety notes: no broker credential collection unless a secure model exists.

#### 2. User separation
- Goal: ensure user data and audit trails remain isolated.
- Changed areas: storage namespace, per-user audit scoping, session identity.
- Acceptance criteria: one user cannot see another user’s watchlist, reports, or logs.
- Validation commands: multi-user access tests.
- Safety notes: keep identities and access boundaries explicit.

#### 3. Terms / disclaimer / privacy
- Goal: prepare legal copy for controlled beta access.
- Changed areas: footer links, onboarding modal, documentation pages.
- Acceptance criteria: users see clear non-advice, no-live-trading language before access.
- Validation commands: content review and legal sign-off.
- Safety notes: wording must match the read-only and educational product posture.

#### 4. Deployment plan
- Goal: define a repeatable deploy process for beta environments.
- Changed areas: release notes, environment matrix, rollout checklist.
- Acceptance criteria: each release has a documented rollback and verification path.
- Validation commands: pre-release checklist and deployment dry run.
- Safety notes: deploys must preserve read-only and dry-run defaults.

#### 5. Monitoring / rate limits
- Goal: keep beta usage predictable and observable.
- Changed areas: metrics, logging, request throttling, alerting.
- Acceptance criteria: API usage, degraded services, and error spikes are visible.
- Validation commands: metrics smoke test and rate-limit probes.
- Safety notes: rate limits must protect cost, safety, and service stability.
