# DEPLOY-005 — Platform Choice + Manual Hosted Deploy Plan

## 1. Status

| Field | Value |
|---|---|
| Task | DEPLOY-005 |
| Scope | Platform choice + manual deploy plan — planning only |
| Deploy performed | No |
| Cloud resources created | No |
| Secrets committed | No |
| Screenshots/binaries committed | No |
| Runtime files changed | No |

---

## 2. Decision Summary

| Platform | Role | Why | Main caution |
|---|---|---|---|
| Render | Primary | Docker web service from repo; Dockerfile Path field in dashboard; PORT-based web service model; clean free tier for demos | Configure Dockerfile Path to `Dockerfile.api`; keep all env vars in dashboard only |
| Railway | Fallback | Valid GitHub + Docker deploy option; auto-detects most settings | Must point to `Dockerfile.api`, not root `Dockerfile`; use `RAILWAY_DOCKERFILE_PATH` or platform UI; shell expansion for PORT needed if overriding CMD |

**Render is the recommended primary platform.** Render's Docker web service model explicitly supports setting a custom Dockerfile path in the dashboard. The existing `Dockerfile.api` uses shell-form CMD so `${PORT:-8000}` expansion works correctly in both environments.

---

## 3. Shared Backend Facts

| Field | Value |
|---|---|
| FastAPI entrypoint | `app.main:app` |
| Dockerfile | `Dockerfile.api` (at repository root) |
| Runtime pin | `python-3.11` (via `runtime.txt`) |
| CMD in `Dockerfile.api` | `sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"` |
| Default port | 8000 (overridden by `PORT` injected by platform) |
| CORS env var | `MELLYTRADE_ALLOWED_ORIGINS` (set in dashboard; required if hosted frontend deployed separately) |

### 3.1 Required health / smoke endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Liveness — platform health check |
| `/api/health` | GET | Application health |
| `/api/safety/status` | GET | Safety posture confirmation |
| `/api/paper/run/preview` | GET | Paper run preview (read-only) |

### 3.2 Safety defaults (must remain unchanged)

| Invariant | Required value |
|---|---|
| `autotrade.enabled` | `false` |
| `autotrade.dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| `execution_enabled` | `false` |
| `max_risk_pct` | `≤ 1.0` |

These are enforced by `config.json` and `app/core/settings.py`. Do not override via platform environment variables.

---

## 4. Render Manual Setup Plan

> **Planning only.** Do not execute until explicitly approved.
>
> Before starting: run `py -3.11 scripts/validate_safety_config.py` locally and confirm OVERALL: PASS.

### 4.1 Dashboard steps (manual)

1. Create a Render account at render.com (free tier is sufficient for a demo).
2. Create a new **Web Service**.
3. Connect the GitHub repository (`alpha_data_scraper_ai`).
4. Select the `main` branch as the deploy branch.
5. Choose **Docker** as the runtime (not Python/pip).
6. In the **Dockerfile Path** field, enter `Dockerfile.api`.
   Leave the Docker Build Context as the repository root (default).
7. Leave the Start Command empty — the `CMD` in `Dockerfile.api` handles the start.
   The CMD uses shell form: `sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"`
   Render injects `PORT` automatically; the shell form expands it correctly.
8. Set the **Health Check Path** to `/health`.
9. Configure environment variables only through the Render **Environment** tab in the dashboard.
   Do not commit any env var values to the repository.
10. Required env vars for a read-only demo (add only what the app needs to start):
    - `MELLYTRADE_ALLOWED_ORIGINS` — set to the hosted frontend origin if a hosted frontend is deployed; omit if only testing the API directly.
    - `CLAUDE_API_KEY` — add only if Claude AI validation is needed for the demo; omit otherwise.
    - `NEWSAPI_KEY` — add only if news sentiment is needed for the demo; omit otherwise.
    - Do **not** add `MT5_LOGIN`, `MT5_PASSWORD`, or `MT5_SERVER`.
11. Do not deploy until explicitly approved.
12. After a successful deploy, run the DEPLOY-004 smoke checklist in full:
    `docs/deployment/hosted_backend_smoke_checklist.md`

### 4.2 Env var policy for Render

- No broker credentials (`MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`).
- No IBKR or Alpaca credentials.
- Do not set `autotrade.enabled=true`, `dry_run=false`, or `execution_enabled=true`.
- All secrets stay in the Render dashboard; never committed to the repo.
- `MELLYTRADE_ALLOWED_ORIGINS` is the only CORS-related env var; set it to the frontend URL once one exists.

### 4.3 What to verify after first Render deploy

See §6 (smoke tests) and `docs/deployment/hosted_backend_smoke_checklist.md` for the full checklist.

Minimum confirmation before sharing any demo URL:
- `GET /health` → HTTP 200
- `GET /api/safety/status` → `read_only: true`, `dry_run: true`, `autotrade_enabled: false`
- `GET /api/paper/run/preview?symbol=EURUSD&side=BUY&quantity=1&entry_price=1.0800&stop_loss=1.0750&take_profit=1.0900&confidence=72&max_risk_pct=0.5` → `allowed: true`, `execution_enabled: false`

---

## 5. Railway Fallback Manual Setup Plan

> **Planning only.** Use Railway only if Render is unavailable or unsuitable.
>
> Before starting: run `py -3.11 scripts/validate_safety_config.py` locally and confirm OVERALL: PASS.

### 5.1 Dashboard steps (manual)

1. Create a Railway account at railway.app (free tier is sufficient for a demo).
2. Create a new project.
3. Deploy from GitHub — connect the `alpha_data_scraper_ai` repository.
4. Select the `main` branch.
5. Railway will attempt to auto-detect the runtime. It may pick the root `Dockerfile` (targets the scheduler/bot CLI). This must be overridden.
6. To point Railway at `Dockerfile.api` instead of the root `Dockerfile`, set this Railway variable in the **Variables** tab: `RAILWAY_DOCKERFILE_PATH=Dockerfile.api`.
   Alternatively, use the Railway dashboard's service settings to select the custom Dockerfile path if the UI supports it.
7. Do **not** override the Start Command unless necessary. The `CMD` in `Dockerfile.api` already uses shell form (`sh -c "..."`), so `${PORT:-8000}` expands correctly when Railway injects `PORT`.
   If a Start Command override is required, use shell form: `sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"`
   Railway injects `PORT` automatically. Do not hardcode a port number.
8. Set the health check path to `/health`.
9. Configure all environment variables only in the Railway **Variables** tab.
   Do not commit any values to the repository.
10. Apply the same env var policy as Render (§4.2): no broker credentials, no trading overrides.
11. Do not deploy until explicitly approved.
12. After a successful deploy, run the DEPLOY-004 smoke checklist in full:
    `docs/deployment/hosted_backend_smoke_checklist.md`

### 5.2 Railway caution: Dockerfile path

The root `Dockerfile` and `Dockerfile.prod` target the scheduler/bot CLI, not the FastAPI backend. If Railway deploys from the wrong Dockerfile, the web service will start the wrong process.

Always confirm via Railway logs after deploy that the process is `uvicorn app.main:app`,
not the scheduler (`main.py`) or any other CLI entrypoint.

---

## 6. Required Smoke Tests After First Deploy

Run the full smoke checklist from:
`docs/deployment/hosted_backend_smoke_checklist.md`

Quick reference — all requests are GET only:

| # | Endpoint | Expected |
|---|---|---|
| 1 | `GET /health` | HTTP 200 |
| 2 | `GET /api/health` | HTTP 200 |
| 3 | `GET /api/safety/status` | `read_only:true`, `dry_run:true`, `autotrade_enabled:false` |
| 4 | `GET /api/paper/run/preview` valid BUY | `allowed:true`, `execution_enabled:false` |
| 5 | `GET /api/paper/run/preview` invalid geometry | `allowed:false`, `paper_run:null` |
| 6 | `GET /api/paper/run/preview` `max_risk_pct=1.5` | `allowed:false` |
| 7 | `POST /api/paper/run/preview` | HTTP 405 |
| 8 | `GET /openapi.json` | No `POST /orders`, `POST /execute`, `POST /trade` |
| 9 | Browser: Paper Run Preview + Melly Pet | Safety chips visible, no order buttons |

---

## 7. Rollback and Failure Plan

If the deploy fails or a smoke check fails:

- Keep the demo in **local or mock mode** — the LAN / Tailscale path in `docs/demo/demo_009_ipad_pwa_smoke_evidence.md` remains a valid fallback.
- Do **not** attempt to fix a failed deploy by relaxing safety flags (`autotrade=true`, `dry_run=false`, `execution_enabled=true`).
- Do **not** add secrets or broker credentials to the repository to resolve startup errors.
- If CORS errors occur, set `MELLYTRADE_ALLOWED_ORIGINS` in the platform dashboard only — do not commit the value.
- If the wrong process starts (Railway): verify `RAILWAY_DOCKERFILE_PATH=Dockerfile.api` and check platform logs.
- If `PORT` is not bound: confirm the Dockerfile CMD uses shell form and that the platform injects `PORT` as an env var (it does — both Render and Railway inject `PORT` automatically).
- If app fails to import: run `py -3.11 -m pytest tests/app/ -q` locally first to catch import errors.
- If safety validation fails on the hosted endpoint, take the service offline and investigate before sharing any demo URL.

---

## 8. Do Not Do List

| Forbidden action | Reason |
|---|---|
| Commit secrets, tokens, passwords, or API keys | Security — use platform dashboard only |
| Add `MT5_LOGIN`, `MT5_PASSWORD`, or `MT5_SERVER` to hosted env | No broker connection needed or permitted for a read-only demo |
| Set `autotrade.enabled=true` in any deployed env | Safety posture — live trading is intentionally disabled |
| Set `dry_run=false` in any deployed env | Safety posture — dry-run must stay enabled |
| Set `execution_enabled=true` in any deployed env | Hardcoded to false in paper run preview responses |
| Deploy without explicit approval | Deploy is a separate step, gated on explicit instruction |
| Expose admin, debug, or broker-management endpoints publicly | Out of scope; not present in the read-only demo backend |
| Add order execution routes or order buttons | No execution routes in a demo deploy |
| Make live trading or production readiness claims | This is a paper-only read-only demo |
| Claim guaranteed profit or past performance | This is a paper trading preview demo only |
| Use root `Dockerfile` or `Dockerfile.prod` for the API service | Those target the scheduler/bot CLI, not FastAPI |
| Commit screenshots, logs, traces, or videos to the repo | Binary artifacts must stay outside the repository |

---

## 9. Evidence Checklist

Planning-only. Fill in when the deploy is executed.

| Evidence item | Expected result | Status | Notes |
|---|---|---|---|
| Platform selected | Render (primary) or Railway (fallback) | ☐ | — |
| Service settings reviewed | Dockerfile Path = `Dockerfile.api`, PORT-based | ☐ | — |
| `Dockerfile.api` path confirmed in dashboard | Correct file selected | ☐ | — |
| Env vars reviewed | No broker credentials, no trading overrides | ☐ | — |
| First deploy approval obtained | Explicit user instruction | ☐ | — |
| Smoke checklist run | All 9 smoke checks pass | ☐ | — |
| Screenshots/logs saved outside repo | `C:\AI\MellyTrade_Workspace\screenshots\deploy-005-platform-plan\` | ☐ | — |

**External evidence path (do not commit):**

```text
C:\AI\MellyTrade_Workspace\screenshots\deploy-005-platform-plan\
```

---

## 10. Cross-References

- [DEPLOY-004 Hosted Backend Smoke Checklist](hosted_backend_smoke_checklist.md)
- [DEPLOY-002 Backend Entrypoint and Health Audit](backend_entrypoint_health_audit.md)
- [Backend Demo Deploy Guide — Railway / Render](backend_demo_deploy_railway_render.md)
- [`Dockerfile.api`](../../Dockerfile.api)
- [`runtime.txt`](../../runtime.txt)
