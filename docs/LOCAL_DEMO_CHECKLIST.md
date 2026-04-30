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

- 36 passed or current equivalent
- no blockers

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
- disconnected/setup-pending UX if TWS Paper is not running
- `Live orders: BLOCKED`
- `supports_live_orders=false`
- no order buttons
- no reconnect controls
- account/cash unavailable if disconnected

## 8. TWS Paper optional

TWS Paper is not required for the local demo. Without TWS, the Broker Card shows a safe disconnected/setup-pending state.

If configuring TWS later:

- PaperTrader login
- API socket enabled
- port `7497`
- Trusted IP `127.0.0.1`
- Read-Only API ON

## 9. Troubleshooting

- backend not running: start it with `.\scripts\start_backend_ibkr_paper.ps1`
- frontend port busy: close the old dev server or use the Vite URL shown in the terminal
- smoke fails on `/health`: backend is not running
- broker disconnected: normal without TWS Paper
- do not use live port `7496`
- do not turn off Read-Only API for validation

## 10. Known good checkpoint

Current verified state:

- frontend build passed
- backend tests passed
- smoke passed
- dashboard HTTP 200
- repo clean and synced
