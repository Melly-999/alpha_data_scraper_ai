# Render Read-Only Backend Runbook

> DEMO-DEPLOY-001. Docs/runbook only — this does **not** deploy anything and adds
> no platform config (`render.yaml`, Dockerfiles, `.env`) to the repository.

## Purpose

Render hosts the FastAPI backend demo in **read-only** mode. The backend serves
GET-only read/preview endpoints; it never enables live trading or broker
execution.

## Backend Command

Expected start command (verify the actual entrypoint before applying):

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

> Confirm the real module path in `mellytrade_v3/mellytrade-api` before applying;
> the working directory / module path may differ. Do not change app code to fit
> the host — adjust the Render start command instead.

## Required Safety Env (placeholders only — set in the Render dashboard)

```
APP_ENV=demo
READ_ONLY=true
DRY_RUN=true
LIVE_ORDERS_BLOCKED=true
AUTOTRADE_ENABLED=false
EXECUTION_ENABLED=false
BROKER_MODE=safe-disconnected
MT5_ENABLED=false
IBKR_ENABLED=false
```

## Forbidden Env (never set for the demo; never commit)

- `MT5_LOGIN`
- `MT5_PASSWORD`
- `IBKR_ACCOUNT_ID`
- `BROKER_API_KEY`
- `LIVE_BROKER_TOKEN`
- `CLAUDE_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GITHUB_TOKEN`

## Health Checks

- `/health`
- `/api/health`
- `/api/safety/status` (if available)

## CORS

- Allow only the Vercel demo origin and the local dev origin.
- Do **not** use a wildcard origin for the production demo unless temporary and
  explicitly documented with a removal date.

## Smoke Checklist

- [ ] deploy builds
- [ ] health endpoint returns 200
- [ ] safety flags confirm read-only / dry-run / live orders blocked
- [ ] no broker credentials present
- [ ] no live execution path reachable
