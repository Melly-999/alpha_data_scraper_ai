# Render, Vercel, and Sevalla Deployment Matrix

| Platform | Best For | Use Now? | Risk | Notes |
|---|---|---|---|---|
| Render | FastAPI backend demo | Yes | Low-Med | Backend web service |
| Vercel | React/Vite frontend demo | Yes | Low | Static frontend/previews |
| Sevalla | Optional PaaS backup | Later | Low-Med | Salvage small PR if needed |
| Localhost | Dev/smoke | Always | Low | Safe local testing |
| EXE/Desktop | Future local demo | Later | Med | Needs packaging decision |

## Environment Safety

All demo deployments run in read-only / dry-run mode. Secrets are never stored
in the repository or in any browser-visible frontend variable.

### Render demo env (backend dashboard)

- `APP_ENV=demo`
- `READ_ONLY=true`
- `DRY_RUN=true`
- `LIVE_ORDERS_BLOCKED=true`
- `AUTOTRADE_ENABLED=false`
- `EXECUTION_ENABLED=false`
- `BROKER_MODE=safe-disconnected`
- `MT5_ENABLED=false`
- `IBKR_ENABLED=false`

### Vercel frontend env

- `VITE_MELLY_API_BASE_URL=https://<render-backend-url>`
- `VITE_READ_ONLY=true`
- `VITE_PUBLIC_DEMO_MODE=true`
- `VITE_LIVE_ORDERS_BLOCKED=true`
- `VITE_EXECUTION_ENABLED=false`

### Forbidden for frontend (never set as `VITE_` or commit)

- `MT5_LOGIN`
- `MT5_PASSWORD`
- `IBKR_ACCOUNT_ID`
- `BROKER_API_KEY`
- `LIVE_BROKER_TOKEN`
- `CLAUDE_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GITHUB_TOKEN`
- `DD_API_KEY`

**Note:** `VITE_` variables are visible in the browser and must **never**
contain secrets. Any real credential belongs only in a backend host's secret
store, never in frontend env or the repository.
