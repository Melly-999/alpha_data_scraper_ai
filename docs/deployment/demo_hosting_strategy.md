# Demo Hosting Strategy

| Layer | Preferred Host | Role |
|---|---|---|
| Backend API | Render | FastAPI read-only demo |
| Frontend Dashboard | Vercel | React/Vite static frontend |
| Alternative PaaS | Sevalla | Backup demo target |
| Local dev | localhost | smoke/development |
| Future desktop | EXE package | local operator demo |

## Purpose

The public demo should be split into a **Render backend** and a **Vercel
frontend**. Render is the better current target for the FastAPI backend, while
Vercel is the best fit for the React/Vite frontend. Sevalla remains an optional
backup target.

## Render Backend

- FastAPI web service
- read-only demo mode
- health checks (`/health`, fallback `/api/health`)
- backend env vars stored in the Render dashboard (not in the repo)
- no secrets in the repo
- no broker credentials
- no live trading

## Vercel Frontend

- React/Vite dashboard
- static build
- `VITE_MELLY_API_BASE_URL` points to the Render backend
- `VITE_` variables are public by design
- no secrets in the Vercel frontend env

## Sevalla Backup

The Sevalla worktree contained a safe, additive deploy concept. It can be
salvaged later as a small deploy PR if a backup target is desired. It is not on
the critical path — Render/Vercel come first.

## Deployment Order

1. Local backend/frontend smoke
2. Render backend runbook
3. Vercel frontend runbook
4. Render backend hosted smoke
5. Vercel frontend hosted smoke
6. E2E hosted smoke
7. iPad/mobile smoke
8. public demo evidence pack

## Non-Goals

- no live trading
- no broker execution
- no real credentials
- no order placement
- no auto-trading demo
- no production profit claims
