# MellyTrade / Alpha Data Scraper AI

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![React](https://img.shields.io/badge/React-dashboard-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-frontend-blue)
![Status](https://img.shields.io/badge/status-paper--trading--workstation-orange)
![Live Trading](https://img.shields.io/badge/live--trading-blocked-red)

MellyTrade is an AI-assisted trading workstation designed around safe signal analysis, broker abstraction, dry-run execution, and dashboard-based monitoring.

The project combines a FastAPI backend, React/TypeScript dashboard, broker adapter architecture, IBKR Paper Trading support, MT5-oriented integration paths, execution and risk controls, and local tooling for safe development and testing.

> Current status: local workstation and paper-trading infrastructure. Live trading is intentionally disabled by default.

---

## MellyTrade Terminal V1

A **read-only, dry-run AI trading terminal prototype** focused on market
context, signal observability, auditability, risk posture, and a daily
plan preview. The terminal is built to *explain what the system is doing
and why it is safe* — not to execute trades.

> **THIS IS A READ-ONLY TOOL. NO LIVE TRADING OCCURS. NO ORDERS ARE PLACED.**

The Terminal V1 surface is GET-only and structurally incapable of placing
an order. Its safety posture is enforced both by code shape (Pydantic
schemas without execution-shaped fields, no mutating frontend helpers in
read-only pages) and by an executable test suite that fails the build if
the posture ever drifts.

## Terminal V1 Highlights

- **Polished read-only dashboard UX states.** Shared `<ResourceState>`
  shell renders consistent loading, empty, degraded, and
  *last-updated-at* states across every polling card.
- **Read-only audit / event feed with safety notes.** Each event carries
  `id`, `timestamp`, `type`, `severity`, `read_only=true`, and a
  one-sentence `safety_note` explaining the safety implication.
- **Daily Trading Plan Preview.** Static, display-only card with
  instrument bias, setup quality, risk tier, no-trade conditions, and
  optional setup-area / notes. No buttons, no clickable rows, no
  BUY/SELL affordances. The schema deliberately omits any
  execution-shaped field (quantity, lot, sl, tp, order id).
- **Safety regression tests.** A 39-assertion pytest file codifies the
  read-only / dry-run contract as enforceable invariants — if a future
  change adds a mutating route, an order-placement function call, or
  raises the per-trade risk cap, the build breaks.
- **Local demo runbook.** A reviewer-ready walkthrough that covers
  prerequisites, startup commands, smoke-test endpoints, and the full
  list of capabilities that are *intentionally* out of scope.

## Safety-First Posture

Terminal V1 enforces the following invariants. Each one has a
corresponding test that fails the build if the posture drifts.

| Invariant | Value | Where it is enforced |
|---|---|---|
| `autotrade.enabled` | `false` | `config.json` + safety regression tests |
| `autotrade.dry_run` | `true` | `config.json` + safety regression tests |
| `read_only` | `true` | every emitted audit event, `/api/risk/config`, schema defaults |
| `max_risk_per_trade` | `≤ 1.0%` | `/api/risk/config`, asserted in tests |
| Live orders | **blocked** | `live_orders_blocked` audit event always emitted |
| Execution routes | **none in Terminal V1** | route-inventory test fails on any non-GET method under the Terminal V1 prefixes |
| Order buttons | **none** | static text-scan test fails on `placeOrder(`, `executeOrder(`, button text like "Place Order" / "Execute Trade" / "Submit Order" |
| Broker write paths | **none in Terminal V1** | `/broker/dry-run-report` is on a small admin allowlist and is dry-run only |
| Secrets required for the demo | **none** | the terminal does not authenticate against any live broker |

## Executable Safety Spec

Three pytest files act as the executable safety contract for Terminal V1:

- [`tests/app/test_safety_invariants.py`](tests/app/test_safety_invariants.py)
  — 39 assertions covering route inventory, `config.json` posture, live
  `/risk/config` values, audit-feed shape, and a static frontend scan
  for mutating helpers and order-button text.
- [`tests/app/test_trading_plan.py`](tests/app/test_trading_plan.py)
  — 10 assertions locking the Daily Trading Plan response shape, the
  read-only label, the `≤ 1%` risk cap, the absence of execution-shaped
  fields, and a 405 proof for POST/PUT/DELETE/PATCH against the route.
- [`tests/app/test_audit_events.py`](tests/app/test_audit_events.py)
  — Existing route and audit coverage that this sprint extends.

These tests are deliberately small and fast (the full
`tests/app/` suite runs in under a second). They are intended to be
treated as a regression net — if any of them fails, something
safety-relevant has changed.

## Local Demo

Full reviewer walkthrough lives in
[`docs/demo/terminal_v1_local_demo.md`](docs/demo/terminal_v1_local_demo.md).
Quick smoke commands (each verified on this branch):

```powershell
# Targeted: safety regression net
py -3.11 -m pytest tests/app/test_safety_invariants.py -q

# Targeted: trading-plan tests
py -3.11 -m pytest tests/app/test_trading_plan.py -q

# Full local backend test suite
py -3.11 -m pytest tests/app/ -q

# Frontend type-check + production build
cd frontend
npm run build
```

Expected on this branch: 39 / 10 / 145 backend tests passing and a
clean Vite production build.

> The free Claude Code / local AI-worker setup that supports this work
> is tracked on a separate branch and is intentionally **not** linked
> from this README until the branches are merged.

## Read-only API Surface

The Terminal V1 endpoints are all GET-only. None of them mutate state,
place orders, or contact a real broker.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Liveness + safety posture summary |
| `GET` | `/api/terminal/events` | Read-only audit / event feed with `safety_note` |
| `GET` | `/api/terminal/trading-plan` | Daily Trading Plan Preview (static, display-only) |
| `GET` | `/api/risk/config` | Live risk gates: `dry_run`, `auto_trade`, `max_risk_per_trade` |
| `GET` | `/api/risk/status` | Current gate state given the account snapshot |
| `GET` | `/api/dashboard/summary` | Aggregate dashboard payload |

A 405 from any other HTTP method against `/api/terminal/trading-plan`
is part of the test contract — see `test_trading_plan_route_is_get_only`.

## What Is Intentionally Not Supported Yet

Each absence below is a design decision, not an oversight. Several are
enforced by `tests/app/test_safety_invariants.py`:

- **Live trading** — no Terminal V1 code path sends orders to a real broker.
- **Order placement** — no order ticket schema, no `POST /orders`, no `POST /trade`.
- **Order buttons** — no UI affordance for Place Order / Execute Trade / Submit Order / Send Live Order.
- **Broker write actions** — `POST /broker/dry-run-report` is allowlisted and dry-run only; it is not exposed in the Terminal V1 UI.
- **MT5 / IBKR live execution** — out of scope; the live execution boundary is upstream of Terminal V1 and intentionally not reachable from it.
- **Automatic trade execution** — `autotrade.enabled` is `false` in the committed `config.json` and the safety regression test fails if it ever flips to `true`.

Adding any of the above would require an explicit, separate change with
its own review and tests; on the current branch it would also break the
safety regression suite by design.

---

## Current Status

MellyTrade is currently in a safe local workstation and paper-trading phase.

Completed:
- FastAPI backend baseline
- React/TypeScript dashboard baseline
- IBKR Paper Adapter v1
- broker health and account endpoints
- read-only dashboard Broker card
- local Windows run scripts
- smoke testing workflow
- CI quality cleanup

In progress:
- MT5 bridge hardening
- execution v1 reconciliation
- broker heartbeat and reconnect monitoring
- dashboard polishing

Intentionally blocked:
- live trading
- real-money order execution
- automatic order placement without manual approval

## Core Features

- FastAPI control plane for health, dashboard, broker, signals, positions, logs, and risk views
- React and TypeScript dashboard for monitoring system state and broker connectivity
- IBKR Paper Adapter v1 with safe disconnected-state handling
- broker health, account, and dry-run reporting endpoints
- dry-run execution posture with defensive runtime defaults
- MT5 integration path preserved for future demo and bridge work
- risk and execution safety posture documented in code and docs
- local Windows helper scripts for backend startup, frontend startup, environment checks, and smoke tests
- pytest, mypy, flake8, and black quality workflow
- safety-first docs and local runbooks

## Architecture

```text
Signal / Analysis Layer
        ↓
Execution & Risk Layer
        ↓
Broker Adapter Interface
   ├── IBKR Paper Adapter
   ├── MT5 Demo / Bridge Path
   └── Future Broker Adapters
        ↓
FastAPI Control Plane
        ↓
React / TypeScript Dashboard
```

The dashboard is read-only for broker status, system visibility, and dry-run observability. It does not expose order-entry controls or live execution actions.

## Safety-First Design

MellyTrade uses defensive defaults:

- `autotrade.enabled = false`
- `dry_run = true`
- IBKR live orders are blocked
- `supports_live_orders = false` in IBKR Paper Adapter v1
- live broker execution is not exposed in the dashboard
- broker health is visible before any future execution path
- `.env.example` contains placeholders only
- local smoke tests verify dry-run behavior

This project is not financial advice and does not guarantee trading performance.

## Broker Support

| Broker / Adapter | Status | Notes |
|---|---:|---|
| IBKR Paper | Available | Safe paper and dry-run adapter with health and account endpoints |
| MT5 | In progress | Demo and integration path preserved |
| IBKR Live | Blocked | Future work only after manual approval mode and extended paper testing |
| XTB | Manual / not integrated | Not used as an automated adapter in the current architecture |

## Local Quick Start

Adjust paths to your local checkout if your repository lives elsewhere.

- Local demo checklist: [docs/LOCAL_DEMO_CHECKLIST.md](docs/LOCAL_DEMO_CHECKLIST.md)
- Local workstation release notes: [docs/RELEASE_NOTES_LOCAL_WORKSTATION.md](docs/RELEASE_NOTES_LOCAL_WORKSTATION.md)
- Portfolio case study: [docs/PORTFOLIO_CASE_STUDY_LOCAL_WORKSTATION.md](docs/PORTFOLIO_CASE_STUDY_LOCAL_WORKSTATION.md)

### Backend — IBKR Paper Mode

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\start_backend_ibkr_paper.ps1
```

### Frontend

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\start_frontend.ps1
```

Open:

```text
http://127.0.0.1:5173/
```

### Smoke Test

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\smoke_ibkr_paper.ps1
```

### Example Runner

```powershell
& "C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\.venv\Scripts\python.exe" example_runner.py --broker ibkr-paper --symbols AAPL MSFT
```

## Dashboard

The dashboard includes a read-only Broker card showing:

- broker adapter
- paper or live mode
- connection status
- account snapshot if available
- `Live orders: BLOCKED`
- `supports_live_orders = false`

When TWS or IBKR is not connected, the dashboard shows a safe disconnected paper state.

## Dashboard Preview

Screenshots can be added under:

```text
docs/assets/
```

Example:

```markdown
![MellyTrade Dashboard](docs/assets/dashboard-broker-card.png)
```

## Repository Structure

```text
app/                  FastAPI application, routes, schemas, services
brokers/              Broker adapter implementations and models
execution/            Execution and risk management layer
frontend/             React and TypeScript dashboard
scripts/              Local Windows helper scripts
docs/                 Runbooks and architecture notes
tests/                Backend and integration tests
mellytrade_v3/        MT5 and worker integration paths
```

## Roadmap

### Near-term
- Connect to a real TWS Paper session
- Add broker heartbeat and reconnect monitoring
- Improve broker and account dashboard cards
- Review and migrate execution v1 branch safely
- Add structured audit logs for broker dry-run reports

### Later
- Manual approval mode before any non-dry-run execution
- Optional IBKR paper bracket orders behind a disabled safety flag
- Persistent execution and audit storage
- Backtest-to-execution reconciliation
- Production deployment hardening

### Explicitly not enabled
- unattended live trading
- real-money order execution
- automatic order placement without manual approval

## Opis po polsku

MellyTrade to eksperymentalny terminal tradingowy i workstation do bezpiecznego testowania sygnałów, integracji brokerskich i przepływu dry-run.

Projekt łączy backend FastAPI, dashboard React/TypeScript, architekturę broker adapterów, wsparcie IBKR Paper, ścieżkę integracji MT5, mechanizmy kontroli ryzyka oraz lokalne skrypty do uruchamiania i testów.

Aktualny etap projektu to lokalne środowisko paper-trading i research. Handel na prawdziwych pieniądzach jest celowo zablokowany.

Najważniejsze założenia bezpieczeństwa:
- `autotrade.enabled=false`
- `dry_run=true`
- IBKR live orders są zablokowane
- dashboard nie udostępnia kontrolek do składania zleceń
- adapter IBKR Paper działa w trybie bezpiecznym i może pokazać stan disconnected, jeśli TWS nie jest uruchomione

## Disclaimer

This repository is for educational, research, and paper-trading development purposes only.

It does not provide financial advice, does not guarantee trading performance, and should not be used for unattended live trading. Live trading is intentionally disabled by default and should only be considered after extended paper testing, manual approval workflows, risk review, and legal and tax considerations.

## Suggested GitHub About

**Description**

AI-assisted trading workstation built with FastAPI, React, broker adapters, dry-run execution, IBKR Paper support, MT5 integration, risk controls, and dashboard monitoring.

**Topics**

`python`, `fastapi`, `react`, `typescript`, `trading`, `algorithmic-trading`, `paper-trading`, `ibkr`, `mt5`, `risk-management`, `dashboard`, `fintech`, `broker-adapter`, `dry-run`
