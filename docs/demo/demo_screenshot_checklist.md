# Demo Screenshot Checklist — MellyTrade Read-Only AI Ops Layer (DEMO-002)

Curated capture plan for the MERGE #100 milestone. Every screenshot is
**safe to publish on GitHub, LinkedIn, OpenAI Showcase, or a portfolio
site** because every page is read-only.

Companion docs:
- Capture runbook: [`demo_002_capture_runbook.md`](demo_002_capture_runbook.md)
- Demo walkthrough: [`professional_demo_walkthrough.md`](professional_demo_walkthrough.md)
- Asset directory: [`../assets/screenshots/README.md`](../assets/screenshots/README.md)
- Architecture: [`../architecture/milestone_100_readonly_ai_ops.md`](../architecture/milestone_100_readonly_ai_ops.md)

---

## Pre-shot setup

1. **Backend on**: `py -3.11 -m uvicorn app.main:app --reload`
2. **Frontend on**: `cd frontend && npm run dev`
3. **Hard refresh** each page before capturing (Ctrl+Shift+R).
4. **Viewport**: 1440×1000 px minimum — 1600×1000 px preferred.
5. **Browser zoom**: 90–100%. Do not use 80% or 110%.
6. **DevTools closed** unless the shot specifically shows the network panel.
7. **Theme**: default dark — do not switch.
8. **Safety banner check**: confirm it reads `DRY RUN · READ-ONLY MODE · LIVE ORDERS BLOCKED · MAX RISK ≤ 1%` before every shot.

---

## Capture sequence and requirements

### Shot 01 — Full AI workspace overview

| Field | Value |
|---|---|
| **Filename** | `01-terminal-ai-workspace.png` |
| **Route** | `/dashboard` |
| **Capture order** | First |
| **Viewport** | 1600×1000 px, zoom 100% |

**Visible elements required:**
- Safety banner at the top — full text visible
- System Status card (MT5, Claude, NewsAPI dependency health)
- Equity curve / account overview section
- Activity feed with at least two rows, each prefixed `[DRY-RUN]`

**Pass criteria:**
- [ ] Safety banner fully visible
- [ ] No `LIVE` indicator anywhere
- [ ] Activity feed rows show `[DRY-RUN]` prefix
- [ ] No account IDs in equity/account card

**Fail if:**
- Safety banner is cut off or scrolled out of view
- Any element says `LIVE`, `executed`, or `order placed`
- Real account numbers are visible

---

### Shot 02 — Decision History with date filters

| Field | Value |
|---|---|
| **Filename** | `02-signal-decision-history-filters.png` |
| **Route** | `/signals` |
| **Capture order** | Second |
| **Viewport** | 1600×1000 px, zoom 90% |

**Setup before capture:**
1. Navigate to `/signals`.
2. Click the **1H** quick-range chip in the Decision History card.
3. Confirm the freshness label reads `updated HH:MM:SS` (not `polling…`).
4. Confirm `read-only` badge is visible.

**Visible elements required:**
- Decision History card header with `dry-run` badge
- Quick-range chips (1H / 4H / 24H / 7D / ALL) with **1H active** (highlighted)
- Date range summary label: `range: last 1h`
- Freshness label: `updated HH:MM:SS`
- Filter controls: Symbol, Decision, Risk status, Direction
- At least three decision rows in the table

**Pass criteria:**
- [ ] 1H chip is visually active (highlighted/selected)
- [ ] `read-only` badge visible
- [ ] Freshness label present
- [ ] Filter controls visible
- [ ] Table rows visible

**Fail if:**
- ALL chip is active instead of 1H
- No rows visible (use a wider range if seed data is outside 1H window)
- Freshness label missing

---

### Shot 03 — AI Reasoning panel (dry-run-allowed signal)

| Field | Value |
|---|---|
| **Filename** | `03-signal-reasoning-panel.png` |
| **Route** | `/signals` (drawer open) |
| **Capture order** | Third |
| **Viewport** | 1600×1000 px, zoom 90% |

**Setup before capture:**
1. Navigate to `/signals`.
2. In the Signal Review table, click a row with `confidence ≥ 80%` and `direction = BUY`.
3. The drawer opens on the right. Scroll down inside the drawer until the AI Reasoning panel is fully visible.
4. Confirm the panel is expanded (not collapsed).

**Visible elements required:**
- Drawer open on the right side
- `AI Reasoning` panel header with sub-caption "Display-only explanation. No order is placed from this panel."
- All four safety badges visible: `DRY RUN ONLY`, `READ ONLY`, `HUMAN REVIEW REQUIRED` (if confidence < 70%), `RISK BLOCKED` (if blocked)
- At minimum: `DRY RUN ONLY` + `READ ONLY` badges always present
- "Why this signal?" section with narrative text
- "Confidence breakdown" section with confidence value and band badge
- "Human review required" section with `autotrade=false`, `dry_run=true` text

**Pass criteria:**
- [ ] `DRY RUN ONLY` badge visible
- [ ] `READ ONLY` badge visible
- [ ] Reasoning narrative present (not "No narrative reasoning available.")
- [ ] Confidence value and band badge visible
- [ ] "Human review required" section visible

**Fail if:**
- Panel is collapsed
- Safety badges not visible
- Panel shows "No reasoning data" for the selected signal

---

### Shot 04 — Audit feed with operational safety events

| Field | Value |
|---|---|
| **Filename** | `04-audit-feed-safety-events.png` |
| **Route** | `/audit` |
| **Capture order** | Fourth |
| **Viewport** | 1440×900 px, zoom 100% |

**Visible elements required:**
- Audit event feed header
- At least one `stale_data_warning` event row
- At least one `scanner_evaluated` event row
- At least one `risk_blocked` event row
- Event rows showing: `id`, `timestamp`, `type`, `severity`, `safety_note`
- `dry_run=true`, `auto_trade=false`, `read_only=true` in the response or visible feed header

**Pass criteria:**
- [ ] Three distinct event types visible: `stale_data_warning`, `scanner_evaluated`, `risk_blocked`
- [ ] Each row shows a `safety_note`
- [ ] No row shows `order placed` or `executed`

**Fail if:**
- Feed is empty
- Event types listed above are not visible in the captured frame

---

### Shot 05 — Supabase status and stale data indicators

| Field | Value |
|---|---|
| **Filename** | `05-supabase-status-and-stale-indicators.png` |
| **Route** | `/signals` |
| **Capture order** | Fifth |
| **Viewport** | 1600×1000 px, zoom 90% |

**Setup before capture:**
1. Navigate to `/signals`.
2. Focus on the Decision History card.
3. If Supabase is connected and returning data: the badge reads `live data` (green).
4. If Supabase is offline (expected in local demo): the badge reads `seed data` (amber).
5. Wait until the freshness label shows a timestamp (not `polling…`).

**Visible elements required:**
- Decision History card
- `read-only` badge (green)
- `live data` (green) **or** `seed data` (amber) badge — either is valid and safe
- `degraded` badge (amber) if any records have `risk_status = blocked` or `warn`
- Freshness label: `updated HH:MM:SS` or `updated HH:MM:SS · stale`

**Pass criteria:**
- [ ] `read-only` badge visible
- [ ] `live data` or `seed data` badge visible — no unlabeled state
- [ ] Freshness label visible with timestamp

**Fail if:**
- Badges are not visible (card still loading)
- Freshness label shows `polling…` only (wait for first poll to complete)

---

### Shot 06 — Broker read-only guardrails

| Field | Value |
|---|---|
| **Filename** | `06-broker-readonly-guardrails.png` |
| **Route** | `/risk` or `/dashboard` |
| **Capture order** | Sixth |
| **Viewport** | 1440×900 px, zoom 100% |

**Visible elements required (use whichever route shows more):**
- `dry_run=true` label
- `auto_trade=false` label
- `read_only=true` label
- `live_orders_blocked=true` or `LIVE ORDERS BLOCKED` banner
- `max_risk_per_trade ≤ 1%` value
- Broker status card showing disconnected / paper state (not live)

**Pass criteria:**
- [ ] At least three of the five safety flag values visible
- [ ] No text says `LIVE` or `connected to live broker`
- [ ] No order placement controls visible

**Fail if:**
- Safety flag values not visible
- Any control resembles an order ticket

---

### Shot 07 — Full Signals page overview

| Field | Value |
|---|---|
| **Filename** | `07-demo-overview.png` |
| **Route** | `/signals` |
| **Capture order** | Seventh (or first if used as hero shot) |
| **Viewport** | 1600×1000 px, zoom 80–90% to show all three cards |

**Setup before capture:**
1. Navigate to `/signals`.
2. Scroll to show all three cards: Signal Review, Decision History, Signal Lifecycle.
3. Set Decision History to **ALL** range so all seed records are visible.
4. Do not open any drawer.

**Visible elements required:**
- Page header: "Signal Review" with read-only badge
- Signal Review card with at least two rows
- Decision History card with summary grid visible
- Signal Lifecycle card with at least two rows
- All three cards visible in one frame (zoom out if needed)

**Pass criteria:**
- [ ] All three cards visible without scrolling
- [ ] Decision History shows summary grid (total, blocked, dry-run-allowed counts)
- [ ] Page header visible with read-only label

**Fail if:**
- Only one or two cards visible
- Summary grid not visible in Decision History

---

## Redaction checklist (check every screenshot before committing)

Run through this list for every file before `git add`:

- [ ] No secrets, API keys, or tokens visible
- [ ] No Supabase `service_role` key values (format: `eyJ…`)
- [ ] No broker account numbers or login credentials
- [ ] No order IDs or execution IDs
- [ ] No personal data (email, name, phone)
- [ ] Safety banner visible and reads correctly
- [ ] No `LIVE` indicator anywhere
- [ ] No text saying an order was placed or executed
- [ ] Browser address bar does not show localhost credentials
- [ ] Browser DevTools are closed (unless intentionally showing network panel)

If any item fails: **do not commit the screenshot**. Recapture or crop.

---

## Optional / nice-to-have shots

| # | Filename | Route | Subject |
|---|---|---|---|
| 08 | `08-empty-state-future-range.png` | `/signals` | Future-only date range → "No decisions in the selected range" empty state |
| 09 | `09-lifecycle-detail.png` | `/signals` | Signal lifecycle steps from `signal_received` through `audit_event_reference` |
| 10 | `10-degraded-seed-badge.png` | `/signals` | Decision History when seed path active: `seed data` (amber) + `degraded` |
| 11 | `11-risk-manager.png` | `/risk` | Risk manager surface — `dry_run=true`, `auto_trade=false`, gates listed |
| 12 | `12-audit-safety-severity.png` | `/audit` | Audit feed filtered to severity=safety — every row shows safety_note |

---

## Captioning template (for external publication)

> *MellyTrade Read-Only AI Ops Layer — `[page name]`. Display-only:
> `autotrade=false`, `dry_run=true`, `read_only=true`,
> `live_orders_blocked=true`, max risk ≤ 1%. No live trading. No live
> broker execution. Open-source on GitHub.*

---

## Output destinations

| Destination | Required shots | Format |
|---|---|---|
| `README.md` Screenshots section | 01, 02, 03, 04, 07 | PNG, 1440×900 max |
| `docs/assets/screenshots/` | All required + optional | PNG, lossless |
| LinkedIn / portfolio | 02, 03, 07 | PNG or WebP |
| OpenAI Showcase | 01, 02, 03 | PNG, 16:9 |

---

## What NOT to screenshot

- Browser DevTools showing real broker credentials (none exist in this
  repo, but never habituate to that risk).
- Any page showing `LIVE`, `executed`, or `order placed` — the system
  never produces those strings; if a screenshot contains them, something
  is wrong.
- API request bodies showing service-role keys (no API key path exists
  in the frontend; verify before capture).
- The `/risk` page if `config.json` has been manually edited to flip a
  safety flag for local testing.
