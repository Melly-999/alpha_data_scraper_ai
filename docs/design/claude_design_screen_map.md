# Claude Design Screen Map

## Source

Generated from Claude Design export stored outside the repo:

```
C:\AI\MellyTrade_Workspace\03_Docs\ClaudeDesign\MellyTrade_Closed_Beta_Demo_UI_Pack
```

Raw export files are intentionally not committed. The prototype (`MellyTrade Prototype.html`, `MellyTrade Canvas.html`) contains 8 screens in hash-router format.

---

## Overview

| # | Route | Screen | Page file |
|---|---|---|---|
| 1 | `/#/overview` | Terminal Overview | `TerminalPage.tsx` |
| 2 | `/#/scanner` | AI Workspace · Signal Scanner | `AIWorkspacePanel.tsx` |
| 3 | `/#/audit` | Audit & Events Rail | `AuditEventsPreview.tsx` |
| 4 | `/#/risk` | Risk Manager | `RiskManagerPage.tsx` |
| 5 | `/#/broker` | Broker Status | (new `BrokerPage.tsx`) |
| 6 | `/#/portfolio` | Portfolio · Reports | (new `PortfolioReportsPage.tsx`) |
| 7 | `/#/settings` | Safety Posture / Settings | (new `SettingsPage.tsx`) |
| 8 | `/#/landing` | Closed Beta Landing | `ClosedBetaLanding.tsx` |

All screens: **no execution controls, no order buttons, no live broker control, read-only/dry-run posture preserved.**

---

## Screen 1 — Terminal Overview

**Route:** `/#/overview`

**Purpose:** Primary landing screen for the closed-beta terminal. Gives a status summary of all running systems and latest signal previews at a glance.

**Key components:**
- `TerminalHeader` — sticky topbar (52 px), breadcrumb, status ticker, service pills, UTC clock
- `DemoModeBanner` — non-dismissible ribbon under topbar
- KPI strip — 5 tiles: Portfolio Value (locked), Signals Scanned, Active Setups, Posture Uptime, Last Scan
- `WatchlistTable` — symbol tape with SignalChip and ConfidenceBar columns
- `BrokerStatusCard` (summary) — SAFE · DISCONNECTED pill, capabilities matrix
- Supabase health summary card
- `AuditEventCard` stream — recent 5 events, link to full audit rail
- Signal preview strip — top 3 `SignalPreviewCard` components

**Safety notes:**
- No execution controls
- No order buttons
- No live broker control
- KPI "Portfolio Value" field is a `LockedField` (padlock, `cursor:not-allowed`)
- All market data is demo/simulated
- `DEMO DATA · READ ONLY · DRY RUN ACTIVE · LIVE ORDERS BLOCKED` badges visible

**Likely repo files:**
- `frontend/src/pages/TerminalPage.tsx`
- `frontend/src/components/terminal/TerminalShell.tsx`
- `frontend/src/components/terminal/WatchlistTable.tsx`
- `frontend/src/lib/terminalApi.ts`

---

## Screen 2 — AI Workspace / Signal Scanner

**Route:** `/#/scanner`

**Purpose:** Filterable list of AI-generated research signals with rationale detail and factor contribution chart. The primary research surface of the terminal.

**Key components:**
- `AIWorkspacePanel` — filterable signal list
- `SignalPreviewCard` — per-signal card (SYM + SignalChip + confidence + thesis preview)
- Signal detail panel — thesis text, factor contributions chart, LockedField cards for invalidation / reference sizing / horizon
- Filter bar — by signal state (WATCH / HOLD / NO_TRADE / LONG_SETUP / SHORT_SETUP / ALL)
- `HUMAN REVIEW REQUIRED` badge on high-confidence previews held for review
- `useSignalPreviews()` hook → `GET /api/signals`

**Safety notes:**
- No execution controls
- No order buttons
- No live broker control
- Signal detail shows "Reference sizing" as `LockedField` — for `NO_TRADE` signals the value is literally *"Suppressed — policy block"* never a number
- Factor contributions are labeled "contribution" never "buy signal"
- SignalChip type union enforced at build time — only 5 safe states permitted
- `DEMO DATA · READ ONLY · HUMAN REVIEW REQUIRED` badges visible

**Likely repo files:**
- `frontend/src/components/terminal/AIWorkspacePanel.tsx`
- `frontend/src/components/terminal/SignalPreviewCard.tsx`
- `frontend/src/lib/scannerPreviewApi.ts`

---

## Screen 3 — Audit & Events Rail

**Route:** `/#/audit`

**Purpose:** Live, filterable, pausable event stream. Shows every audit event emitted by the system with severity, timestamp, source, and kind. Full transparency into system behavior.

**Key components:**
- `AuditEventsPreview` — full-page event rail
- `AuditEventCard` — severity left rail (2 px), time/source column, `kind` in mono, message, optional safety note
- Filter bar — by severity (success / info / warning / degraded / all)
- Pause / Resume control — pausing halts stream rendering; server continues recording
- Severity legend
- `useAuditStream(paused)` hook → `GET /api/events` (SSE), append-only buffer, cap 200

**Empty/degraded states:**
- Paused: "stream paused · 0 new events" — press RESUME to resume
- Degraded: health probe unreachable → generic "Health probe unreachable" row with severity=degraded

**Safety notes:**
- No execution controls
- No order buttons
- No live broker control
- Read-only view of server-recorded events
- `READ ONLY` badge visible

**Likely repo files:**
- `frontend/src/components/terminal/AuditEventsPreview.tsx`
- `frontend/src/components/terminal/AuditEventCard.tsx`
- `frontend/src/lib/terminalApi.ts`

---

## Screen 4 — Risk Manager (read-only)

**Route:** `/#/risk`

**Purpose:** Display-only policy values and runtime posture. Proves the safety posture visually. Intentionally has no editable controls.

**Key components:**
- `RiskMetricCard` — always `locked: true`. Renders as `LockedField` (padlock icon, `cursor:not-allowed`). Hover tooltip: "Why read-only — compile-time constant + 60 s heartbeat"
- `RiskGuardrailsCard` — max risk ≤ 1% NAV, position limits, correlation limits — all LockedFields
- "Buttons that intentionally don't exist" educational card — explains what the product refuses to do
- Runtime posture display: `autotrade=false · dry_run=true · read_only=true · live_orders_blocked=true · max_risk_pct≤1.0`
- `useTerminalPosture()` hook → `GET /api/posture`

**Safety notes:**
- No execution controls
- No order buttons
- No live broker control
- Zero `<form>`, zero `<input>` without `readOnly`, zero `<button type="submit">` — enforced by snapshot test
- `READ ONLY · LIVE ORDERS BLOCKED` badges visible

**Likely repo files:**
- `frontend/src/pages/RiskManagerPage.tsx`
- `frontend/src/components/terminal/RiskMetricCard.tsx`
- `frontend/src/lib/terminalApi.ts`

---

## Screen 5 — Broker Status (safe-disconnected)

**Route:** `/#/broker`

**Purpose:** IBKR adapter status display. Proves the broker is in a permanent safe-disconnected state. Simulate-reconnect demo shows the policy guard firing.

**Key components:**
- `BrokerStatusCard` — permanent `SAFE · DISCONNECTED` pill
- Capabilities matrix: `place_order`, `cancel_order`, `modify_order` always rendered as *blocked*
- Supabase health card — reads p95 latency + threshold; degraded state turns card border red + "no write attempts were made" note
- "Simulate reconnect" button — OK, always resolves to `safe-disconnected` via `POST /api/broker/reconnect-dry`
- Result appended to audit rail as `broker_safe_disconnected` event
- `useBrokerStatus()` hook → `GET /api/broker`

**Degraded states:**
- SAFE · DISCONNECTED (normal/expected): amber pill, dashed empty art "order paths unreachable · by design"
- Supabase degraded: card border red, "Reads slow. UI continues read-only with cached values. No write attempts were made during the degraded window."

**Safety notes:**
- No execution controls
- No live broker connect controls — "Connect live" is explicitly forbidden
- "Simulate reconnect" is permitted; it never flips `live_orders_blocked`
- `SAFE · DISCONNECTED` badge visible
- `live_orders_blocked=true` is a compile-time constant

**Likely repo files:**
- `frontend/src/components/terminal/BrokerStatusCard.tsx`
- `frontend/src/lib/brokerApi.ts` — exports only `useBrokerStatus()` and `useSimulateReconnectDry()`

---

## Screen 6 — Portfolio / Reports (placeholder)

**Route:** `/#/portfolio`

**Purpose:** Placeholder for the post-beta research journal milestone. MellyTrade does not execute trades, so there are no positions to display — this is intentional.

**Key components:**
- `PortfolioReportsPlaceholder` — "0 positions · never any in this build" empty state
- Placeholder card explaining the next milestone: signal-vs-price-action attribution journal
- `DEMO DATA · READ ONLY` badges visible

**Empty state copy:**
> **This is intentional.** MellyTrade does not execute trades, so there are no positions to display. The journal milestone will introduce signal-vs-price-action attribution here.

**Safety notes:**
- No execution controls
- No order buttons
- No live broker control
- No position data — zero positions by design

**Likely repo files:**
- `frontend/src/pages/PortfolioReportsPage.tsx` (new)

---

## Screen 7 — Settings / Safety Posture

**Route:** `/#/settings`

**Purpose:** Shows every safety flag as a `LockedToggle`. Locked toggles are visually switch-shaped but `cursor:not-allowed` with tooltips explaining "compile-time constant". Compliance language and build version pinned here.

**Key components:**
- `LockedToggle` — for each safety flag: `autotrade`, `dry_run`, `read_only`, `live_orders_blocked`, `max_risk`
- Tooltip on each: "This is a compile-time constant. It cannot be changed at runtime."
- Build version + compliance footer
- `READ ONLY · DRY RUN ACTIVE · LIVE ORDERS BLOCKED` badges visible

**Safety notes:**
- No execution controls
- No order buttons
- No live broker control
- All toggles are permanently locked — no user interaction changes safety posture
- This screen exists to make the posture *visible* and auditable, not configurable

**Likely repo files:**
- `frontend/src/pages/SettingsPage.tsx` (new)

---

## Screen 8 — Closed Beta Landing

**Route:** `/#/landing` (public, no app shell)

**Purpose:** Marketing surface for closed-beta invitees. Explains what MellyTrade is and what it explicitly refuses to do. Compliance footer. No auth required to view.

**Key components:**
- `ClosedBetaLanding` — hero + refuses-to-do list + compliance footer
- Hero: product name, tagline, safety posture string
- "Refuses to do" list — 6 prohibition items:
  1. No order execution
  2. No order buttons
  3. No broker write access
  4. No investment advice
  5. No profit guarantee
  6. No policy bypass
- Compliance footer: "Educational/research use only. Not personal investment advice."
- `CLOSED BETA` badge visible

**Safety notes:**
- No execution controls
- No order buttons
- No live broker control
- Hero contains literal text: `autotrade=false · dry_run=true · read_only=true · live_orders_blocked=true · max_risk≤1%`
- Landing refuses to render the hero if posture endpoint is unsafe (same SafetyBadge check as the app)
- Captured screenshots must show safety badges — no live account data

**Likely repo files:**
- `frontend/src/pages/ClosedBetaLanding.tsx`

---

## Empty & degraded states (all screens)

Extracted from `states.html`:

| State | Component | Copy |
|---|---|---|
| Watchlist empty | `WatchlistTable` | "no symbols on this watchlist yet" · adding a symbol does not place an order — read-only research view |
| Scanner no matches | `AIWorkspacePanel` | "0 of N match this filter" · widen filter or wait for next scan tick |
| Audit paused | `AuditEventsPreview` | "stream paused · 0 new events" · server continues recording |
| Portfolio (by design) | `PortfolioReportsPage` | "0 positions · never any in this build" · intentional, not a fault |
| Watchlist loading | `WatchlistTable` | Skeleton lines shimmer · if >3 s, switch to degraded read banner |
| Broker safe-disconnected | `BrokerStatusCard` | "order paths unreachable · by design" · compile-time constant |
| Supabase degraded | banner | "Reads slow. UI continues read-only with cached values." |
| Scanner model unreachable | banner | "Signal scanner is paused. Watchlist tape continues. Cached previews stamped stale." |
| Macro NO_TRADE window | all signal chips | All setups downgraded to NO_TRADE during FOMC ±30 min window — policy, not a fault |
| Human review pending | `AuditEventCard` | "N signals held for analyst pass" — visible so not confused with system fault |
| Rate limited | banner | "Scanner throttling intake. Preview latency may exceed 12 s target." |
| Network down | global | Last sync timestamp · no retries mutate state |
| Auth session expired | redirect | Sign in to resume read-only view |
