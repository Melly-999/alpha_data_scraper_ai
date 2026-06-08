# MellyTrade — Read-only AI Trading Terminal & Paper Risk Workspace

> A safety-first fintech demo showing AI-assisted market review, paper-only planning, portfolio/risk status, audit visibility, mobile/PWA workflow, and screenshot-based analysis — **without broker execution**.

[![Read Only](https://img.shields.io/badge/mode-READ%20ONLY-blue?style=flat-square)](https://alpha-data-scraper-ai.vercel.app)
[![Dry Run](https://img.shields.io/badge/execution-DRY%20RUN-blue?style=flat-square)](https://alpha-data-scraper-ai.vercel.app)
[![Live Orders Blocked](https://img.shields.io/badge/live%20orders-BLOCKED-red?style=flat-square)](https://alpha-data-scraper-ai.vercel.app)
[![Paper Only](https://img.shields.io/badge/trading-PAPER%20ONLY-orange?style=flat-square)](https://alpha-data-scraper-ai.vercel.app)
[![Human Review Required](https://img.shields.io/badge/review-HUMAN%20REQUIRED-yellow?style=flat-square)](https://alpha-data-scraper-ai.vercel.app)
[![Not Financial Advice](https://img.shields.io/badge/disclaimer-NOT%20FINANCIAL%20ADVICE-lightgrey?style=flat-square)](https://alpha-data-scraper-ai.vercel.app)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-frontend-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-typed-3178C6?style=flat-square&logo=typescript)](https://typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-build-646CFF?style=flat-square&logo=vite)](https://vitejs.dev)
[![Hosted on Vercel](https://img.shields.io/badge/hosted-Vercel-black?style=flat-square&logo=vercel)](https://alpha-data-scraper-ai.vercel.app)

---

## Live Demo

| Surface | URL |
|---|---|
| **Frontend demo** | [alpha-data-scraper-ai.vercel.app](https://alpha-data-scraper-ai.vercel.app) |
| **Terminal** | [/terminal](https://alpha-data-scraper-ai.vercel.app/terminal) |
| **Mobile / PWA** | [/mobile](https://alpha-data-scraper-ai.vercel.app/mobile) |
| **Broker status** | [/brokers](https://alpha-data-scraper-ai.vercel.app/brokers) |
| **Backend health** | [alpha-data-scraper-ai.onrender.com/api/health](https://alpha-data-scraper-ai.onrender.com/api/health) |
| **Safety status** | [alpha-data-scraper-ai.onrender.com/api/safety/status](https://alpha-data-scraper-ai.onrender.com/api/safety/status) |

> **No account, no login, no API keys required.** All views are read-only and paper/simulation only.

---

## Safety Contract

MellyTrade enforces a strict read-only posture at every layer. The safety invariants are codified in `config.json`, enforced by the FastAPI backend, and verified by an executable pytest suite on every push.

```text
autotrade           = false
dry_run             = true
read_only           = true
live_orders_blocked = true
execution_enabled   = false
max_risk_per_trade  = <= 1%

No buy / sell / order / execute controls in the UI
No live broker connections
No real orders placed
No AI provider keys in the frontend
No secrets required to run the demo
```

The safety regression suite (`tests/app/test_safety_invariants.py`, `test_openapi_forbidden_paths.py`) fails the build if any of these invariants ever drift.

---

## Demo Screenshots

<!-- screenshot: terminal -->
*Terminal dashboard — red/black institutional UI with safety banner, signal workspace, audit feed, and risk posture*

<!-- screenshot: mobile-pwa -->
*Mobile / PWA view — AI companion, Paper Game Plan, Safety Score, FOMO Guard, Melly Pet risk coach*

<!-- screenshot: ai-screenshot-review -->
*AI Screenshot Review — upload a chart image, receive analysis-only paper preview (image never stored)*

<!-- screenshot: safety-badges -->
*Safety badge rail — DRY RUN · READ ONLY · HUMAN REVIEW REQUIRED · LIVE ORDERS BLOCKED on every key view*

<!-- screenshot: broker-readonly -->
*Broker status — safe disconnected read-only state, no execution controls visible*

---

## Feature Overview

### Institutional Terminal Preview
Red/black professional trading terminal UI. Shows system status, equity curve, signal workspace, audit/event feed, and daily paper plan preview — all display-only. No order entry, no execution affordances.

### AI Workspace
Signal analysis layer with a structured reasoning panel: confidence breakdown, risk gate pass/fail status, explicit *human review required* framing, and four safety badges on every variant. Powered by a deterministic mock by default — no live AI provider key needed.

### Paper Sandbox
Paper-only plan preview. The backend exposes `GET /paper/run/preview` — no `POST/PUT/PATCH/DELETE` trading mutation routes. The Pydantic schema deliberately omits execution-shaped fields (quantity, lot, sl, tp, order id).

### AI Screenshot Review
On the `/mobile` route: upload a chart screenshot for analysis-only paper commentary. The image is never stored, no broker integration, no order placement. Runs a deterministic mock by default.

### Mobile / PWA Demo
Full mobile-first companion app installable as a PWA on iOS / Android / iPad:
- AI Chart Review
- Paper Game Plan
- Safety Score
- Watchlist
- Setup Journal
- FOMO Guard
- Weekly Report
- Monte Carlo snapshot
- Melly Pet risk coach (inline SVG mascot — pure UI, no API calls)

### Broker Status — Read-only
Broker cards show adapter name, paper/live mode indicator, connection health, and `Live orders: BLOCKED`. No write paths. No broker credentials required.

### Audit / Evidence Trail
Every API response carries `read_only=true` and a `safety_note`. The audit feed logs `live_orders_blocked`, `scanner_evaluated`, `risk_blocked`, and `stale_data_warning` events. Every smoke test run is documented as a markdown evidence report in `docs/evidence/`.

### Safety-First Architecture
- All endpoints are `GET`-only on Terminal / Signal / Paper surfaces
- `autotrade=false` and `dry_run=true` enforced in `config.json` and asserted in pytest
- Forbidden-path test (`test_openapi_forbidden_paths.py`) fails if a mutating route appears under guarded prefixes
- Safety validator script (`scripts/validate_safety_config.py`) runs in CI and locally
- Playwright e2e suite: 54 tests across iPad and mobile viewports (GitHub Actions, no backend required)

---

## Architecture

```text
┌──────────────────────────────────────────────────────┐
│  Frontend  (React + TypeScript + Vite)               │
│  Hosted: Vercel                                      │
│                                                      │
│  /terminal   — institutional dashboard               │
│  /mobile     — PWA AI companion                     │
│  /brokers    — read-only broker status               │
│                                                      │
│  Poll-only: apiGet() — no mutation helpers           │
│  No provider keys exposed in browser                │
└───────────────────┬──────────────────────────────────┘
                    │  HTTPS  GET-only
┌───────────────────▼──────────────────────────────────┐
│  Backend  (FastAPI + Python 3.11+)                   │
│  Hosted: Render                                      │
│                                                      │
│  GET /api/health          liveness + safety posture  │
│  GET /api/safety/status   live invariant values      │
│  GET /api/terminal/*      dashboard payloads         │
│  GET /api/signals/*       signal decisions           │
│  GET /api/risk/config     dry_run / autotrade gates  │
│  GET /paper/run/preview   paper plan preview         │
│                                                      │
│  No POST/PUT/PATCH/DELETE on trading surfaces        │
│  No broker write paths registered                    │
│  No live order execution reachable                   │
└──────────────────────────────────────────────────────┘
```

**Stack:** Python · FastAPI · Pydantic · React · TypeScript · Vite · Vercel · Render · pytest · PWA

---

## Validation & Evidence

### Hosted Smoke — PASS (demo-008)

Full 21-check hosted smoke test run against production URLs — CORS verified, safety posture confirmed, no unsafe controls found.

- Evidence report: [`docs/evidence/demo-008-hosted-smoke-pass.md`](docs/evidence/demo-008-hosted-smoke-pass.md)
- Merged via PR #268

### SPA Deep-link Fix (PR #269)

Direct routes (`/terminal`, `/mobile`, `/brokers`) return HTTP 200 without full reload via Vercel SPA catch-all rewrite. Post-merge production smoke confirmed PASS.

- Config: [`frontend/vercel.json`](frontend/vercel.json)
- Merged via PR #269

### Safety Validator

```powershell
py -3.11 scripts/validate_safety_config.py
# OVERALL PASS — all safety invariants confirmed
```

### Test Suite

```powershell
py -3.11 -m pytest tests/app/test_openapi_forbidden_paths.py tests/app/test_safety_invariants.py -q
# 60 tests passed
```

### Static Safety Scan

No `placeOrder(`, no `executeOrder(`, no "Place Order" / "Execute Trade" / "Submit Order" button text, no broker write paths, no secrets in source.

---

## What This Project Demonstrates

| Engineering skill | Where it shows |
|---|---|
| **AI product engineering** | Signal reasoning panel, screenshot review flow, safety-aware UX patterns |
| **Safe fintech UX** | Read-only posture enforced simultaneously at UI, API, and test layers |
| **FastAPI + React architecture** | Typed Pydantic schemas, poll-only frontend, CORS-safe cross-origin hosting |
| **Deployment & debugging** | CORS root-cause analysis, Vercel build-time env var bake, SPA rewrite fix |
| **Safety-first automation** | config.json + pytest safety contract, forbidden-path testing, validator script |
| **Portfolio-quality evidence** | Smoke reports, PRs with detailed bodies, documented merge history |
| **PWA / mobile engineering** | iOS/iPad-installable PWA, responsive mobile companion, multi-viewport CI |
| **CI/CD** | GitHub Actions: pytest, Playwright e2e (54 tests, iPad + mobile viewports) |

---

## Roadmap

Honest, safe roadmap — no live trading planned.

**Planned:**
- [ ] Demo asset capture pack (annotated screenshots for portfolio)
- [ ] Portfolio case study document
- [ ] EXE / desktop wrapper exploration
- [ ] PWA / mobile wrapper hardening
- [ ] Better signal reasoning UI (expand AI reasoning panel)
- [ ] Auth / persistent storage (only after explicit safety review)

**Explicitly not planned:**
- Live trading
- Real-money order execution
- Unattended automated order placement
- Broker live credentials in the repository

---

## Local Quick Start

```powershell
# Backend (from repo root)
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

# Frontend
cd frontend
npm install
npm run dev
# Open: http://127.0.0.1:5173/terminal
```

```powershell
# Safety validator
py -3.11 scripts/validate_safety_config.py

# Safety regression tests
py -3.11 -m pytest tests/app/test_safety_invariants.py tests/app/test_openapi_forbidden_paths.py -q
```

---

## Repository Structure

```text
app/              FastAPI application — routes, schemas, services
frontend/         React + TypeScript + Vite dashboard
  vercel.json     SPA catch-all rewrite (deep-link fix, PR #269)
scripts/          Safety validator, local helper scripts
tests/app/        Safety regression suite (pytest)
docs/evidence/    Smoke test evidence reports
docs/demo/        Demo docs and screenshot checklists
docs/showcase/    Portfolio showcase docs
config.json       Runtime safety config (autotrade=false, dry_run=true)
```

---

## Beta Documentation

For source-only beta operations, start here:

- [Beta Docs Index](docs/beta/README.md)
- [Beta Rollout Operator Command Center](docs/beta/beta_rollout_operator_command_center.md)
- [Beta Rollout Operator Master Checklist](docs/qa/beta_rollout_operator_master_checklist.md)

> Source-only beta is read-only, dry-run-only, and manual. It does not approve live trading, broker execution, investment advice, or generated artifact releases.

---

## Disclaimer

This repository is for **educational, research, and paper-trading portfolio demonstration purposes only**.

- **Not financial advice.** Nothing here constitutes investment advice, financial guidance, or a recommendation to trade any instrument.
- **No live trading.** No real orders are or can be placed through this demo.
- **Paper / simulation / read-only only.** All outputs are for analysis and planning preview only.
- **Human review required.** No automated execution of any kind is enabled or planned.
- **No profit guarantee.** Past signal analysis does not imply future trading performance.
- **No broker execution.** This demo does not connect to any live broker account.

---

## GitHub About Metadata

> *Proposed repository metadata — apply via GitHub repository Settings > About.*

**Repository description:**
```
Safety-first read-only AI trading terminal and paper risk workspace with FastAPI, React, mobile PWA, AI screenshot review, audit evidence, and no live order execution.
```

**Website:**
```
https://alpha-data-scraper-ai.vercel.app
```

**Topics:**
```
ai  fintech  trading-dashboard  risk-management  fastapi  react  vite  pwa
paper-trading  read-only  safety-first  portfolio-project  ai-dashboard
automation  python
```

---

*MellyTrade — read-only · paper-only · human review required · not financial advice*
