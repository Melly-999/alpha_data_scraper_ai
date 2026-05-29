# DEPLOY-004 — Hosted Backend Smoke Checklist

## 1. Purpose

Use this checklist after a successful Railway or Render backend deployment
(see `backend_demo_deploy_railway_render.md`) to verify that the hosted
backend is safe, read-only, and demo-ready.

---

## 2. Status

| Field | Value |
|---|---|
| Task | DEPLOY-004 / DEPLOY-006D / DEPLOY-008B |
| Scope | Hosted backend smoke — executed and passed (live + staging) |
| Deploy performed | Yes — Render Existing Image (DEPLOY-006D) + Git-connected staging (DEPLOY-008B) |
| Cloud resources created | Yes — `mellytrade-api` (`srv-d8c2o2ugvqtc73e6k7tg`) + `alpha_data_scraper_ai` staging (`srv-d8ckffjbc2fs738761n0`) |
| Secrets committed | No |
| Runtime files changed | No |
| Smoke executed (live) | Yes — 2026-05-28 — 8/8 PASS |
| Smoke executed (staging) | Yes — 2026-05-29 — 8/8 PASS |

### Deployment method note

The standard Render GitHub App OAuth path and the Public Git Repository path
were both blocked by a GitHub account flag — unauthenticated requests to the
repository returned 404. A Docker Hub Existing Image fallback was used instead:

- Image built locally from `Dockerfile.api`
- Pushed to Docker Hub as `docker.io/melly999/mellytrade-api:deploy-006`
- Render Web Service created via **Deploy an existing image from a registry**
- No GitHub connection required

A `.dockerignore` security fix (commit `2bdc192`) was applied and pushed to
`origin/main` before the build to ensure `.env` files and `mellytrade_v3/`
credentials were excluded from the Docker build context.

**DEPLOY-008A/B update (2026-05-29):** The GitHub account flag was subsequently
lifted. The Render GitHub App was installed, granting access to
`Melly-999/alpha_data_scraper_ai`. A separate Git-connected staging service was
created from the GitHub source (see §8). The Existing Image live service was not
modified.

---

## 3. Prerequisites

Before executing any hosted smoke check, verify all of the following locally:

- [x] `runtime.txt` exists at repository root and contains `python-3.11`
- [x] `Dockerfile.api` exists at repository root (added in DEPLOY-003B)
- [x] Safety validation passes locally:

  ```powershell
  py -3.11 scripts/validate_safety_config.py
  ```

  Expected: `OVERALL: PASS`

- [ ] Safety regression tests pass locally:

  ```powershell
  py -3.11 -m pytest tests/app/test_openapi_forbidden_paths.py tests/app/test_safety_invariants.py -q
  ```

- [x] Start command is confirmed:

  ```text
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

  (`$PORT` is injected automatically by Railway and Render.)

- [x] CORS / allowed origins are configured through the hosting dashboard only — not committed to the repo.
- [x] No secrets, tokens, passwords, or API keys are committed to the repository.
- [x] No broker credentials (`MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`) exist in any deployed config file.

---

## 4. Required Safety Env/Config Notes

These safety invariants must hold in the hosted environment. They are enforced by `config.json` and `app/core/settings.py`. Do not override them via platform environment variables.

| Invariant | Required value | How enforced |
|---|---|---|
| `autotrade.enabled` | `false` | `config.json` + safety regression tests |
| `autotrade.dry_run` | `true` | `config.json` + safety regression tests |
| `read_only` | `true` | every emitted audit event, safety endpoint |
| `live_orders_blocked` | `true` | audit event always emitted |
| `execution_enabled` | `false` | response field on every paper preview |
| `max_risk_pct` | `≤ 1.0` | enforced by paper run preview service |

**Do not set `autotrade.enabled=true`, `dry_run=false`, or `execution_enabled=true` in any hosted environment variable.**

---

## 5. Smoke Endpoints

Replace `<hosted-url>` with the Railway or Render deployment URL.
All requests are `GET` only. No `POST`, `PUT`, `PATCH`, or `DELETE` calls.

### 5.1 Health check

```text
GET https://<hosted-url>/health
```

**Expected:**
- HTTP 200
- `status: ok` or equivalent liveness confirmation

```text
GET https://<hosted-url>/api/health
```

**Expected:**
- HTTP 200
- backend reachable, no broker credentials required

### 5.2 Safety status

```text
GET https://<hosted-url>/api/safety/status
```

**Expected:**
- HTTP 200
- `read_only: true`
- `dry_run: true`
- `autotrade_enabled: false` or `autotrade.enabled: false`
- `live_orders_blocked: true`

### 5.3 Paper Run Preview — valid BUY geometry

```text
GET https://<hosted-url>/api/paper/run/preview
    ?symbol=EURUSD
    &side=BUY
    &quantity=1
    &entry_price=1.0800
    &stop_loss=1.0750
    &take_profit=1.0900
    &confidence=72
    &max_risk_pct=0.5
```

**Expected:**
- HTTP 200
- `allowed: true`
- `paper_run` object present (not null)
- `paper_only: true`
- `dry_run: true`
- `read_only: true`
- `live_orders_blocked: true`
- `requires_human_review: true`
- `execution_enabled: false`
- IDs are paper-scoped (`paper_order_*`, `paper_fill_*`, `paper_pos_*`)
- **No** `account_id`, `broker_order_id`, `execution_id`, `trade_id`, `secret`, `token`, `password`, `api_key`

### 5.4 Paper Run Preview — invalid BUY geometry (stop_loss above entry)

```text
GET https://<hosted-url>/api/paper/run/preview
    ?symbol=EURUSD
    &side=BUY
    &quantity=1
    &entry_price=1.0800
    &stop_loss=1.0900
    &take_profit=1.0700
    &confidence=72
    &max_risk_pct=0.5
```

**Expected:**
- HTTP 200 (not an error — validation failures are handled gracefully)
- `allowed: false`
- `paper_run: null`
- `reason` field present and descriptive
- Safety flags (`paper_only`, `dry_run`, `read_only`, `live_orders_blocked`) still present

### 5.5 Paper Run Preview — max_risk_pct exceeds 1% cap

```text
GET https://<hosted-url>/api/paper/run/preview
    ?symbol=EURUSD
    &side=BUY
    &quantity=1
    &entry_price=1.0800
    &stop_loss=1.0750
    &take_profit=1.0900
    &confidence=72
    &max_risk_pct=1.5
```

**Expected:**
- HTTP 200
- `allowed: false`
- `reason` mentions risk cap exceeded (max_risk_pct must not exceed 1.0)
- `paper_run: null`
- Safety flags still present

### 5.6 Method safety — POST must not be accepted

```text
POST https://<hosted-url>/api/paper/run/preview
```

**Expected:**
- HTTP 405 Method Not Allowed

No `POST`, `PUT`, `PATCH`, or `DELETE` method should succeed against the paper run preview endpoint. The route is `GET` only by design.

### 5.7 OpenAPI schema check

```text
GET https://<hosted-url>/openapi.json
```

**Expected:**
- HTTP 200
- Scan response for: `POST /orders`, `POST /execute`, `POST /trade`, `POST /paper/run`
- **None of the above should be present**
- Only `GET /api/paper/run/preview` should appear under paper-run-preview paths

---

## 6. Browser and Frontend Checks

If the hosted frontend (`VITE_API_BASE_URL` pointing to `<hosted-url>`) is also deployed:

- [ ] Paper Run Preview panel loads and returns a response from the hosted backend
- [ ] Safety chips visible: `READ ONLY` · `DRY RUN` · `LIVE ORDERS BLOCKED` · `HUMAN REVIEW REQUIRED` · `EXECUTION OFF`
- [ ] Melly Pet companion visible in AI Workspace right rail (all four chips: `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED`, `EXECUTION OFF`)
- [ ] No `Buy` / `Sell` / `Execute` / `Place Order` buttons present anywhere in the demo UI
- [ ] No broker credentials or account data visible in the UI
- [ ] No horizontal overflow at desktop or iPad viewport

---

## 7. Evidence Table — DEPLOY-006D Execution (2026-05-28)

### 7.1 Deployment details

| Field | Value |
|---|---|
| Date executed | 2026-05-28 |
| Platform | Render (primary) |
| Deploy method | Existing Image from Docker Hub (GitHub OAuth blocked — see §2 note) |
| Service name | `mellytrade-api` |
| Service ID | `srv-d8c2o2ugvqtc73e6k7tg` |
| Public URL | `https://mellytrade-api.onrender.com` |
| Image URL | `docker.io/melly999/mellytrade-api:deploy-006` |
| Image digest | `sha256:8e132094913569c5c3ea9cd96faf1ab718efa06878c87b224a7ece432b3c8d9e` |
| Instance type | Free |
| Health check path | `/health` |
| Env vars added | None |
| Broker credentials added | None |
| Live trading enabled | No |
| Safety posture | Unchanged — confirmed via `/api/safety/status` |
| `.dockerignore` fix | Committed as `2bdc192` before build — `.env`, `.env.*`, `mellytrade_v3/` excluded |

### 7.2 Safety posture confirmed on hosted service

| Invariant | Actual value | Status |
|---|---|---|
| `dry_run` | `true` | ✅ |
| `auto_trade` | `false` | ✅ |
| `read_only` | `true` | ✅ |
| `live_orders_blocked` | `true` | ✅ |
| `execution_enabled` | `false` | ✅ |
| `max_risk_per_trade_pct` | `1.0` | ✅ |

Safety pillars reported by `/api/safety/status`:
`DRY_RUN_ACTIVE` · `READ_ONLY_ACTIVE` · `AUTO_TRADE_DISABLED` · `LIVE_ORDERS_BLOCKED` · `MAX_RISK_CAPPED`

### 7.3 Smoke results

| # | Check | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | `GET /health` | HTTP 200, `status:ok`, `dry_run:true`, `auto_trade:false` | HTTP 200 — confirmed | ✅ PASS |
| 2 | `GET /api/health` | HTTP 200, `status:ok`, fallback mode allowed | HTTP 200 — `fallback_mode:true`, all optional deps `false` | ✅ PASS |
| 3 | `GET /api/safety/status` | `read_only:true`, `dry_run:true`, `live_orders_blocked:true`, `auto_trade:false` | All four confirmed | ✅ PASS |
| 4 | Paper preview — valid BUY (0.5% risk) | `allowed:true`, `execution_enabled:false`, paper-scoped IDs | Confirmed — `allowed:true`, IDs `paper-run-*`/`paper-order-*`/`paper-fill-*`/`paper-pos-*` | ✅ PASS |
| 5 | Paper preview — risk cap exceeded (1.5%) | `allowed:false`, `paper_run:null`, reason mentions cap | `allowed:false`, `paper_run:null`, reason: "max_risk_pct 1.5000 exceeds the maximum permitted per-trade risk of 1.0" | ✅ PASS |
| 6 | `POST /api/paper/run/preview` | HTTP 405 | HTTP 405 `{"detail":"Method Not Allowed"}` | ✅ PASS |
| 7 | OpenAPI — no forbidden execution routes | No `POST /orders`, `POST /execute`, `POST /trade` | `/api/orders` is GET-only. 3 POST routes present: `dry-run-report` (report), `paper/tickets/draft` (paper sandbox, no broker execution), `risk/emergency-stop` (risk control). No forbidden patterns. | ✅ PASS |
| 8 | Forbidden field scan on paper preview response | No `account_id`, `broker_order_id`, `execution_id`, `trade_id`, `secret`, `token`, `password`, `api_key` | None found — all IDs paper-scoped | ✅ PASS |
| 9 | Frontend safety chips | All 5 chips visible | Not yet tested — hosted frontend not yet deployed against this backend URL | ⬜ PENDING |
| 10 | Melly Pet visible | All 4 chips | Not yet tested | ⬜ PENDING |
| 11 | No order buttons | None present | Not yet tested | ⬜ PENDING |

Backend smoke: **8/8 PASS**. Frontend smoke: pending hosted frontend deploy (PWA-DEMO-002).

### 7.4 OpenAPI scan detail

All routes exposed by the hosted service (`GET https://mellytrade-api.onrender.com/openapi.json`):

- All paper-run-preview paths: `GET /api/paper/run/preview` only (no POST variant)
- `/api/orders`: GET only (read-only history, not execution)
- POST routes: `POST /api/broker/dry-run-report`, `POST /api/paper/tickets/draft`, `POST /api/risk/emergency-stop`
- None of the forbidden patterns (`POST /orders`, `POST /execute`, `POST /trade`) are present

### 7.5 External evidence path (do not commit)

```text
C:\AI\MellyTrade_Workspace\screenshots\deploy-007-hosted-render-smoke\
```

Recommended filename pattern:

```text
deploy_007_01_health_response.png
deploy_007_02_api_health_response.png
deploy_007_03_safety_status_response.png
deploy_007_04_paper_preview_valid_buy.png
deploy_007_05_paper_preview_risk_cap.png
deploy_007_06_post_405.png
deploy_007_07_openapi_schema.png
deploy_007_08_forbidden_field_scan.png
```

---

## 8. Evidence Table — DEPLOY-008B Git-Connected Staging (2026-05-29)

### 8.1 Deployment details

| Field | Value |
|---|---|
| Date executed | 2026-05-29 |
| Platform | Render |
| Deploy method | Git-connected — GitHub `Melly-999/alpha_data_scraper_ai`, branch `main` |
| Service name | `alpha_data_scraper_ai` |
| Service ID | `srv-d8ckffjbc2fs738761n0` |
| Staging URL | `https://alpha-data-scraper-ai.onrender.com` |
| Dockerfile Path | `Dockerfile.api` |
| Start Command | Empty (image CMD handles uvicorn) |
| Health check path | `/health` |
| Instance type | Free |
| Env vars added | None |
| Broker credentials added | None |
| Live trading enabled | No |
| Existing live service touched | No — `mellytrade-api` untouched throughout |

### 8.2 Root cause and fix

| Item | Detail |
|---|---|
| Initial failure | Render auto-detected root `Dockerfile` (targets Alpha AI Scheduler CLI, not FastAPI) |
| Symptom | Logs showed "Alpha AI Scheduler started" and "No open ports detected" |
| Root cause | Root `Dockerfile` starts the scheduler process; it does not bind a port |
| Fix applied | Render dashboard: **Dockerfile Path** changed from blank → `Dockerfile.api` |
| Redeploy method | Manual Deploy → Clear build cache & deploy |
| Result after fix | `INFO: Uvicorn running on http://0.0.0.0:10000` — FastAPI confirmed |
| Repo files changed | None — dashboard-only fix |

### 8.3 Safety posture confirmed on staging

| Invariant | Actual value | Status |
|---|---|---|
| `dry_run` | `true` | ✅ |
| `auto_trade` | `false` | ✅ |
| `read_only` | `true` | ✅ |
| `live_orders_blocked` | `true` | ✅ |
| `execution_enabled` | `false` | ✅ |
| `max_risk_per_trade_pct` | `1.0` | ✅ |

Safety pillars: `DRY_RUN_ACTIVE` · `READ_ONLY_ACTIVE` · `AUTO_TRADE_DISABLED` · `LIVE_ORDERS_BLOCKED` · `MAX_RISK_CAPPED`

### 8.4 Smoke results

| # | Check | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | `GET /health` | HTTP 200, `status:ok`, `dry_run:true`, `auto_trade:false` | HTTP 200 — confirmed | ✅ PASS |
| 2 | `GET /api/health` | HTTP 200, `status:ok`, fallback mode allowed | HTTP 200 — `fallback_mode:true` | ✅ PASS |
| 3 | `GET /api/safety/status` | `read_only:true`, `dry_run:true`, `live_orders_blocked:true`, `auto_trade:false` | All four confirmed | ✅ PASS |
| 4 | Paper preview — valid BUY (0.5% risk) | `allowed:true`, `execution_enabled:false`, paper-scoped IDs | Confirmed — `allowed:true`, all safety flags present | ✅ PASS |
| 5 | Paper preview — risk cap (1.5%) | `allowed:false`, `paper_run:null`, reason mentions cap | `allowed:false`, `paper_run:null`, reason: "max_risk_pct 1.5000 exceeds the maximum permitted per-trade risk of 1.0" | ✅ PASS |
| 6 | `POST /api/paper/run/preview` | HTTP 405 | HTTP 405 `{"detail":"Method Not Allowed"}` | ✅ PASS |
| 7 | OpenAPI — no forbidden execution routes | No `POST /orders`, `POST /execute`, `POST /trade` | `/api/orders` GET-only; 3 POST routes all safe (report, paper sandbox, emergency-stop) | ✅ PASS |
| 8 | Forbidden field scan | No sensitive fields in paper preview response | PASS — no `account_id`, `broker_order_id`, `execution_id`, `secret`, `token`, `password`, `api_key` | ✅ PASS |

Staging smoke: **8/8 PASS**

### 8.5 Service roles

Both Render services are live and operate independently:

| Service name | URL | Source | Role |
|---|---|---|---|
| `mellytrade-api` | `https://mellytrade-api.onrender.com` | Docker Hub Existing Image `deploy-006` | **Stable demo / recruiter URL** — version-pinned, no auto-deploy |
| `alpha_data_scraper_ai` | `https://alpha-data-scraper-ai.onrender.com` | GitHub `main` (Git-connected) | **Staging** — tracks `main`, validates each push before promoting to stable demo |

Promotion path: when staging smoke passes after a `main` push, build a new Docker image tag (e.g. `deploy-007`), push to Docker Hub, and update the Existing Image service manually. The stable demo URL never changes.

### 8.6 External evidence path (do not commit)

```text
C:\AI\MellyTrade_Workspace\screenshots\deploy-008-staging-smoke\
```

Recommended filename pattern:

```text
deploy_008_01_health_response.png
deploy_008_02_api_health_response.png
deploy_008_03_safety_status_response.png
deploy_008_04_paper_preview_valid_buy.png
deploy_008_05_paper_preview_risk_cap.png
deploy_008_06_post_405.png
deploy_008_07_openapi_schema.png
deploy_008_08_forbidden_field_scan.png
```

---

## 9. Rollback and Failure Notes

If any check fails:

- Keep the demo in **local or mock mode** — the existing LAN / Tailscale path documented in `docs/demo/demo_009_ipad_pwa_smoke_evidence.md` remains a valid fallback.
- Do **not** attempt to fix a failed hosted deployment by enabling live execution, relaxing safety flags, or adding broker credentials.
- Do **not** add secrets or credentials to the repository to resolve a startup failure.
- If the backend fails to start, check the hosting platform logs. Common issues:
  - Missing `requirements.txt` dependency — fix in `requirements.txt`, do not modify `Dockerfile.api` without a separate review.
  - `PORT` not injected — confirm the start command uses `$PORT`, not a hardcoded port.
  - Import error — run `py -3.11 -m pytest tests/app/ -q` locally first.
- If safety validation fails on the hosted endpoint, take the service offline and investigate before sharing any demo URL.

---

## 10. Do Not Do List

| Forbidden action | Reason |
|---|---|
| Enable `autotrade.enabled=true` in hosted env | Safety posture — live trading is intentionally disabled |
| Set `dry_run=false` in any deployed config | Safety posture — dry-run must stay enabled |
| Commit secrets, tokens, passwords, or API keys | Security — use platform dashboard only |
| Add `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER` for a demo | No broker account connection needed or permitted |
| Enable a `POST /execute`, `POST /orders`, or `POST /trade` route | No execution routes in a demo deploy |
| Commit screenshots, logs, traces, or videos to the repo | Binary artifacts must stay outside the repo |
| Make live trading or profit claims about the hosted demo | This is a paper-only preview demo |
| Expose `execution_enabled=true` | Hardcoded to false in the paper run preview response |

---

## 11. Cross-References

- [DEPLOY-002 Backend Entrypoint and Health Audit](backend_entrypoint_health_audit.md)
- [DEPLOY-005 Platform Choice + Manual Deploy Plan](platform_choice_manual_deploy_plan.md)
- [Backend Demo Deploy Guide — Railway / Render](backend_demo_deploy_railway_render.md)
- [iPad PWA Paper Run Preview Showcase](../showcase/ipad_pwa_paper_run_preview.md)
- [DEMO-MASCOT-001 Melly Pet Evidence](../demo/demo_mascot_001_melly_pet_evidence.md)
- [DEMO-009 iPad PWA smoke evidence](../demo/demo_009_ipad_pwa_smoke_evidence.md)
- [Safety validation script](../../scripts/validate_safety_config.py)
- [`Dockerfile.api`](../../Dockerfile.api)
- [`runtime.txt`](../../runtime.txt)
