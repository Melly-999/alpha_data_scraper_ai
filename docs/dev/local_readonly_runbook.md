# Local Read-Only Runbook — MellyTrade Research Terminal

Local development guide for running MellyTrade as a **read-only research
terminal**. No live trading, no broker execution, no order buttons.

---

## Safety invariants

These are enforced in code and must never be changed for local dev:

| Flag | Value | Where enforced |
|------|-------|----------------|
| `autotrade` | `false` | `config.json`, `_sanitize_config()` |
| `dry_run` | `true` | `config.json`, `_sanitize_config()` |
| `read_only` | `true` | `AuditEventRecord` model_validator |
| `live_orders_blocked` | `true` | broker adapter defaults |
| `max_risk_per_trade` | `≤ 1%` | `_sanitize_config()` clamps to 1.0 |
| `auto_trade` | `false` | `_sanitize_config()` hard-codes |

`PUT /api/risk/config` cannot override `dry_run` or `auto_trade` —
`_sanitize_config()` silently resets both to safe values on every write.

---

## Port situation

Vite's `frontend/vite.config.ts` proxies `/melly-api` → `http://localhost:8000`.
If port 8000 is occupied by an unrelated process (check with
`netstat -ano | grep ":8000"`), start the backend on **8001** instead
(the scripts below do this by default) and use `VITE_MELLY_API_BASE_URL` to
bypass the stale proxy. See the Frontend section below.

---

## Starting the backend

**Script (recommended):**

```powershell
# Terminal 1
.\scripts\start_backend_local.ps1
# Uses port 8001 by default; uses .venv Python if present, py -3.11 otherwise.
# Binds to 127.0.0.1 only — never 0.0.0.0.
```

**Manual command:**

```powershell
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --log-level info
```

The backend is ready when you see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

---

## Starting the frontend

**Script (recommended):**

```powershell
# Terminal 2 (separate from backend)
.\scripts\start_frontend_local.ps1
# Sets VITE_MELLY_API_BASE_URL=http://127.0.0.1:8001 automatically.
# Bypasses the vite.config.ts proxy to port 8000.
```

**Manual commands (PowerShell):**

```powershell
cd frontend
$env:VITE_MELLY_API_BASE_URL = "http://127.0.0.1:8001"
$env:VITE_API_BASE_URL       = "http://127.0.0.1:8001/api"
npm run dev -- --host 127.0.0.1
```

The frontend is ready when Vite prints:
```
  ➜  Local:   http://127.0.0.1:5173/
```

---

## URLs

| Resource | URL |
|----------|-----|
| Backend health | http://127.0.0.1:8001/health |
| Backend API health | http://127.0.0.1:8001/api/health |
| OpenAPI docs | http://127.0.0.1:8001/docs |
| Frontend | http://127.0.0.1:5173 |
| Terminal view | http://127.0.0.1:5173/terminal |
| Signal decisions | http://127.0.0.1:5173/signals |

---

## Smoke tests

Use only GET endpoints. All checks below are read-only.

**Script (recommended):**

```powershell
.\scripts\smoke_local_readonly.ps1
# Defaults to http://127.0.0.1:8001 — backend must be running first.
# Prints PASS/FAIL per check.
```

**Manual curl commands:**

```bash
BASE=http://127.0.0.1:8001

# Core health
curl -s $BASE/health | python -m json.tool
curl -s $BASE/api/health | python -m json.tool

# Signal scanner (advisory only — no execution)
curl -s "$BASE/api/signals/scanner/preview" | python -m json.tool

# Decision history
curl -s "$BASE/api/signals/decisions" | python -m json.tool

# Lifecycle view
curl -s "$BASE/api/signals/lifecycle" | python -m json.tool

# Risk config (read-only GET)
curl -s "$BASE/api/risk/config" | python -m json.tool

# Broker list (GET only)
curl -s "$BASE/api/brokers" | python -m json.tool
```

**Expected safety fields:**

| Endpoint | Required fields |
|----------|----------------|
| `/health` | `auto_trade=false`, `dry_run=true` |
| `/api/signals/scanner/preview` | `risk_allowed=false`, `execution_mode=dry_run_only`, `requires_human_review=true` |
| `/api/signals/decisions` | `dry_run=true`, `auto_trade=false`, `read_only=true` |
| `/api/signals/lifecycle` | `dry_run=true`, `auto_trade=false`, `supports_live_orders=false` |

---

## Expected degraded states (normal for local dev)

| Dependency | Expected state | Safe? |
|------------|---------------|-------|
| Supabase | `degraded=true`, `persisted=false` in audit logs | Yes — graceful fallback |
| MT5 | `mt5: false` in `/health` | Yes — synthetic data used |
| Claude AI | `claude: false` in `/health` | Yes — local signal only |
| NewsAPI | `news: false` in `/health` | Yes — neutral sentiment |
| IBKR | adapter shows `connected=false` or disabled | Yes — no broker needed |

`fallback_mode: true` in `/health` is the normal and expected state for
local dev. All signals are advisory only.

---

## Troubleshooting

### Port 8000 blocked

```bash
netstat -ano | grep ":8000 " | grep "LISTEN"
# Note the PID shown.
taskkill //F //PID <pid>   # Only if it's a stale Python/uvicorn process.
```

If the process cannot be killed, use port 8001 (scripts default) and restart
the frontend with `VITE_MELLY_API_BASE_URL` set as shown above.

### Port 5173 occupied

```powershell
.\scripts\start_frontend_local.ps1 -FrontendPort 5174
```

### Frontend shows API errors / "Failed to fetch"

The Vite dev proxy in `vite.config.ts` targets port 8000 by default. If the
backend is on 8001, the proxy will fail unless `VITE_MELLY_API_BASE_URL` is
set. The `start_frontend_local.ps1` script sets this automatically.

Manual fix:

```powershell
$env:VITE_MELLY_API_BASE_URL = "http://127.0.0.1:8001"
cd frontend && npm run dev -- --host 127.0.0.1
```

### Stopping backend / frontend

Press `Ctrl+C` in the respective terminal. Both uvicorn and the Vite dev
server handle SIGINT cleanly.

---

## What this runbook does NOT cover

- IBKR paper trading: see `docs/LOCAL_RUNBOOK_IBKR_PAPER.md`
- Docker / production deployment: see `DEPLOYMENT_GUIDE.md`
- Supabase schema: see `docs/supabase/`
- Live trading: **not supported and not documented here**
