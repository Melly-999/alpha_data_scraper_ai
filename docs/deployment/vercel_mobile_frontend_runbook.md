# Vercel Mobile Frontend Runbook

> DEMO-DEPLOY-002. Docs/runbook only — adds no `vercel.json` or platform config
> to the repository and performs no deploy.

## Purpose

Vercel hosts the React/Vite mobile/frontend demo, pointing at the Render backend.

## Project Settings

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Install command: `npm ci` (or `npm install` if no lockfile is present)
- Framework preset: Vite

## Required Frontend Env (placeholders only — public by design)

```
VITE_API_BASE_URL=https://<render-backend-url>/api
VITE_MELLY_API_BASE_URL=https://<render-backend-url>/api
VITE_READ_ONLY=true
VITE_PUBLIC_DEMO_MODE=true
VITE_LIVE_ORDERS_BLOCKED=true
VITE_EXECUTION_ENABLED=false
```

> `VITE_` variables are embedded in the browser bundle and are **public**. Never
> place secrets, broker credentials, or API keys in any `VITE_` variable.

## Routes to Test

- `/`
- `/terminal`
- `/mobile`
- `/terminal/paper-run-preview` (if present)

## Smoke Checklist

- [ ] Vercel build passes
- [ ] `/mobile` loads
- [ ] safety badges visible (READ ONLY · DRY RUN · LIVE ORDERS BLOCKED · HUMAN REVIEW REQUIRED)
- [ ] no order / buy / sell / execute controls
- [ ] Melly Pet visible
- [ ] mobile viewport clean (no horizontal overflow)
- [ ] backend URL configured (points at Render demo)
- [ ] no console crash
