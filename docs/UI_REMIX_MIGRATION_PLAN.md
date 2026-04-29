# Remix UI Migration Plan

## What the Remix prototype contains

`MellyTrade (Remix).zip` contains a standalone dashboard prototype with:

- `src/layout.jsx`: top bar, sidebar, status pills, and app shell composition
- `src/dashboard.jsx`: account metrics, equity chart, watchlist, signals, activity, system health, risk, and execution mode sections
- `src/shared.jsx`: card, badge, table, drawer, mini chart, and utility component ideas
- `src/signals.jsx`: signal table and signal detail drawer ideas
- `src/risk.jsx`: risk manager layout ideas
- `src/mt5.jsx`: MT5 status and connection-log layout ideas
- `src/backtest.jsx`: backtest lab layout ideas
- `src/architecture.jsx` and `src/pages.jsx`: static navigation and reference views
- `src/data.js`: mock prototype state via `window.MT_DATA`

## Why it was not connected automatically

The prototype is not a production frontend. It reads from `window.MT_DATA`, includes hard-coded account/signal/risk/MT5 values, and contains controls that are not safe to port directly. The working app already has real FastAPI hooks and typed API contracts, so the prototype should be used only as a visual reference.

The Remix dashboard migration must not replace live app state with prototype mock data.

## Current working frontend structure

- `frontend/src/App.tsx`: router and app shell wiring
- `frontend/src/layout/AppShell.tsx`: layout wrapper
- `frontend/src/layout/Sidebar.tsx`: navigation
- `frontend/src/layout/TopBar.tsx`: health and safety status
- `frontend/src/pages/DashboardPage.tsx`: dashboard and Broker Card
- `frontend/src/hooks/useDashboard.ts`: dashboard summary polling
- `frontend/src/hooks/useHealth.ts`: API health polling
- `frontend/src/hooks/useRisk.ts`: risk config/status/violations polling
- `frontend/src/hooks/useBroker.ts`: IBKR paper broker health/account polling
- `frontend/src/lib/api.ts`: shared API client
- `frontend/src/types/api.ts`: typed backend contracts
- `frontend/src/components/shared/*`: shared card, badge, table, chart, and drawer components

## Current real backend connections

The current frontend uses real backend endpoints:

- health: `/health` through `/api/health` base wiring
- dashboard summary: `/api/dashboard/summary`
- risk: `/api/risk/config`, `/api/risk/status`, `/api/risk/violations`
- broker health: `/api/broker/health`
- broker account: `/api/broker/account`
- signals: existing signal endpoints
- positions: existing position endpoints
- MT5 status: existing MT5 status endpoint
- logs: existing logs endpoint

Broker dry-run report submission exists at `POST /api/broker/dry-run-report`, but passive dashboard UI must not call it as read state.

## Target UI direction

Adopt the useful Remix visual direction:

- denser terminal-style dashboard shell
- stronger status strip
- compact account metric cards
- clearer grid hierarchy
- tighter card spacing and mono labels
- grouped system health, risk, execution, and broker safety sections

Do not adopt:

- `window.MT_DATA`
- mock data as source of truth
- execute buttons
- order controls
- reconnect controls
- emergency-stop controls unless they are part of an existing safe page flow

## Prototype classification

Visual reference:

- `src/layout.jsx`
- `src/dashboard.jsx`
- passive visual ideas from `src/mt5.jsx`
- passive visual ideas from `src/backtest.jsx`

Component idea:

- status pills
- compact cards
- dense tables/lists
- grouped health and risk rows

Mock-data only:

- `src/data.js`
- any page logic that reads `window.MT_DATA`

Unsafe/action UI not suitable:

- signal execution button in `src/signals.jsx`
- config toggles and emergency-pause controls in `src/risk.jsx`
- reconnect action in `src/mt5.jsx`
- backtest run controls unless a real safe backend workflow exists

## Migration stages

Stage 1: dashboard shell v2 - done

- update `frontend/src/pages/DashboardPage.tsx`
- update `frontend/src/index.css`
- preserve `useBroker.ts`
- preserve the Broker Card and visible live-order block
- keep all data from real hooks

Stage 2: shared visual primitives - done

- refine `frontend/src/components/shared/Card.tsx`
- refine `frontend/src/components/shared/Badge.tsx`
- refine `frontend/src/components/shared/Table.tsx`
- refine drawer, button, and gauge styling through shared CSS only
- keep existing component props and backend data flow unchanged

Stage 3: passive page alignment

- align `SignalsPage`, `MT5BridgePage`, and `RiskManagerPage` visually
- only use existing real endpoints
- do not add execution controls
- do not add signal execution buttons
- do not add MT5 reconnect controls
- do not add new risk setting capabilities
- preserve any existing backend-gated safety controls without expanding their scope
- use safe passive layouts for any analytics/backtest page unless a real read-only endpoint exists

Stage 4: broker dry-run report visibility

- add read-only dry-run report display only if a safe read endpoint exists
- do not call `POST /api/broker/dry-run-report` from passive dashboard UI
- if report history is needed, first add a dedicated read-only endpoint such as:
  - `GET /api/broker/dry-run-reports`
  - or `GET /api/execution/reports`
- do not add mutation endpoints or order controls

## API mapping

- health: `/health` and `/api/health`
- broker health: `/api/broker/health`
- broker account: `/api/broker/account`
- dry-run report submission: `POST /api/broker/dry-run-report`
- dry-run report history: not currently exposed as a read-only dashboard endpoint
- dashboard: `/api/dashboard/summary`
- risk: `/api/risk/config`, `/api/risk/status`, `/api/risk/violations`
- MT5: existing MT5 status endpoint only
- signals: existing signal endpoints only
- backtest: existing endpoints only if present, otherwise safe placeholders

## Safety requirements

- keep `autotrade.enabled=false`
- keep `dry_run=true`
- preserve `supports_live_orders=false`
- preserve visible `Live orders: BLOCKED`
- do not enable live trading
- do not add order buttons
- do not expose execution controls
- do not switch the dashboard to `window.MT_DATA`
- do not use prototype mock data as real state
- do not touch MT5 execution behavior
- do not change risk settings
- do not commit secrets

## Risks

- the prototype includes unsafe action controls that must remain out of this app
- mock state names differ from the real backend contract
- broad CSS changes can affect other pages
- broker-card preservation must be verified on every dashboard pass

## Exact files for next pass

Likely files:

- `frontend/src/components/shared/Card.tsx`
- `frontend/src/components/shared/Badge.tsx`
- `frontend/src/components/shared/Table.tsx`
- `frontend/src/pages/SignalsPage.tsx`
- `frontend/src/pages/MT5BridgePage.tsx`
- `frontend/src/pages/RiskManagerPage.tsx`

Any next pass should keep route/API changes separate from visual refactoring.

This pass should not introduce new actions. Shared component polish is limited to density, typography, table states, badge/status presentation, and consistent panel headers.

Stage 3 must also remain passive. No action controls from the Remix prototype were migrated: signal execution buttons, MT5 reconnect controls, mock risk toggles, emergency/live controls, and backtest run controls remain out of scope.

## Branch alignment requirement

Before any Remix UI migration PR, the working branch must be based on the latest `origin/main` and must contain the IBKR paper run tooling/dashboard broker-card work from PR #25.

Required files:

- `frontend/src/hooks/useBroker.ts`
- `scripts/start_backend_ibkr_paper.ps1`
- `docs/LOCAL_RUNBOOK_IBKR_PAPER.md`

If any are missing, stop and sync or merge PR #25 first.

The Remix dashboard migration must preserve the read-only Broker Card, real broker API hooks, dry-run safety state, and visible `Live orders: BLOCKED` indicator.
