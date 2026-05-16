# Claude Design PR Breakdown

## Source

Generated from Claude Design export stored outside the repo:

```
C:\AI\MellyTrade_Workspace\03_Docs\ClaudeDesign\MellyTrade_Closed_Beta_Demo_UI_Pack
```

Raw export files are intentionally not committed.

---

## Overview

Five sequential, reviewable PRs. Each is independently deployable, preserves the safety posture, and ends with a green CI run.

**Safety posture must hold across every PR:**

```
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

**CI guards on every PR:**

```bash
pnpm -C frontend typecheck
pnpm -C frontend lint
pnpm -C frontend build
pnpm -C frontend test -- --run no-execution-wording
py -3.11 -m pytest tests/app/test_safety_invariants.py tests/app/test_openapi_forbidden_paths.py -q
```

---

## PR 1 — Document theme tokens

**Branch:** `docs/claude-design-handoff` *(this PR)*

**Commit tag:** `docs(design): add Claude Design handoff package`

**Scope:** docs-only, no runtime changes.

**Files:**
- add `docs/design/claude_design_theme_handoff.md`
- add `docs/design/claude_design_implementation_handoff.md`
- add `docs/design/claude_design_screen_map.md`
- add `docs/design/claude_design_pr_breakdown.md`

**Acceptance:**
- Theme strategy documented; Amber/Navy/Crimson roles clear
- Safety constraints documented
- Token values match Claude Design export verbatim
- `validate_safety_config.py` passes
- No runtime files touched
- No frontend build changes
- No backend changes

---

## PR 2 — Add CSS variables

**Commit tag:** `feat(terminal): theme tokens`

**Scope:** Convert terminal inline color literals to CSS variables. Amber remains default. No visual semantic changes. No new components, no new buttons, no copy changes, no backend changes.

**Files likely touched:**
- add `frontend/src/styles/tokens.css` — Amber at `:root`, Navy at `[data-theme="navy"]`
- add `frontend/src/styles/severity.css` — severity ramp + `[data-severity="crimson"]` override
- update `frontend/src/components/terminal/terminal.css` — `@import "../../styles/tokens.css"; @import "../../styles/severity.css";` at top
- update any inline hex literals in `TerminalShell.tsx`, `AuditEventsPreview.tsx`, `AIWorkspacePanel.tsx`, `RiskManagerPage.tsx` → `var(--…)`

**Acceptance:**
- Default load shows Amber palette exactly as before — visual snapshot diff ≤ 2 px per region
- Adding `data-theme="navy"` on `<html>` (devtools) instantly switches surfaces + accent to navy; severity ramp unchanged
- Adding `data-severity="crimson"` turns NO_TRADE chip + blocked capability cards from `#F87171` to `#DC2626`; success/info/warning unchanged
- No new components
- No new buttons
- No copy changes
- No backend changes
- `pnpm -C frontend build` passes
- `validate_safety_config.py` passes

**Validation:**

```bash
pnpm -C frontend typecheck && pnpm -C frontend lint
pnpm -C frontend build

# forbid inline hex sneaking back in
git grep -nE "#([0-9a-fA-F]{3}){1,2}\b" -- "frontend/src/components/terminal/*.tsx"
# expected: empty (all colors come from CSS variables)
```

---

## PR 3 — Optional Navy palette support

**Commit tag:** `feat(terminal): navy theme`

**Scope:** Add static `data-theme="navy"` support. No user-facing switcher yet unless separately approved.

**Files likely touched:**
- `frontend/src/styles/tokens.css` — confirm Navy block is complete
- optionally `frontend/src/components/terminal/TerminalShell.tsx` — apply `data-theme` from config/env

**Acceptance:**
- Amber remains default for all users
- Navy changes palette only — no semantic, copy, or functional changes
- No backend preference route
- No localStorage persistence
- No user-facing theme switcher button
- No mutation controls
- `validate_safety_config.py` passes

---

## PR 4 — Scanner/watchlist visual polish

**Commit tag:** `refactor(terminal): typed cards`

**Scope:** Improve visual clarity of scanner and watchlist. Use existing demo/fallback data. No new trading instructions.

**Files likely touched:**
- add `components/terminal/WatchlistTable.tsx`
- add `components/terminal/SignalPreviewCard.tsx`
- add `components/terminal/AuditEventCard.tsx`
- update `components/terminal/AIWorkspacePanel.tsx` — list items → `<SignalPreviewCard/>`, detail uses LockedField pattern
- update `components/terminal/AuditEventsPreview.tsx` — rows → `<AuditEventCard compact/>`
- update `pages/TerminalPage.tsx` — adds 5-tile KPI strip + WatchlistTable above AIWorkspacePanel
- update `lib/scannerPreviewApi.ts` — typed `Signal` model

**Acceptance:**
- Advisory labels only: `WATCH` / `HOLD` / `LONG_SETUP` / `SHORT_SETUP` / `NO_TRADE`
- `HUMAN REVIEW REQUIRED` badge remains visible on held signals
- No `buy` / `sell` / `execute` wording anywhere
- `NO_TRADE` reference sizing LockedField value is literally *"Suppressed — policy block"* — never a number
- WatchlistTable has no "Trade", "Open", "Position" affordance — confirmed by snapshot test
- SignalChip type union throws at build time on invalid states
- `pnpm -C frontend test -- --run no-execution-wording` passes
- `validate_safety_config.py` passes

**Validation:**

```bash
pnpm -C frontend typecheck
pnpm -C frontend test -- --run no-execution-wording
pnpm -C frontend test -- --run WatchlistTable
curl -s localhost:8000/api/signals | jq '.[0] | keys'
# expected: ["id","sym","state","conf","thesis","factors","invalidation","riskHint","horizon","emittedAt"]
```

---

## PR 5 — README screenshot pack

**Commit tag:** `docs(terminal): screenshot pack`

**Scope:** `docs/assets/screenshots` only. Demo/read-only screenshots. No secrets. No account IDs.

**Files likely touched:**
- add `frontend/docs/README-screenshots/01–12-*.png` (12 images, 1920×1080)
- update `README.md` — hero image, feature grid linking screenshots
- add `scripts/capture-screenshots.ts` — Playwright capture for all 12 routes; deterministic via `VITE_DEMO_SEED=2026-05-16`
- add `frontend/src/pages/ClosedBetaLanding.tsx` — public route at `/`, no app shell
- add `frontend/src/pages/PortfolioReportsPage.tsx` — placeholder

**Acceptance:**
- All screenshots show safety badges (`DEMO DATA · READ ONLY` visible)
- No live account data in any screenshot
- No execution controls visible in any screenshot
- `README.md` hero image above the fold with canonical safety string
- Landing page hero contains literal: `autotrade=false · dry_run=true · read_only=true · live_orders_blocked=true · max_risk≤1%`
- Landing "Refuses to do" list contains all 6 prohibition items
- Capture script refuses to run unless `VITE_DEMO_MODE=true`
- `validate_safety_config.py` passes

**Validation:**

```bash
pnpm -C frontend exec playwright install --with-deps chromium
pnpm -C frontend exec tsx scripts/capture-screenshots.ts
ls frontend/docs/README-screenshots/   # expect 12 files

pnpm exec markdownlint README.md
pnpm -C frontend test -- --run ClosedBetaLanding.copy.test
```

---

## Deferred — Theme switcher (UI)

**Do not implement yet.**

If implemented later:
- Must default to Amber for all new users
- Must not require backend mutation initially — local env/config only
- No server-side preference route unless specifically approved and reviewed
- No localStorage-only persistence (closed-beta auditors must see the same UI as everyone else)
- Must be separately reviewed with its own PR

If a server-side preference route is ever added:
- Scope strictly to `{theme, severity}` — no other keys
- Preferences PATCH must refuse any key not in allow-list (422 + audit event `preference_rejected`)
- CI matrix tests all 4 combinations (Amber+default, Amber+crimson, Navy+default, Navy+crimson)

---

## Safety constraints (all PRs)

These must hold across every PR in this series:

| Constraint | Enforcement |
|---|---|
| No trading buttons | `no-execution-wording.test.tsx` CI guard |
| No execution controls | No `onClick` handler with a network mutation in PR 2 |
| Severity meanings preserved | CI matrix runs posture + wording tests for each theme combo |
| No copy changes | Wording audit in CI for each PR |
| No new mutation endpoints (except reconnect-dry) | `test_no_mutation_routes.py` CI guard |
| `autotrade=false` | `test_posture.py` CI guard |
| `live_orders_blocked=true` | `test_posture.py` CI guard |
| `dry_run=true` | `test_posture.py` CI guard |
| `read_only=true` | `test_posture.py` CI guard |
| `max_risk_pct ≤ 1.0` | `test_posture.py` CI guard |
| No secrets / account IDs committed | Pre-commit hook + screenshot capture requires `VITE_DEMO_MODE=true` |
