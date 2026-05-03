# MellyTrade Local Demo Checklist

## Purpose

This checklist documents the known-good Windows local demo flow for MellyTrade as a read-only, dry-run workstation. It is intended for local development, dashboard review, and paper-broker connectivity checks without enabling live trading.

## Safety posture

- `autotrade.enabled=false`
- `dry_run=true`
- `supports_live_orders=false`
- `Live orders: BLOCKED`
- no live trading
- no real orders
- no order buttons
- MT5 execution untouched
- TWS Paper optional

## Prerequisites

- Windows PowerShell
- repository path:

```text
C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
```

- Python virtual environment available
- frontend dependencies installed with `npm install`
- TWS Paper optional; it is not required for the disconnected demo

## 1. Sync repo

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
git fetch origin --prune
git switch main-synced
git reset --hard origin/main
git status --short --branch
git --no-pager log --oneline --decorate -n 8
```

Expected:

- clean status
- latest main commit visible

## 2. Frontend build check

```powershell
cd frontend
npm install
npm run build
cd ..
```

Expected:

- build passes
- 0 TypeScript errors

## 3. Backend tests

```powershell
python -m pytest tests/app/test_api_contracts.py tests/app/test_broker_routes.py tests/test_ibkr_paper_adapter.py -q
```

Expected:

- current app test suite passes
- targeted backend tests pass

## 4. Start backend

```powershell
.\scripts\start_backend_ibkr_paper.ps1
```

Expected:

- backend starts on `127.0.0.1:8001`
- `/health` returns 200
- `dry_run=true`
- `auto_trade=false`

## 5. Start frontend

```powershell
.\scripts\start_frontend.ps1
```

Expected:

- frontend starts on `127.0.0.1:5173`
- dashboard reachable at:

```text
http://127.0.0.1:5173/dashboard
```

## 6. Run smoke test

```powershell
.\scripts\smoke_ibkr_paper.ps1
```

Expected:

- `/health` OK
- `/api/health` OK
- `/api/broker/health` OK
- `/api/broker/account` OK
- `/api/broker/dry-run-report` OK dry-run report only
- no live orders

## 7. Expected dashboard state

- Remix UI visible
- Broker Card visible
- Local Demo Checklist visible
- disconnected/setup-pending UX if TWS Paper is not running
- `Live orders: BLOCKED`
- `supports_live_orders=false`
- no order buttons
- no reconnect controls
- account/cash unavailable if disconnected

## 8. Dashboard Local Demo Checklist

The dashboard includes a read-only **Local Demo Checklist** card. It is backed by:

```text
GET /api/local/checklist
```

This endpoint aggregates existing backend safety state and broker health snapshots. It does not mutate config, connect to live trading, place orders, or call execution endpoints.

Checks:

- Backend API: FastAPI is responding.
- Dry-run mode: expected `dry_run=true`.
- Auto-trade: expected `auto_trade=false`.
- Broker live orders: expected `supports_live_orders=false`.
- Broker mode/status: paper connected is good; disconnected/setup-pending is safe; live-port configuration is degraded/blocked.

Expected good state:

- Backend API `pass`
- Dry-run mode `pass`
- Auto-trade `pass`
- Broker live orders `pass`
- Broker mode/status `pass` if TWS Paper is connected, or `warn` if TWS Paper is not running

Broker disconnected can still be safe because the adapter remains read-only, live orders remain blocked, and the dashboard exposes no order controls.

Troubleshooting:

- If Backend API is unavailable, start `.\scripts\start_backend_ibkr_paper.ps1`.
- If Dry-run or Auto-trade checks fail, stop and inspect config before continuing.
- If Broker mode/status warns, verify TWS Paper setup only when you need a connected paper session.
- If Broker mode/status fails because a live port is configured, use paper port `7497`.

## 9. TWS Paper optional

TWS Paper is not required for the local demo. Without TWS, the Broker Card shows a safe disconnected/setup-pending state.

If configuring TWS later:

- PaperTrader login
- API socket enabled
- port `7497`
- Trusted IP `127.0.0.1`
- Read-Only API ON

## 10. Troubleshooting

- backend not running: start it with `.\scripts\start_backend_ibkr_paper.ps1`
- frontend port busy: close the old dev server or use the Vite URL shown in the terminal
- smoke fails on `/health`: backend is not running
- broker disconnected: normal without TWS Paper
- do not use live port `7496`
- do not turn off Read-Only API for validation

## 11. Signal Decision History

`GET /api/signals/decisions` returns a read-only log of dry-run signal decisions.

Smoke check:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/api/signals/decisions
```

Expected response fields:

- `dry_run: true`
- `auto_trade: false`
- `read_only: true`
- `decisions`: array of decision records (7 seed records by default)
- `total`: count matching `len(decisions)`

Each decision record includes `dry_run=true`, `auto_trade=false`, `read_only=true`, `stop_loss_required=true`, `take_profit_required=true`, `max_risk_per_trade=0.01`.

Filter by symbol:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/signals/decisions?symbol=AAPL"
```

Safety invariants:

- GET-only — no mutation, no order placement, no broker connection, no MT5 execution
- All records have `dry_run=true` and `auto_trade=false`
- `max_risk_per_trade` is capped at `0.01` (1%)
- Decision values: `dry_run_allowed`, `blocked`, `watch_only`, `no_action`

The Signals page in the dashboard shows the Decision History section below the signal table.

## 12. Signal Lifecycle View

`GET /api/signals/lifecycle` returns a read-only explanation of each signal path:

```text
signal received
-> confidence checked
-> risk checked
-> broker safety checked
-> dry-run decision
-> blocked/allowed reason
-> audit event reference
```

Smoke check:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/api/signals/lifecycle
```

Expected response fields:

- `dry_run: true`
- `auto_trade: false`
- `read_only: true`
- `supports_live_orders: false`
- `lifecycle`: array of signal lifecycle records
- every record has `order_placed: false`
- every record has `max_risk_per_trade <= 0.01`

Filter by symbol:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/signals/lifecycle?symbol=AAPL"
```

Filter by decision or risk status:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/signals/lifecycle?decision=blocked"
Invoke-RestMethod "http://127.0.0.1:8001/api/signals/lifecycle?risk_status=pass"
Invoke-RestMethod "http://127.0.0.1:8001/api/signals/lifecycle?symbol=AAPL&decision=blocked"
```

Filters are read-only GET query parameters. They do not trigger execution,
connect to a broker, place orders, or call MT5 execution. `dry_run_allowed`
is a review-only dry-run state; it is not an order. Blocked filters are useful
for debugging why signals stop at safety gates. Empty results are safe and
expected when filters do not match any lifecycle records.

### Export filtered lifecycle records

The Signal Lifecycle panel includes browser-local export actions:

- Export CSV
- Export JSON

Exports include only the currently filtered read-only lifecycle records already
loaded in the dashboard. The download is generated in the browser; the backend
does not write files, persist exports, or create server-side artifacts. Exported
data is for debugging and observability only. Export actions do not place orders,
call broker actions, or call MT5 execution. `dry_run_allowed` still does not mean
an order was placed.

Safety invariants:

- GET-only endpoint
- no mutation, no order placement, no broker connection, no MT5 execution
- `dry_run_allowed` means review-only simulation; it does not mean an order was placed
- audit event references are for observability only and do not imply execution

The Signals page in the dashboard shows the Signal Lifecycle section below Decision History.

## 13. Known good checkpoint

Current verified state:

- frontend build passes with 0 TypeScript errors
- current app test suite passes
- targeted backend tests pass
- smoke passed
- dashboard HTTP 200
- repo clean and synced
