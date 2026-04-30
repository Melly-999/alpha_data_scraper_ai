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
