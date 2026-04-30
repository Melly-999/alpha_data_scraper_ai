# MellyTrade Local Workstation — Portfolio Case Study

**Type:** Portfolio documentation  
**Milestone:** Local Workstation — Phase 1 Checkpoint  
**Audience:** Recruiters, technical reviewers, fintech / backend / AI-assisted developer context  
**Status:** Local demo / paper-trading / read-only workstation — not a live trading system

---

## 1. Project Summary

MellyTrade is an AI-assisted trading workstation prototype built around a FastAPI backend and a React/Vite TypeScript frontend. The current milestone focuses on broker visibility, dry-run safety, and local workstation diagnostics rather than automated execution.

The system is currently local, demo-oriented, and read-only. It is not a live trading system, does not place real orders, and does not claim production deployment.

Key capabilities shipped at this milestone:

- **IBKR Paper Adapter v1** — typed broker adapter for Interactive Brokers Paper Trading with safe disconnected-state handling
- **Broker Card** — read-only dashboard component displaying broker mode, connection status, and live-order blocked status
- **Local Demo Checklist** — dashboard card and API endpoint aggregating local safety state
- **Frontend build fixed** — TypeScript configuration repaired, 0 errors after build
- **Local smoke/test workflow** — repeatable PowerShell scripts for backend start, frontend start, and smoke validation

---

## 2. Problem

This project addresses a set of concrete local development challenges common in fintech and trading system work:

- **Execution before observability is unsafe.** Trading tools built with order controls before safety visibility and risk gates are in place carry significant operational risk. The project prioritises read-only observability first.
- **Local environment state is often unclear.** Without a documented local run flow, it is difficult to confirm that the system is in a safe, testable state before each development session.
- **Broker dependency should not block local development.** When a paper broker (TWS Paper) is unavailable, the dashboard and backend must still be usable and must not crash or produce confusing error states.
- **Developers need repeatable validation.** Build, test, and smoke steps must be documented and scripted so the same flow can be followed consistently across sessions.
- **Degraded states must be visible and expected.** A disconnected broker is a normal local development state, not an application error. The UI must communicate this clearly without implying a failure.

---

## 3. Solution

The milestone delivers a read-only local workstation foundation:

- **FastAPI backend** with health, broker state, and local checklist routes
- **React/Vite dashboard** with a Broker Card and Local Demo Checklist card, both read-only
- **Safe disconnected state** when TWS Paper is unavailable — the adapter returns a typed disconnected status; no crash, no order controls exposed
- **Dry-run and live-order blocked visibility** — `dry_run=true` and `Live orders: BLOCKED` are surfaced prominently in the dashboard
- **Documented Windows local run flow** — PowerShell scripts for backend start, frontend start, environment check, and smoke test
- **Typed frontend API client** in `frontend/src/lib/api.ts` and Vite environment types
- **TypeScript build repair** — root cause fixed in `tsconfig.json`, not suppressed

---

## 4. Architecture Overview

```text
React / Vite Dashboard
    ↓ typed API client (frontend/src/lib/api.ts)
    ↓
FastAPI Backend (127.0.0.1:8001)
    ↓
Broker Adapter Layer (safe paper-broker factory)
    ↓
IBKR Paper Adapter v1
    → health() → BrokerHealth
    → account_snapshot() → BrokerAccountSnapshot
    → submit_dry_run_report() → BrokerExecutionReport
    → (safe disconnected snapshot when TWS is unavailable)
```

**API surface exposed:**

| Route | Purpose |
|---|---|
| `GET /health` | Application liveness |
| `GET /api/health` | Backend health + dry-run/auto-trade flags |
| `GET /api/broker/health` | Broker adapter health, mode, port, live-order status |
| `GET /api/broker/account` | Read-only account snapshot (zeroed when disconnected) |
| `GET /api/local/checklist` | Aggregated local safety checklist |

No dashboard mutation calls for trading are exposed. Broker actions remain read-only. The smoke script (`smoke_ibkr_paper.ps1`) validates safe local behavior against these endpoints.

---

## 5. Safety-First Design

The system enforces a strict safety posture at every layer:

**Runtime defaults:**
- `autotrade.enabled = false`
- `dry_run = true`

**Broker adapter:**
- `supports_live_orders = false` (IBKR Paper Adapter v1)
- Live orders blocked — `supports_live_orders()` always returns `False`
- Live TWS ports (`7496`, `4001`) are refused; start script aborts if a live port is configured
- Read-Only API recommended when TWS Paper is configured

**Dashboard:**
- No order buttons
- No reconnect or execution controls
- `Live orders: BLOCKED` chip always visible
- Disconnected broker state treated as expected and degraded, not a crash

**Execution scope:**
- TWS Paper is optional — the system operates safely without it
- MT5 execution path is untouched
- Risk settings are untouched

**CI:**
- `ib_insync` is intentionally excluded from `requirements-ci.txt`; the adapter must return a typed `missing_dependency` health status on CI without crashing

---

## 6. Key Features Shipped

### Backend / API

- FastAPI health routes (`/health`, `/api/health`)
- Broker health and account routes (`/api/broker/health`, `/api/broker/account`)
- `GET /api/local/checklist` — aggregates backend safety state and broker health snapshot; read-only, no mutation
- Typed Pydantic schemas for broker health, account snapshot, execution report, and checklist response
- Safe disconnected account snapshot — zeroed balances with typed `last_error` when TWS is not connected

### Broker Integration

- **IBKR Paper Adapter v1** — imports cleanly when `ib_insync` is not installed
- Paper port `7497` by default; live port `7496` blocked
- `supports_live_orders = false`
- Handles `ib_insync` missing, TWS not running, wrong port, stale connection, and accidental live-port configuration — none of these crash the FastAPI app
- Optional TWS Paper connected-state path documented

### Frontend / Dashboard

- Remix-inspired dashboard shell
- **Broker Card** — displays adapter, mode, port, connection status, account snapshot, and live-order status
- **Local Demo Checklist card** — reads from `GET /api/local/checklist`; shows pass/warn per safety check
- Passive page visual alignment (Signals, Positions, Risk, Logs, MT5 Bridge, Trade Blotter, Settings)
- Read-only status presentation throughout — no execution controls

### Tooling / Docs

- `scripts/start_backend_ibkr_paper.ps1` — starts FastAPI with IBKR Paper adapter; refuses live port
- `scripts/start_frontend.ps1` — installs npm deps if needed, starts Vite dev server
- `scripts/smoke_ibkr_paper.ps1` — smoke validates all key routes
- `scripts/check_local_env.ps1` — prints branch, Python, venv, IBKR files, `.env` presence (never prints secret content)
- `docs/LOCAL_DEMO_CHECKLIST.md` — repeatable local demo steps
- `docs/RELEASE_NOTES_LOCAL_WORKSTATION.md` — milestone release notes
- TypeScript build root cause fix (`tsconfig.json`)

---

## 7. Validation

The following results were verified at the local workstation checkpoint:

| Check | Result |
|---|---|
| Frontend build | Passed |
| TypeScript errors | 0 |
| Backend tests | 38 passed |
| Smoke test | Passed |
| Dashboard HTTP | 200 |
| `/api/local/checklist` reachable | Yes |

**Checklist safety check results:**

| Check | Result | Notes |
|---|---|---|
| Backend API | pass | FastAPI responding |
| Dry-run mode | pass | `dry_run=true` confirmed |
| Auto-trade | pass | `auto_trade=false` confirmed |
| Broker live orders | pass | `supports_live_orders=false` confirmed |
| Broker mode/status | warn | TWS Paper disconnected — expected without active TWS session |

The broker mode/status warning is the expected and safe state when TWS Paper is not running. The adapter remains read-only, live orders remain blocked, and no order controls are exposed.

---

## 8. Technical Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic, uvicorn |
| Testing | pytest, mypy, flake8, black |
| Frontend | React, TypeScript, Vite |
| Broker integration | IBKR Paper (ib_insync optional dependency) |
| Local tooling | PowerShell scripts |
| CI/CD | GitHub Actions, PR-based workflow |
| Future integration path | MT5 (preserved, not modified) |

The project does not claim production readiness. It is a local workstation and paper-trading prototype at the current milestone.

---

## 9. Engineering Decisions

**Read-only observability before execution.** The deliberate choice to build broker visibility, health endpoints, and the dashboard before any execution path ensures that safety state is verifiable before any future execution work begins.

**Disconnected broker as a safe degraded state.** Rather than treating TWS Paper unavailability as an error condition, the adapter returns a typed disconnected status. This allows local development to proceed without broker configuration while keeping the safety invariants intact.

**TWS Paper kept optional.** Requiring a live TWS session for local development would block most development workflows. The optional dependency model means the adapter degrades gracefully and CI does not require `ib_insync`.

**GET-only checklist endpoint.** `GET /api/local/checklist` aggregates existing backend state and broker health. It does not mutate configuration, connect to live trading, place orders, or call execution endpoints.

**Dashboard free of mutation and order controls.** Order controls and execution surfaces require independent review and manual approval design. Keeping the dashboard read-only at this milestone eliminates an entire class of accidental execution risk.

**TypeScript build root cause fix.** The TypeScript configuration error was resolved at the source in `tsconfig.json` rather than suppressed with `// @ts-ignore` or similar workarounds. This produces a clean, zero-error build and avoids hidden type errors accumulating.

**Repeatable local demo flow.** Scripted and documented local run steps (`start_backend_ibkr_paper.ps1`, `start_frontend.ps1`, `smoke_ibkr_paper.ps1`) make the demo flow reproducible across development sessions without relying on implicit environment assumptions.

---

## 10. Screenshots / Demo Placeholders

The following screenshots can be added under `docs/assets/` when available:

```
[Screenshot placeholder: Dashboard overview with Broker Card and Local Demo Checklist]
```

```
[Screenshot placeholder: Broker Card — disconnected paper state with "Live orders: BLOCKED" chip]
```

```
[Screenshot placeholder: Local Demo Checklist card — Backend API pass, Dry-run pass, Broker mode warn]
```

```
[Screenshot placeholder: Smoke test terminal output — all routes OK, supports_live_orders=false confirmed]
```

---

## 11. Limitations

- This is a local workstation milestone, not a production trading system.
- TWS Paper connection is optional and may remain disconnected in most local development sessions.
- No live trading. No real orders. No real money involved.
- No production deployment claim.
- `ib_insync` is an optional dependency; the adapter reports `missing_dependency` cleanly when it is not installed.
- Paper connection validation can be extended in future milestones.
- Any execution workflow beyond dry-run reporting requires future manual approval design and audit logging before implementation.

---

## 12. Next Steps

Suggested safe future work, in order of priority:

- **Read-only audit and event feed** — structured log visibility in the dashboard for dry-run decisions and broker state changes
- **Signal lifecycle explanation view** — a read-only view showing how signals are generated, scored, and gated before reaching execution
- **Read-only analytics and backtest summary** — historical signal performance visibility without execution controls
- **Optional TWS Paper connected-state validation** — extend the local demo checklist to include a connected-state path once TWS Paper is stable
- **Manual approval mode design** — before any non-dry-run execution is considered, design and audit-log a per-decision human approval step
- **Broker heartbeat and reconnect monitoring** — passive visibility into broker connection stability
- **Dashboard portfolio and positions UX polish** — improve account and position display when connected-state data is available

No execution, order-entry, or live-trading work should proceed without explicit milestone approval, manual approval mode implementation, and extended paper-testing review.

---

## 13. Portfolio Summary

MellyTrade demonstrates backend and API design with FastAPI and Pydantic, React and TypeScript UI work, safety-first broker adapter architecture, test-driven local validation, and developer tooling for a fintech-style workstation. The project prioritises clear safety posture, graceful degradation, and observable system state over execution feature velocity.

The current milestone is a read-only local workstation and paper-trading prototype. It is suitable for review as an example of systematic local infrastructure work, typed API design, and safety-conscious broker integration in a financial tools context.

---

*This document is portfolio and development documentation only. It does not constitute financial advice and does not claim trading performance or production deployment.*
