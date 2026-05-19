# MellyTrade Terminal Demo

An institutional-style, read-only AI trading terminal focused on advisory analysis, paper sandbox visibility, and conservative risk posture.

## Screenshot Placeholders
- `![Terminal AI Workspace](path/to/01_terminal_ai_workspace_1366x768.png)`
- `![Paper Sandbox Activity Rail](path/to/03_terminal_paper_sandbox_activity_1366x768.png)`
- `![Read-only Signals](path/to/04_signals_readonly_1366x768.png)`
- `![Broker Posture](path/to/05_brokers_readonly_1366x768.png)`
- `![Portfolio Read-only View](path/to/06_portfolio_readonly_1366x768.png)`

## Architecture
- React + Vite frontend
- FastAPI backend
- Paper Sandbox Preview and History are consumed as GET-only status surfaces
- Paper Sandbox Activity/Audit Rail highlights recent read-only events
- AI Workspace remains advisory-only
- Terminal shell uses an institutional dark theme with a red-black frame treatment

## Safety Posture
- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `max risk <= 1%`

## Validation Checklist
- Safety configuration validation passes
- OpenAPI forbidden-path tests pass
- Safety invariants tests pass
- Frontend build passes
- Demo smoke validates paper sandbox preview/history and frontend routes

## Local Demo Commands
```powershell
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8001
cd frontend
npm run dev
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/demo_paper_sandbox_readonly_smoke.ps1 -BackendBaseUrl http://127.0.0.1:8001 -FrontendBaseUrl http://127.0.0.1:5173
```

## Current Limitations
- No live execution controls
- No order placement UI
- No connect-live broker flow
- Demo data may degrade gracefully when backend services are offline
- Screenshot paths are intentionally placeholders only; no binary assets are committed

