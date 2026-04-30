# MellyTrade Local Workstation Release Notes

## Status

This release note describes the current stable MellyTrade local workstation checkpoint for development and demo use.

The project now has a local FastAPI backend, React/Vite frontend, IBKR Paper Adapter v1, dashboard Broker Card, Local Demo Checklist, safe disconnected broker mode, and a dry-run/read-only safety posture. It is suitable for local workstation validation and paper-readiness review. It is not a live-trading release.

## What shipped

### Backend / API

- FastAPI health endpoints at `/health` and `/api/health`
- broker health and account endpoints at `/api/broker/health` and `/api/broker/account`
- read-only local checklist endpoint at `GET /api/local/checklist`
- typed schemas for broker and local checklist responses
- safe disconnected broker snapshots when TWS Paper is not running

### Broker / IBKR Paper

- IBKR Paper Adapter v1
- paper mode defaults
- paper port `7497`
- live ports blocked, including `7496`
- `supports_live_orders=false`
- TWS Paper is optional for the local demo

### Frontend / Dashboard

- Remix-inspired dashboard shell
- shared component polish
- passive page visual alignment
- read-only Broker Card
- Local Demo Checklist card
- disconnected/setup-pending UX for TWS Paper not running

### Local tooling

- `scripts/start_backend_ibkr_paper.ps1`
- `scripts/start_frontend.ps1`
- `scripts/smoke_ibkr_paper.ps1`
- local demo checklist docs in `docs/LOCAL_DEMO_CHECKLIST.md`

### Build / Quality

- frontend TypeScript build fixed
- typed frontend API client in `frontend/src/lib/api.ts`
- Vite environment types
- backend tests green

## Verified local checkpoint

Latest verified local results:

- frontend build passed
- TypeScript errors: 0
- backend tests: 38 passed
- smoke test: passed
- dashboard HTTP 200
- `/api/local/checklist` reachable
- checklist degraded only because TWS Paper is disconnected

Key checklist safety checks:

- Backend API: pass
- Dry-run mode: pass
- Auto-trade: pass
- Broker live orders: pass
- Broker mode/status: warn when disconnected/setup-pending

## Safety posture

- `autotrade.enabled=false`
- `dry_run=true`
- `supports_live_orders=false`
- `live_orders_blocked=true`
- no live trading
- no real orders
- no order buttons
- no reconnect/order controls
- MT5 execution untouched
- risk settings untouched
- TWS Paper optional
- Read-Only API recommended if TWS is configured

## How to run locally

Backend:

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\start_backend_ibkr_paper.ps1
```

Frontend:

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\start_frontend.ps1
```

Smoke:

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\smoke_ibkr_paper.ps1
```

Dashboard:

```text
http://127.0.0.1:5173/dashboard
```

Checklist endpoint:

```text
http://127.0.0.1:8001/api/local/checklist
```

## Known limitations

- real IBKR/TWS Paper connection is optional and may remain disconnected
- disconnected broker state is expected and safe without TWS
- no live trading
- no order execution
- no production deployment claim
- current scope is local workstation, development, and paper-readiness validation

## Next milestones

- optional TWS Paper connected-state validation
- portfolio/positions UX polish
- audit log visibility
- read-only analytics/backtest summary polish
- documentation polish for portfolio presentation

Future milestones should remain safe and read-only unless explicit approval is given for a broader scope.
