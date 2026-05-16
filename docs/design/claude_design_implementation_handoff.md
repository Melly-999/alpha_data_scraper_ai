# Claude Design Implementation Handoff

## Source

Generated from Claude Design export stored outside the repo:

```
C:\AI\MellyTrade_Workspace\03_Docs\ClaudeDesign\MellyTrade_Closed_Beta_Demo_UI_Pack
```

Raw export files are intentionally not committed.

---

## Product direction

MellyTrade is a read-only AI trading research terminal.

It is not:
- a live trading bot
- an execution platform
- an investment advice product
- a guaranteed-profit product

---

## Visual direction

Use:
- premium dark terminal UI
- institutional fintech spacing
- amber/gold default accent
- green safe state
- amber degraded/warning state
- red/crimson critical/blocked state
- JetBrains Mono or Geist Mono for market data/numbers
- Geist / Inter-style sans UI font

**Typography:**

| Role | Stack | Weights |
|---|---|---|
| UI sans | `Geist → Inter → system-ui` | 400 · 500 · 600 · 700 |
| Mono / numerals | `Geist Mono → JetBrains Mono → ui-monospace` | 400 · 500 · 600 |

Features: tabular numerals (`tnum`) everywhere data lives, `zero` for monospace disambiguation.

**Spacing (4 px base):**

| Token | Value | Use |
|---|---|---|
| `--s-2` | 8 px | Inside-row gap |
| `--s-3` | 12 px | Card body padding |
| `--s-4` | 16 px | Card padding default |
| `--s-6` | 24 px | Page gutter |
| `--s-8` | 40 px | Section gap |

**Radii:**

| Token | Value | Use |
|---|---|---|
| `--r-2` | 3 px | Badges, chips |
| `--r-4` | 7 px | Inputs |
| `--r-5` | 10 px | Cards |
| `--r-6` | 14 px | Large panels |

**Shadows:**

| Token | Use |
|---|---|
| `--sh-1` | Card resting (inset 1px + 2px drop) |
| `--sh-2` | Card emphasis (24 px drop) |
| `--accent-glow` | Hero card / active CTA (24 px gold) |

---

## Core safety badges

Every major screen should preserve or support these canonical badges:

| Badge | Severity | Shown when |
|---|---|---|
| `DEMO DATA` | accent (gold) | `VITE_DEMO_MODE === 'true'` |
| `READ ONLY` | accent (gold) | always |
| `DRY RUN ACTIVE` | success (green) | always |
| `LIVE ORDERS BLOCKED` | success (green) | always |
| `HUMAN REVIEW REQUIRED` | warning (amber) | when relevant |
| `POLICY · LOCKED` | locked (gold-muted) | locked fields |

SafetyBadge fails closed: if the posture endpoint returns a flag as unsafe (e.g. `autotrade=true`), the corresponding badge does **not** render and the CI guard fails.

---

## Signal chip vocabulary

Only five states are permitted. The type system throws at build time if any other value is passed.

| Chip | Severity | Meaning |
|---|---|---|
| `WATCH` | neutral | Monitoring — no action implied |
| `HOLD` | neutral/muted | Hold position — no action implied |
| `NO_TRADE` | degraded (red) | Policy block — no setup available |
| `LONG_SETUP` | success (green) | Research setup identified — advisory only |
| `SHORT_SETUP` | warning (amber) | Research setup identified — advisory only |

No `buy`, `sell`, `enter`, `execute`, or `guaranteed profit` wording is permitted anywhere in the product.

---

## Component inventory

All components live under `frontend/src/components/terminal/`.

### Shell

| Component | Suggested path | Notes |
|---|---|---|
| `TerminalShell` | `components/terminal/TerminalShell.tsx` | Existing — hosts SidebarNav + TerminalHeader + DemoModeBanner + content slot |
| `SidebarNav` | `components/terminal/SidebarNav.tsx` | 244 px sticky rail. Groups: WORKSPACE · POLICY · SYSTEM. Gold-bar accent on active. |
| `TerminalHeader` | `components/terminal/TerminalHeader.tsx` | Sticky topbar (52 px). Breadcrumb + StatusTicker + 2× ServiceStatusPill + UTC clock. |
| `StatusTicker` | `components/terminal/StatusTicker.tsx` | Horizontal marquee. `prefers-reduced-motion` halves speed. Tabular numerals. Read-only. |
| `ServiceStatusPill` | `components/terminal/ServiceStatusPill.tsx` | Pill with dot. Dot pulses only on `degraded`. No click handler. |

### Banners

| Component | Suggested path | Notes |
|---|---|---|
| `DemoModeBanner` | `components/terminal/banners/DemoModeBanner.tsx` | Always non-dismissible. "Demo data · educational/research use only · no live execution". Hidden only when `VITE_DEMO_MODE !== 'true'`. |
| `DegradedServicesBanner` | `components/terminal/banners/DegradedServicesBanner.tsx` | Renders only when ≥1 service is `degraded` or `safe-disconnected`. No "fix" button. |

### Badges

| Component | Suggested path | Props |
|---|---|---|
| `SafetyBadge` | `components/terminal/badges/SafetyBadge.tsx` | `kind: 'READ_ONLY' \| 'DRY_RUN' \| 'LIVE_ORDERS_BLOCKED' \| 'HUMAN_REVIEW' \| 'AUTOTRADE_OFF'` |
| `DemoDataBadge` | `components/terminal/badges/DemoDataBadge.tsx` | `variant?: 'sm' \| 'lg'` |

### Data surfaces

| Component | Suggested path | Notes |
|---|---|---|
| `WatchlistTable` | `components/terminal/WatchlistTable.tsx` | Columns: Symbol · Last · Δ% · σ-z · Vol · Trend · State (SignalChip) · Conf (ConfidenceBar). Row hover only — no row click that mutates. |
| `SignalPreviewCard` | `components/terminal/SignalPreviewCard.tsx` | Header: SYM + SignalChip. Opens detail in AIWorkspacePanel — never opens a trade dialog. |
| `AuditEventCard` | `components/terminal/AuditEventCard.tsx` | Severity left rail (2 px). Time/source column. `kind` in mono. Safety note line. |

### Policy surfaces

| Component | Suggested path | Notes |
|---|---|---|
| `BrokerStatusCard` | `components/terminal/BrokerStatusCard.tsx` | Permanent `SAFE · DISCONNECTED` pill. Capabilities matrix (`place_order`, `cancel_order`, `modify_order` always blocked). "Simulate reconnect" OK; "Connect live" forbidden. |
| `RiskMetricCard` | `components/terminal/RiskMetricCard.tsx` | Always `locked: true`. Renders as LockedField (padlock icon, `cursor:not-allowed`). Hover tooltip explains why. |

---

## Hooks (lib)

| Hook | Source | Returns |
|---|---|---|
| `useTerminalPosture()` | `lib/terminalApi.ts → /api/posture` | `{ autotrade, dry_run, read_only, live_orders_blocked, max_risk_pct, human_review }` |
| `useServicesHealth()` | `lib/terminalApi.ts → /api/services` | `{ ibkr, supabase, scanner }` each `'ok'\|'degraded'\|'safe-disconnected'` |
| `useWatchlist()` | `lib/terminalApi.ts → /api/watchlist` | SWR-style |
| `useSignalPreviews()` | `lib/scannerPreviewApi.ts → /api/signals` | SWR-style |
| `useAuditStream(paused)` | `lib/terminalApi.ts → /api/events (SSE)` | Append-only buffer, cap 200 |
| `useBrokerStatus()` | `lib/brokerApi.ts → /api/broker` | BrokerStatus |

---

## Existing repo mapping

| Status | File | Change |
|---|---|---|
| NEW | `frontend/src/styles/tokens.css` | All design tokens |
| NEW | `frontend/src/styles/severity.css` | Severity ramp + Crimson override |
| UPDATE | `frontend/src/components/terminal/terminal.css` | `@import` tokens + severity |
| UPDATE | `frontend/src/components/terminal/TerminalShell.tsx` | Wraps SidebarNav + TerminalHeader + DemoModeBanner + slot |
| UPDATE | `frontend/src/components/terminal/AuditEventsPreview.tsx` | Rows → `<AuditEventCard compact/>` |
| UPDATE | `frontend/src/components/terminal/AIWorkspacePanel.tsx` | Rows → `<SignalPreviewCard/>` + detail |
| NEW | `frontend/src/components/terminal/TerminalHeader.tsx` | — |
| NEW | `frontend/src/components/terminal/SidebarNav.tsx` | — |
| NEW | `frontend/src/components/terminal/StatusTicker.tsx` | — |
| NEW | `frontend/src/components/terminal/ServiceStatusPill.tsx` | — |
| NEW | `frontend/src/components/terminal/WatchlistTable.tsx` | — |
| NEW | `frontend/src/components/terminal/SignalPreviewCard.tsx` | — |
| NEW | `frontend/src/components/terminal/AuditEventCard.tsx` | — |
| NEW | `frontend/src/components/terminal/BrokerStatusCard.tsx` | — |
| NEW | `frontend/src/components/terminal/RiskMetricCard.tsx` | — |
| NEW | `frontend/src/components/terminal/badges/SafetyBadge.tsx` | — |
| NEW | `frontend/src/components/terminal/badges/DemoDataBadge.tsx` | — |
| NEW | `frontend/src/components/terminal/banners/DemoModeBanner.tsx` | — |
| NEW | `frontend/src/components/terminal/banners/DegradedServicesBanner.tsx` | — |
| UPDATE | `frontend/src/pages/TerminalPage.tsx` | Shell + KPI strip + WatchlistTable |
| UPDATE | `frontend/src/pages/RiskManagerPage.tsx` | Replace fields with `<RiskMetricCard locked/>` |
| UPDATE | `frontend/src/lib/terminalApi.ts` | Add posture / services / audit hooks |
| UPDATE | `frontend/src/lib/scannerPreviewApi.ts` | Typed Signal model |
| UPDATE | `frontend/src/lib/brokerApi.ts` | Guarantee no place/cancel/modify exports |

FastAPI side stays untouched by this UI pack except for adding read-only GET endpoints and the single allowed non-GET route.

---

## Backend contract (FastAPI, GET-only)

Routes that must exist (add as read-only first if not already present):

```
GET  /api/posture          → PostureFlags (autotrade=false, dry_run=true, read_only=true, live_orders_blocked=true, max_risk_pct≤1.0)
GET  /api/services         → ServicesHealth (ibkr, supabase, scanner)
GET  /api/watchlist        → list[Watchlist]
GET  /api/signals          → list[Signal]
GET  /api/events           → SSE stream of AuditEvent
GET  /api/broker           → BrokerStatus
POST /api/broker/reconnect-dry  → always returns {status:'safe-disconnected', kind:'broker_safe_disconnected'}
```

`POST /api/broker/reconnect-dry` is the **only** non-GET route in the entire product. A CI test must assert the route table.

---

## Implementation principles

- Small PRs only.
- Prefer frontend display-only changes.
- Prefer existing GET-only APIs.
- No new mutation routes (except the single approved reconnect-dry).
- No live broker connections.
- No account IDs.
- No secrets.
- No execution surface.
- Every PR must keep local read-only smoke valid.

---

## Validation commands

Required for frontend changes:

```bash
cd frontend
npm run build
cd ..
py -3.11 scripts/validate_safety_config.py
```

Required for backend changes if any:

```bash
py -3.11 -m pytest tests/app/test_safety_invariants.py tests/app/test_openapi_forbidden_paths.py -q
```

CI guards that run on every PR:

```bash
# forbidden wording guard
pnpm -C frontend test -- --run no-execution-wording

# posture guard
py -3.11 -m pytest tests/app/test_posture.py -q

# route mutation guard
py -3.11 -m pytest tests/app/test_no_mutation_routes.py -q
```

---

## Definition of done

- All 5 PRs land in order; each ships with green CI including the three guards above.
- Posture endpoint at runtime returns the canonical safety string; the homepage banner reads it live.
- `RiskManagerPage` contains zero `<form>`, zero `<input>` without `readOnly`, zero `<button type="submit">`.
- `brokerApi.ts` exports no place/cancel/modify/connect-live functions. ESLint rule blocks regression.
- Twelve README screenshots committed; `scripts/capture-screenshots.ts` reproduces them from `VITE_DEMO_SEED=2026-05-16`.
- Landing page is publicly browsable and contains the canonical safety string + refuses-to-do list.
