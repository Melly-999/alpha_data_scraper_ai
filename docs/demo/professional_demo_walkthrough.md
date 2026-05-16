# Professional Demo Walkthrough — MellyTrade Read-Only AI Ops Layer

A scripted walkthrough that takes a viewer (recruiter, reviewer, prospective
employer, OpenAI Showcase visitor) from "what is this?" to "I understand the
safety model and the AI explainability layer" in roughly **8 minutes**.

> **Single most important framing:** this is a **read-only AI operations
> layer** for a trading bot, not a live trading bot. Every page is GET-only.
> Every order-shaped row is prefixed `[DRY-RUN]`. The execution path is not
> wired up. `autotrade=false`, `dry_run=true`, `read_only=true`,
> `live_orders_blocked=true`, `max_risk_per_trade ≤ 1%`.

---

## 0. Pre-flight (30 seconds)

Confirm the demo state before sharing the screen:

| Check | Where | Expected |
|---|---|---|
| Backend running | `http://localhost:8000/health` | `200`, `dry_run=true`, `auto_trade=false` |
| Frontend running | `http://localhost:5173/dashboard` | Dashboard renders |
| Safety banner | Top of any page | "DRY RUN · READ-ONLY MODE · LIVE ORDERS BLOCKED · MAX RISK ≤ 1%" |
| No "LIVE" indicator anywhere | All pages | Confirmed absent |

If any check fails: **stop**, fix locally, restart.

---

## 1. Dashboard (1 min) — "Here's what you're looking at"

URL: `/dashboard`

Talking points, in order:

1. **The safety banner** at the top is not decorative — it reflects live
   FastAPI state pulled from `/api/risk/config` and `/api/local-checklist`.
   It cannot be turned off from the UI.
2. **System Status** card shows MT5, Claude, NewsAPI dependency state. All
   degrade gracefully — there is no path where a missing dependency triggers
   an order.
3. **Equity curve + account overview** are seeded fixture data. The repo
   does not ship with broker credentials, and no broker connection is
   attempted at this layer.
4. **Activity feed** — point out that every advisory row is prefixed
   `[DRY-RUN]` and ends with "no order placed". This is intentional: the
   demo data is shaped so a screenshot cannot be misread as live trading.

---

## 2. Signals page (2 min) — "AI decision flow, explainable"

URL: `/signals`

This is the core of the milestone-100 layer.

### 2.1 Signal Review card
- The table is populated by `GET /api/signals`. No interaction here places
  any order — clicking a row only opens the read-only drawer.

### 2.2 Decision History card  ← **DEMO HIGHLIGHT**
- Point at the `read-only` and `live data` / `seed data` badges (SUPA-012,
  SUPA-013). They show whether the panel is reading from real Supabase rows
  or the in-memory seed fixture. **Both paths are GET-only.**
- Point at the **freshness label** (SUPA-013): `polling…`, `updated HH:MM:SS`,
  or `updated HH:MM:SS · stale`. Cite the 90s threshold from SUPA-009.
- **Demonstrate the date range controls (SUPA-015):**
  1. Click `1H` chip → table re-fetches with `?from_date=<iso>`
  2. Click `7D` chip → wider window
  3. Set the custom `From` / `To` pickers → URL params update
  4. Click `Clear dates` to return to the quick range
  5. Try a future-only window → empty state reads "No decisions in the
     selected range. Try widening the date range or clearing filters."
- Show the **per-row** badges: dry-run, blocked, watch-only,
  dry_run_allowed. Each is a real audit record persisted to Supabase.

### 2.3 Signal Lifecycle card
- Each lifecycle entry shows the safety steps every signal walks through:
  `signal_received → confidence_checked → risk_checked →
  broker_safety_checked → dry_run_decision → blocked_or_allowed_reason →
  audit_event_reference`.
- The `audit_event_reference` row is correlated back to a row in the
  audit feed — explain this is how an operator would trace any decision.

### 2.4 Drawer — open one signal  ← **DEMO HIGHLIGHT**
- Click any row to open the signal drawer.
- Show the new **AI Reasoning panel (DATA-002)**:
  - "Why this signal?" narrative
  - Confidence breakdown vs the 70% review threshold
  - "Why blocked?" if applicable
  - Risk gates triggered (failed gates expanded, passed gates collapsed)
  - "Human review required" framing
  - Safety badges: `DRY RUN ONLY`, `READ ONLY`, `HUMAN REVIEW REQUIRED`,
    `RISK BLOCKED`
- Click `Collapse` / `Expand` to show the panel is a pure UI affordance —
  it never makes a network call.

---

## 3. Audit Trail (1 min) — "How we know nothing happened"

URL: `/audit`

- The feed combines startup events, terminal load events, risk policy
  events, broker disconnection state, MT5 disconnection state, scanner
  evaluation summaries, and stale-data warnings.
- Each row has an explicit `safety_note` explaining why it is safe.
- Filter by severity → show how the operator surfaces only warnings/errors.

---

## 4. Supabase Observability (1 min) — "Where the data lives"

- Open `docs/supabase/migration_runbook.md` in another tab.
- Talking points:
  - `signal_decisions` table has RLS enabled (deny-all default, SUPA-012).
  - The frontend NEVER reads Supabase directly. All reads go
    `frontend → FastAPI → service_role → Supabase`.
  - Service role is not exposed to the browser.
  - Every safety field is enforced by CHECK constraints AND re-asserted
    on the read path. The DB cannot return a row with `dry_run=false`.

---

## 5. Safety posture recap (1 min) — "Why this is safe to demo publicly"

Cite the contract verbatim:

```
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max_risk_per_trade <= 0.01
no POST/PUT/PATCH/DELETE on the signal surface
no broker execution routes registered
no MT5 execution paths invoked
no service_role exposure to the browser
no order placement code path
no interactive trading controls
```

Tests that enforce this:

- `tests/app/test_safety_invariants.py`
- `tests/app/test_openapi_forbidden_paths.py`
- `scripts/validate_safety_config.py`
- `scripts/validate_local.ps1`

---

## 6. Closing (30 sec) — "What this proves"

> "This is what a *responsible* AI-driven trading workstation looks like
> when an engineer is still in the seat. The AI does the reasoning; the
> human signs every order; the system makes it impossible to skip that
> step. Read-only by design, not by accident."

---

## Screenshot Capture Flow

Use this section when taking the DEMO-002 screenshot pack. It maps each
required screenshot to the exact demo step where that state is natural.
Full per-screenshot requirements live in
[`demo_screenshot_checklist.md`](demo_screenshot_checklist.md).

### Recommended capture sequence

| Order | Filename | Demo step | Setup |
|---|---|---|---|
| 1 | `07-demo-overview.png` | Before step 2 | `/signals`, ALL range, no drawer, all three cards visible |
| 2 | `01-terminal-ai-workspace.png` | Step 1 (Dashboard) | `/dashboard`, safety banner visible, activity feed loaded |
| 3 | `02-signal-decision-history-filters.png` | Step 2.2 (1H chip) | `/signals`, click 1H chip, wait for freshness label |
| 4 | `05-supabase-status-and-stale-indicators.png` | Step 2.2 (badges) | `/signals`, Decision History badges: `read-only` + `live data`/`seed data` |
| 5 | `03-signal-reasoning-panel.png` | Step 2.4 (drawer) | Open drawer on a ≥80% confidence signal, expand AI Reasoning panel |
| 6 | `04-audit-feed-safety-events.png` | Step 3 (Audit Trail) | `/audit`, scroll to show `stale_data_warning` + `scanner_evaluated` + `risk_blocked` |
| 7 | `06-broker-readonly-guardrails.png` | Step 5 (Safety recap) | `/risk` or `/dashboard`, safety flag values visible |

### Navigation flow for capture

1. Open `/dashboard`. Confirm safety banner. **Capture 01-terminal-ai-workspace.png**.
2. Switch to `/signals`. Set Decision History to **ALL**. Scroll to show all
   three cards. **Capture 07-demo-overview.png**.
3. Still on `/signals`. Click **1H** chip. Wait for freshness label.
   **Capture 02-signal-decision-history-filters.png**.
4. Still on `/signals`. Frame the Decision History badges.
   **Capture 05-supabase-status-and-stale-indicators.png**.
5. Click a signal row with confidence ≥ 80% in the Signal Review card.
   Drawer opens. Scroll to AI Reasoning panel. Expand if collapsed.
   **Capture 03-signal-reasoning-panel.png**.
6. Switch to `/audit`. Scroll to show `stale_data_warning`,
   `scanner_evaluated`, `risk_blocked` rows together.
   **Capture 04-audit-feed-safety-events.png**.
7. Switch to `/risk`. Frame the safety flag summary.
   **Capture 06-broker-readonly-guardrails.png**.

### How to explain read-only safety posture during a live demo

When a reviewer asks "is this doing real trading?":

1. Point at the safety banner: "This is not decorative — it reflects live
   FastAPI state pulled from `/api/risk/config` and cannot be turned off
   from the UI."
2. Show the Decision History panel: "Every row is labelled `dry_run_allowed`,
   `blocked`, or `watch_only` — there is no `executed` state."
3. Open a signal drawer: "The AI Reasoning panel has four safety badges.
   `DRY RUN ONLY` and `READ ONLY` are always present regardless of the
   signal outcome."
4. Cite the test suite: "1059 tests run green. Thirty-nine of them are
   dedicated safety-invariant assertions that fail the build if any route,
   schema, or config drifts toward execution."

### How to explain Supabase observability

- "Signal decisions are persisted to `signal_decisions` in Supabase with
  RLS deny-all by default — the frontend cannot read them directly."
- "FastAPI reads via `service_role` server-side. The key never reaches
  the browser. The frontend only sees the shaped JSON response."
- "When Supabase is offline, the service degrades to seed fixtures and
  surfaces an amber `seed data` badge — no errors, no broken UI."

### How to explain fallback and degraded states

- **`seed data` badge (amber)**: Supabase returned no rows or is
  unreachable. The in-memory seed fixture is serving requests.
  This is the expected state without a Supabase connection.
- **`degraded` badge (amber)**: At least one record in the current view
  has `risk_status = blocked` or `warn`. This is normal — it means the
  risk gates are working.
- **Freshness label `· stale`**: Last successful poll was >90 seconds ago.
  Display-only warning; no execution semantics.

---

## Common questions to be ready for

| Q | A |
|---|---|
| "Can it actually trade?" | The execution adapter exists in `mt5_trader.py`, but no route, no button, and no frontend control reaches it. Every API surface is GET-only. |
| "What if Supabase is offline?" | Reader degrades gracefully — service falls back to in-memory seed fixtures and surfaces a `seed data` badge. No errors propagate. |
| "What if Claude is offline?" | Reasoning panel renders without `claude_response`; the rest of the layer works unchanged. |
| "How do you know it's actually dry-run?" | Three independent layers: route-level safety flags, response model defaults, and read-path re-enforcement of every safety field. Two of those layers cannot be bypassed by changing a single file. |
