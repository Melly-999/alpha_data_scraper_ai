# MellyTrade Terminal V1 — Local Demo Runbook

A reviewer-friendly walkthrough for running the **read-only / dry-run**
MellyTrade Terminal V1 locally and understanding what it does — and,
just as importantly, what it deliberately does not do.

---

## Purpose

MellyTrade Terminal V1 is a **safety-first prototype** of a trading
operations terminal. It is built around the idea that the most valuable
thing a junior trading dashboard can do is **explain itself clearly**
without ever placing a real order.

The terminal focuses on:

- **Market context** — instruments, watchlist, broker reachability.
- **AI signal observability** — signal decision history, lifecycle, and
  per-signal reasoning (read-only logs, never order intent).
- **Audit events** — a structured feed of what the backend did, why it
  is in dry-run mode, and which safety gates fired.
- **Risk posture** — current `dry_run`, `auto_trade`, `read_only`,
  per-trade risk cap, and gate status surfaced as live data, not
  hardcoded copy.
- **Daily Trading Plan Preview** — a static, display-only planning card
  with instrument bias, setup quality, risk tier, and explicit
  no-trade conditions.
- **Safety-first UI** — persistent badges, a degraded-backend banner,
  and consistent loading / empty / error states across every panel.

> **This demo does not place trades and does not execute orders.** Every
> mutating capability has been intentionally left out of Terminal V1.

---

## Safety Posture

The terminal enforces a single, repository-wide safety contract. The
current values shown in the banner are also asserted by automated tests
in `tests/app/test_safety_invariants.py`.

| Invariant | Value | Where it lives |
|---|---|---|
| `autotrade.enabled` | `false` | `config.json` |
| `autotrade.dry_run` | `true` | `config.json` |
| `read_only` | `true` | `/api/health`, `/api/risk/config`, every emitted audit event |
| `max_risk_per_trade` | `≤ 1.0%` | `/api/risk/config`, asserted in tests |
| Live orders | **blocked** | `live_orders_blocked` audit event always emitted |
| Execution routes in Terminal V1 | **none** | route inventory test fails if any non-GET route appears under `/api/terminal`, `/api/dashboard`, `/api/audit`, `/api/positions`, `/api/orders`, `/api/logs`, `/api/signals`, `/api/account`, `/api/health`, `/api/mt5`, `/api/local` |
| Order buttons in the UI | **none** | static text-scan test fails on `placeOrder(`, `executeOrder(`, button text like "Place Order", "Execute Trade", "Submit Order", "Send Live Order" |
| Broker write paths | **none in Terminal V1** | `/broker/dry-run-report` is on a small admin allowlist and is dry-run-only |
| Real orders placed | **none — never** | the codebase has no live-order code path that the Terminal V1 surface can reach |

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| **Python** | 3.11+ | The repo is tested under Python 3.11. |
| **Node.js + npm** | LTS (≥ 18) | For the Vite dev server and the production build. |
| **Git** | recent | To clone and switch branches. |
| **Repository** | cloned locally | Path examples below assume `C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai` on Windows. |
| **Backend dependencies** | `pip install -r requirements-ci.txt` is sufficient for the read-only demo | The CI requirements file omits MetaTrader5 and TensorFlow on purpose; the terminal does not need them. |
| **Frontend dependencies** | `npm install` (or `npm ci` if `package-lock.json` is present) | Installed once into `frontend/node_modules/` (git-ignored). |

> **No real broker credentials are required for this demo.** The terminal
> never authenticates against MT5, IBKR, or any live broker. If you have
> credentials, leave them out of your shell — they are not used here.

---

## Backend Startup

The backend is a FastAPI application served by Uvicorn. The repo binds it
to `127.0.0.1:8001` by convention. Run from the repository root:

```powershell
# From: C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai
py -3.11 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Or use the existing helper script (same effect):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

Expected output: `Application startup complete.` on
`http://127.0.0.1:8001`. Leave this terminal running.

---

## Frontend Startup

The frontend is a Vite + React + TypeScript app. By default the dev
server serves on `http://127.0.0.1:5173` and proxies API calls to the
backend via `VITE_API_BASE_URL`.

In a **second** terminal, from the repository root:

```powershell
cd frontend
npm install        # first run only; on subsequent runs, prefer `npm ci`
npm run dev
```

Or use the existing helper script (same effect, also sets
`VITE_API_BASE_URL=http://127.0.0.1:8001/api`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_frontend.ps1
```

Open the browser to `http://127.0.0.1:5173`. The dashboard should load
within a couple of seconds and the safety banner should turn green.

---

## Demo Walkthrough

A 5-minute reviewer walkthrough — explain each item out loud while
pointing at the screen.

### 1. Safety banner / safety badges

- Located at the very top of every page.
- Four pills: `DRY RUN`, `READ-ONLY MODE`, `LIVE ORDERS BLOCKED`,
  `MAX RISK ≤ N.N%`.
- Pills are driven by `/api/health` and `/api/risk/config` — they are
  not hardcoded copy. Stop the backend and they fall back to a muted
  "telemetry unavailable" state.

### 2. Dashboard loading, empty, degraded, and last-updated states

- Open `Positions`, `Trade Blotter`, and `Logs` from the sidebar.
- Each card uses the shared `<ResourceState>` shell:
  - `Loading …` while the first poll is in flight.
  - `No <thing> recorded yet.` empty state.
  - A red **Backend unavailable** card if the backend goes away.
  - `Last updated at HH:MM:SS` footer once data has arrived.
- Try stopping the backend (`Ctrl+C` in the Uvicorn terminal) and watch
  the cards switch to the degraded state without losing the safety banner.

### 3. Read-only audit feed with `safety_note`

- Open `Audit Trail` and the **Dashboard → Audit Events** card.
- Each event carries `id`, `timestamp`, `type`, `severity`, `source`,
  `read_only: true`, and a one-sentence `safety_note` explaining the
  *why* — e.g. `live_orders_blocked` → "All execution paths gated. No
  order will be sent to a broker."
- The feed is asserted by tests: every event must be `read_only: true`,
  and every safety-severity event must carry a non-empty `safety_note`.

### 4. Daily Trading Plan Preview

- Located on `Dashboard`, just under the Audit Events card.
- Tagged `READ-ONLY PLAN PREVIEW` and `NO ORDERS PLACED`.
- Each row shows: instrument, bias (`bullish` / `bearish` / `neutral` /
  `wait`), setup quality, risk tier, no-trade condition, optional
  setup area, optional notes.
- There are no buttons, no clickable rows, no BUY/SELL affordances.
- The schema deliberately omits any execution-shaped field
  (`quantity`, `lot_size`, `sl`, `tp`, `order_id`) — a regression test
  fails immediately if one is ever added.

### 5. Risk / read-only indicators

- `Risk Manager` (sidebar) shows the live `RiskConfig` from the
  backend: `dry_run`, `auto_trade`, `max_risk_per_trade`, daily loss
  cap, and gate status. Numbers are reported, not editable from the
  read-only Terminal V1 surface.

### 6. Backend unavailable / degraded behaviour

- Stop the Uvicorn process. Watch the dashboard:
  - Safety banner shows `Safety telemetry unavailable`.
  - Each `<ResourceState>`-wrapped panel switches to the red
    **Backend unavailable** card and reports the time of its last
    successful fetch.
- Restart Uvicorn. The panels recover automatically — there is no
  manual refresh required.

---

## Smoke Test Endpoints

The terminal surface is GET-only. Verify each endpoint from any second
terminal while the backend is running.

```powershell
# Health, with safety posture
Invoke-RestMethod http://127.0.0.1:8001/api/health

# Read-only audit / event feed (Task 2)
Invoke-RestMethod http://127.0.0.1:8001/api/terminal/events

# Daily Trading Plan Preview (Task 4)
Invoke-RestMethod http://127.0.0.1:8001/api/terminal/trading-plan

# Live risk configuration — note dry_run=true, max_risk_per_trade <= 1
Invoke-RestMethod http://127.0.0.1:8001/api/risk/config

# Aggregate dashboard summary
Invoke-RestMethod http://127.0.0.1:8001/api/dashboard/summary
```

To prove the trading-plan endpoint is GET-only, expect a `405 Method Not
Allowed` from any mutating method:

```powershell
try {
  Invoke-RestMethod -Method POST `
    http://127.0.0.1:8001/api/terminal/trading-plan
} catch {
  $_.Exception.Response.StatusCode  # → MethodNotAllowed (405)
}
```

---

## Validation Commands

Every command below has been run successfully on this branch.

```powershell
# Targeted: safety regression net (Task 3)
py -3.11 -m pytest tests/app/test_safety_invariants.py -q

# Targeted: trading-plan tests (Task 4)
py -3.11 -m pytest tests/app/test_trading_plan.py -q

# Full local backend test suite
py -3.11 -m pytest tests/app/ -q

# Frontend type-check + production build
cd frontend
npm run build
```

Expected results on this branch:

| Command | Result |
|---|---|
| `pytest tests/app/test_safety_invariants.py -q` | 39 passed |
| `pytest tests/app/test_trading_plan.py -q` | 10 passed |
| `pytest tests/app/ -q` | 145 passed |
| `npm run build` | TypeScript clean, Vite production bundle built |

---

## Screenshot Checklist

When recording a demo or attaching screenshots to a portfolio entry,
capture the following six views in this order:

1. **Safety banner** — green pills across the top of any page.
2. **Audit feed with `safety_note`** — Audit Trail page filtered by
   `safety` severity, showing the per-event explanation.
3. **Daily Trading Plan Preview** — Dashboard card with `READ-ONLY PLAN
   PREVIEW` and `NO ORDERS PLACED` tags visible, plus at least three
   instrument rows.
4. **Degraded / empty / loading state** — Stop the backend, refresh the
   Positions page, capture the red "Backend unavailable" card with the
   "Last successful update at …" line.
5. **Passing backend tests** — terminal output of
   `pytest tests/app/ -q` showing `145 passed`.
6. **Passing frontend build** — terminal output of `npm run build`
   showing `built in <N> ms` with no TypeScript errors.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Address already in use` on 8001 | Another Uvicorn / FastAPI process is bound to the port | `Get-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess` then stop it, or pass `--port 8002` and update `VITE_API_BASE_URL` accordingly |
| Vite picks port 5174 / 5175 | 5173 was busy and Vite auto-incremented | Either close the other dev server or open the URL printed in the Vite startup banner |
| Dashboard shows "Backend unavailable" | Uvicorn not running or bound to a different host/port | Confirm Uvicorn is on `127.0.0.1:8001` and that no firewall rule blocks loopback |
| `npm ERR! missing` after `npm install` | Stale `node_modules` from a different Node version | Delete `frontend/node_modules/` and re-run `npm install` |
| `ModuleNotFoundError` from Uvicorn | Wrong working directory | Always run Uvicorn from the **repository root**, not from `frontend/` or `app/` |
| Safety pills are muted/grey | `/api/health` returned an error | Check the Uvicorn log; the pills will recover once `/api/health` returns 200 |
| `gh` says "not authenticated" | GitHub CLI is not signed in | This is **fine for the local demo** — `gh` is only needed when you want to push or open a PR |

---

## What Is Intentionally Not Supported Yet

The Terminal V1 surface deliberately excludes the following. Each
absence is a design decision, not an oversight, and several are
enforced by automated tests:

- **Live trading.** No code path in Terminal V1 sends orders to a real
  broker.
- **Order placement.** No `POST /orders`, no `POST /trade`, no order
  ticket schema.
- **Order buttons.** No "Place Order", "Execute Trade", "Submit Order",
  or "Send Live Order" UI affordance — `tests/app/test_safety_invariants.py`
  fails the build if such text appears in any Terminal V1 page.
- **Broker write actions.** The only mutating broker route is
  `POST /broker/dry-run-report`, which is allowlisted and explicitly
  dry-run only. It is not exposed in the Terminal V1 UI.
- **MT5 / IBKR live execution.** No live MetaTrader5 or IBKR Paper
  *or* live order submission from this surface.
- **Account funding / withdrawal.** Out of scope at every layer.
- **Automatic trade execution.** `autotrade.enabled` is `false` and the
  safety regression test fails if it ever flips to `true` in the
  committed `config.json`.

If a future iteration adds any of the above, it will require an
explicit, separate change with its own review and tests — adding it
would make the Task 3 safety-invariants test fail by design.

---

## Portfolio Explanation

MellyTrade Terminal V1 demonstrates a **safety-first full-stack trading
terminal prototype**: a FastAPI backend with strict GET-only Pydantic
contracts, a React + TypeScript + Vite dashboard with a shared
`<ResourceState>` shell for loading / empty / degraded / last-updated
states, an explicit read-only audit event model with per-event safety
explanations, a static Daily Trading Plan card that is structurally
incapable of representing an order ticket, and a regression test layer
that codifies the dry-run posture as enforceable invariants. The
project is deliberately framed as a prototype rather than a production
trading system; live trading remains out of scope and is blocked by
both code structure and tests.

---

**Last updated**: 2026-05-08
