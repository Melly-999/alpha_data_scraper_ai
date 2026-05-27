# DEPLOY-002 — Backend Entrypoint and Health Audit

## 1. Purpose

This document records the findings from a local audit of the MellyTrade backend
entrypoint, health endpoints, safety endpoints, and hosted deploy compatibility.
It is a read-only investigation report. No deployment was performed.

Follows: [DEPLOY-001 Backend Demo Deploy Guide](backend_demo_deploy_railway_render.md)

---

## 2. Audit Summary

| Item | Finding | Status |
|---|---|---|
| FastAPI entrypoint | `app.main:app` | VERIFIED |
| Uvicorn start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | VERIFIED |
| Working directory | repository root | VERIFIED |
| `GET /health` (root) | 200 OK, correct payload | VERIFIED LOCAL |
| `GET /api/health` | 200 OK, correct payload | VERIFIED LOCAL |
| `GET /api/safety/status` | 200 OK, safety posture confirmed | VERIFIED LOCAL |
| `GET /api/paper/run/preview` | 200 OK — implemented in PAPER-RUN-API-001 | RESOLVED |
| `requirements.txt` has uvicorn | `uvicorn==0.34.0` | CONFIRMED |
| Dockerfile CMD for FastAPI | Not set — CMD runs scheduler, not FastAPI | GAP |
| CORS env var | `MELLYTRADE_ALLOWED_ORIGINS` required for hosted frontend | ACTION NEEDED |
| Python version declaration | `runtime.txt` added in DEPLOY-003A — pins `python-3.11` for Railway/Render | RESOLVED |
| Startup with no API keys | Starts cleanly in fallback mode, all degradations are logged | VERIFIED |

---

## 3. Backend Entrypoint

### 3.1 FastAPI application object

File: `app/main.py`

```python
app = FastAPI(
    title="MellyTrade Phase 1 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)
```

The object name is `app`. The import path for uvicorn is:

```text
app.main:app
```

### 3.2 Recommended start command for Railway / Render

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Both Railway and Render inject `$PORT` automatically. Do not use `--reload` in
a hosted environment.

### 3.3 Working directory

The working directory must be the **repository root** (the directory that
contains `app/`, `config.json`, `requirements.txt`). The app reads `config.json`
via a relative path (`Path("config.json")`). If the working directory is wrong,
startup will log a config warning but will not crash (defaults are applied).

### 3.4 Python version

Local scripts use `py -3.11`. A `runtime.txt` is now committed at the repository
root (added in DEPLOY-003A) with the content:

```text
python-3.11
```

This pins the Python runtime to 3.11 for Railway and Render hosted deploys.
Railway and Render both detect `runtime.txt` automatically during the build phase.
No patch version is specified; the platform resolves the latest available 3.11
patch release. If a specific patch version is required by the platform at deploy
time, update `runtime.txt` then — do not guess a patch version in advance.

---

## 4. Health Endpoints

Both paths are registered in `app/main.py`:

```python
# Registered under /api prefix (via for-loop at line 125-149)
app.include_router(health.router, prefix="/api")

# Also registered at root (bare path, line 151)
app.include_router(health.router)
```

This results in two valid health paths.

### 4.1 `GET /health` (root, no `/api` prefix)

**Recommended** for Railway/Render health check configuration — shorter path,
no prefix dependency.

Local smoke result:

```json
{
  "status": "ok",
  "service": "MellyTrade Phase 1",
  "version": "0.1.0",
  "uptime_seconds": 1207,
  "dependencies": {
    "mt5": false,
    "claude": false,
    "news": false
  },
  "fallback_mode": true,
  "safety": {
    "max_risk_per_trade": 1.0,
    "max_daily_loss": 2.0,
    "max_drawdown": 5.0,
    "min_confidence": 75,
    "min_rr": 1.5,
    "max_open_positions": 5,
    "max_lot_size": 0.5,
    "cooldown_seconds": 120,
    "allow_same_signal": false,
    "dry_run": true,
    "auto_trade": false,
    "emergency_pause": false
  }
}
```

Key fields to verify on a hosted deploy:

- `"status": "ok"` — backend is running
- `"fallback_mode": true` — expected when no API keys are set; not an error
- `"safety.dry_run": true` — must always be true
- `"safety.auto_trade": false` — must always be false

### 4.2 `GET /api/health`

Same handler as `/health`, registered under the `/api` prefix. Returns identical
payload. Use as a secondary health check if the hosted platform requires an
`/api/`-prefixed path.

---

## 5. Safety Endpoint

### 5.1 `GET /api/safety/status`

Local smoke result:

```json
{
  "dry_run": true,
  "auto_trade": false,
  "read_only": true,
  "live_orders_blocked": true,
  "max_risk_per_trade_pct": 1.0,
  "pillars": [
    "DRY_RUN_ACTIVE",
    "READ_ONLY_ACTIVE",
    "AUTO_TRADE_DISABLED",
    "LIVE_ORDERS_BLOCKED",
    "MAX_RISK_CAPPED"
  ],
  "safety_note": "Terminal V1 is in read-only / dry-run mode. Live orders are blocked, autotrade is disabled, and per-trade risk is capped at 1%. No code path on this surface can submit an order to a real broker.",
  "generated_at": "2026-05-27T07:50:20.361923Z"
}
```

All five safety pillars confirmed: `DRY_RUN_ACTIVE`, `READ_ONLY_ACTIVE`,
`AUTO_TRADE_DISABLED`, `LIVE_ORDERS_BLOCKED`, `MAX_RISK_CAPPED`.

This endpoint is the authoritative hosted-deploy safety check. After any hosted
deploy, confirm all five pillars are present before sharing a demo URL.

---

## 6. ~~Critical Blocker~~ RESOLVED: `GET /api/paper/run/preview` Implemented

**Status: RESOLVED by PAPER-RUN-API-001.**

The Paper Run Preview panel (`PaperRunPreviewPanel.tsx`) calls:

```text
GET /api/paper/run/preview?symbol=...&side=...&...
```

This endpoint is now implemented. Local smoke confirms:

```text
GET /api/paper/run/preview  →  200 OK (allowed)
GET /api/paper/run/preview  →  200 OK (blocked — invalid geometry or risk cap)
```

### Implementation summary

Files added in PAPER-RUN-API-001:

- `app/schemas/paper_run_preview.py` — Pydantic v2 schemas with embedded safety flags
- `app/services/paper_run_preview_service.py` — deterministic, local-only service; no broker calls, no network I/O, no DB writes
- `app/api/routes/paper_run_preview.py` — GET-only router registered in `app/main.py`
- `tests/app/test_paper_run_preview_endpoint.py` — 87 tests covering happy path, blocked geometry, risk cap, method safety, safety flags, forbidden fields, OpenAPI, broker-import scan, config mutation check

### Endpoint contract (matches `paperRunPreviewApi.ts`)

Query params: `symbol`, `side` (`BUY`|`SELL`), `quantity`, `entry_price`,
`stop_loss`, `take_profit`, `confidence`, `max_risk_pct`.

Response always includes:

```typescript
type PaperPreviewSafetyFlags = {
  paper_only: true;
  dry_run: true;
  read_only: true;
  live_orders_blocked: true;
  requires_human_review: true;
  execution_enabled: false;
};
```

Validation rules:

- `max_risk_pct > 1.0` → `allowed: false`, `paper_run: null` (HTTP 200)
- BUY geometry violation (`stop_loss ≥ entry_price` or `entry_price ≥ take_profit`) → `allowed: false`, `paper_run: null` (HTTP 200)
- SELL geometry violation (`stop_loss ≤ entry_price` or `entry_price ≤ take_profit`) → `allowed: false`, `paper_run: null` (HTTP 200)
- All checks pass → `allowed: true`, `paper_run` with one order, fill, and position; all IDs use `paper-*` prefix

### Safety invariants (never mutated)

All six flags are embedded at every nesting level (response, run, order, fill,
position) and enforced by Pydantic `Literal` types. The endpoint never calls any
broker, never writes to any database, never returns `account_id`,
`broker_order_id`, `execution_id`, `trade_id`, `secret`, `token`, `api_key`, or
`password`.

### Impact on hosted demo

The 404 blocker is resolved. A hosted backend deploy will now serve
`GET /api/paper/run/preview` correctly. The Paper Run Preview panel will display
allowed and blocked states as designed.

---

## 7. Full Route Inventory (46 routes — updated by PAPER-RUN-API-001)

The following routes were confirmed from a live `GET /openapi.json` call against
the local backend.

### Read-only routes (GET only)

```text
GET  /api/account/overview
GET  /api/backtest/summary
GET  /api/broker/account
GET  /api/broker/health
GET  /api/brokers
GET  /api/brokers/{adapter_id}/account
GET  /api/brokers/{adapter_id}/positions
GET  /api/brokers/{adapter_id}/status
GET  /api/dashboard/summary
GET  /api/health
GET  /api/investment
GET  /api/local/checklist
GET  /api/logs
GET  /api/market/overview
GET  /api/mt5/status
GET  /api/news/sentiment
GET  /api/orders
GET  /api/paper/run/preview
GET  /api/paper/sandbox/history
GET  /api/paper/sandbox/preview
GET  /api/portfolio/risk-summary
GET  /api/positions/history
GET  /api/positions/open
GET  /api/risk/config
GET  /api/risk/policy
GET  /api/risk/status
GET  /api/risk/violations
GET  /api/safety/status
GET  /api/signals
GET  /api/signals/decisions
GET  /api/signals/feed
GET  /api/signals/lifecycle
GET  /api/signals/quality/summary
GET  /api/signals/scanner/preview
GET  /api/signals/scanner/universes
GET  /api/signals/{signal_id}
GET  /api/signals/{signal_id}/reasoning
GET  /api/supabase/status
GET  /api/terminal/events
GET  /api/terminal/summary
GET  /api/terminal/trading-plan
GET  /api/watchlist
GET  /health
```

### Mutating routes (POST / PUT)

```text
POST /api/broker/dry-run-report   — dry-run report only, no live execution
POST /api/paper/tickets/draft     — paper-only draft, no live execution
PUT  /api/risk/config             — updates in-memory risk config (see §8.4)
POST /api/risk/emergency-stop     — safety pause action only
```

No `POST /orders`, `POST /execute`, `POST /trade`, or live order placement
routes are present. This is confirmed by the validated safety test suite
(`test_openapi_forbidden_paths.py`).

---

## 8. Requirements Compatibility

### 8.1 `requirements.txt` (17 lines — for hosted deploy)

```text
numpy>=1.26,<3.0
pandas==2.2.0
scikit-learn>=1.4,<2.0
yfinance==0.2.41
ib_insync==0.9.86
alpaca-py==0.43.2
PyYAML==6.0.1
httpx==0.28.1
fastapi==0.128.0
SQLAlchemy>=2.0,<3.0
uvicorn==0.34.0
APScheduler==3.10.4
requests==2.32.0
anthropic>=0.50.0
python-dotenv==1.0.0
python-telegram-bot==21.5
openpyxl==3.1.5
```

`uvicorn==0.34.0` is present. `MetaTrader5` is **not** in `requirements.txt`
(Windows-only package; the app degrades gracefully without it).

### 8.2 `requirements-ci.txt` (19 lines — NOT for server start)

Contains `pytest`, `black`, `flake8`, `mypy`, and type stubs. Does **not**
include `uvicorn`. **Do not use as the install target for a hosted backend.**

### 8.3 Broker adapter packages

`ib_insync==0.9.86` (IBKR) and `alpaca-py==0.43.2` (Alpaca) are pure-Python
packages. They will install on Railway/Render's Linux runners. The app degrades
gracefully when no broker connection is available — `probe_dependencies()` wraps
the MT5 import in `try/except`, and broker adapters initialize in a
disconnected/disabled state.

No broker credentials are needed in the environment for a read-only demo deploy.

### 8.4 `PUT /api/risk/config` — demo caution

This route allows in-memory risk config updates at runtime. Changes reset on
service restart and are never persisted to `config.json`. For a portfolio demo,
document this route as advisory-only. If the demo backend is public-facing,
consider adding API key authentication before exposing it. This is a DEPLOY-003
action item.

---

## 9. Startup Behaviour (No API Keys)

Verified local startup log with no `CLAUDE_API_KEY`, `NEWSAPI_KEY`, or
Supabase credentials set:

```text
WARNING  app.services.audit_writer: audit_writer: no client — event not persisted (degraded)
WARNING  app.services.audit_writer: audit_writer: no client — event not persisted (degraded)
WARNING  app.services.audit_writer: audit_writer: no client — event not persisted (degraded)
INFO     app.services.startup_audit: startup_audit: 3/3 events degraded (Supabase unavailable)
INFO     trading.app.main: MellyTrade Phase 1 backend initialized
```

- 3 Supabase startup audit events degrade to warnings, never errors.
- Backend reaches `"MellyTrade Phase 1 backend initialized"` cleanly.
- Health check immediately returns `"status": "ok"`.
- `fallback_mode: true` is expected and correct when API keys are absent.

---

## 10. CORS Configuration

The `MELLYTRADE_ALLOWED_ORIGINS` environment variable controls which frontend
origins the backend will accept requests from.

Default (hardcoded in `app/core/settings.py`):

```text
http://127.0.0.1:5173,http://localhost:5173
```

**For a hosted demo deploy**, this variable must be set in the platform
dashboard to include the hosted frontend URL. Without it, browsers will block
requests from the hosted frontend to the hosted backend due to CORS policy.

Example (do not commit — set in Railway or Render dashboard only):

```text
MELLYTRADE_ALLOWED_ORIGINS=https://<your-frontend-domain>
```

Do not commit this value to the repository. Set it through the platform's
environment variable interface only.

---

## 11. Dockerfile / docker-compose Gap

Neither existing Dockerfile targets the FastAPI backend:

| File | CMD | Suitable for FastAPI demo? |
|---|---|---|
| `Dockerfile` | `python scheduler.py` | No |
| `Dockerfile.prod` | `python main.py` (old trading bot CLI) | No |
| `docker-compose.yml` | `python example_runner.py` | No |

**For Railway or Render**, do not use any existing Dockerfile. Instead, specify
the start command directly in the platform dashboard:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

If a Dockerfile is required later, a new `Dockerfile.api` targeting only the
FastAPI backend should be created. This is a DEPLOY-003 action item.

---

## 12. Required Environment Variables for a Read-only Demo

Set these in the Railway or Render dashboard only. Never commit values to
the repository.

| Variable | Required? | Purpose | Safe to omit? |
|---|---|---|---|
| `MELLYTRADE_ALLOWED_ORIGINS` | Yes | CORS — must include hosted frontend URL | No — CORS will block browser requests |
| `CLAUDE_API_KEY` | Optional | Claude AI signal validation | Yes — degrades gracefully to fallback mode |
| `NEWSAPI_KEY` | Optional | News sentiment overlay | Yes — degrades gracefully |

**Do not set** for a read-only demo:

- `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER` — no broker connection needed
- Any IBKR account credentials
- Any Alpaca API keys
- Any Supabase service-role key or admin credentials

---

## 13. What Must Not Be Deployed

- Live broker credentials of any kind
- `autotrade.enabled = true` in any config override
- `dry_run = false` in any config override
- Any `POST /orders`, `POST /execute`, or order-placement route
- Any admin or internal endpoint exposed publicly without authentication
- Any claim of live trading capability
- Any claim of guaranteed profit or financial performance
- Any investment or financial advice

---

## 14. Suggested Future Task Split

| Task | Scope |
|---|---|
| DEPLOY-003A | ✅ Add `runtime.txt` to pin Python 3.11 — resolved. `runtime.txt` committed at repo root. No deploy performed. |
| DEPLOY-003 (remaining) | Document `PUT /api/risk/config` demo caution; create `Dockerfile.api` if needed. (`GET /api/paper/run/preview` resolved by PAPER-RUN-API-001. `runtime.txt` resolved by DEPLOY-003A.) |
| DEPLOY-004 | Hosted backend smoke checklist — run after first successful Railway or Render deploy |
| PWA-DEMO-002 | Hosted PWA smoke checklist — confirm PWA works against hosted backend URL |
| DEMO-013 | Recruiter hosted demo walkthrough — full evidence pack for hosted demo |

---

## Cross-references

- [DEPLOY-001 Backend Demo Deploy Guide](backend_demo_deploy_railway_render.md)
- [Safety validation script](../../scripts/validate_safety_config.py)
- [Backend entrypoint](../../app/main.py)
- [Health route](../../app/api/routes/health.py)
- [Safety route](../../app/api/routes/safety.py)
- [Settings](../../app/core/settings.py)
- [Dependencies probe](../../app/core/dependencies.py)
- [Paper Run Preview frontend API](../../frontend/src/lib/paperRunPreviewApi.ts)
- [Paper Run Preview e2e spec](../../frontend/e2e/paper-run-preview-interaction.spec.ts)
- [Paper Run Preview schemas](../../app/schemas/paper_run_preview.py)
- [Paper Run Preview service](../../app/services/paper_run_preview_service.py)
- [Paper Run Preview route](../../app/api/routes/paper_run_preview.py)
- [Paper Run Preview tests](../../tests/app/test_paper_run_preview_endpoint.py)
