# MellyTrade Local Read-Only Demo Smoke

## 1. Purpose

- Verifies the local MellyTrade demo flow safely.
- Confirms the demo remains read-only, dry-run, and advisory-only.
- Uses GET-only checks for backend and frontend reachability.

## 2. Prerequisites

- Python 3.11
- npm installed
- backend dependencies installed
- frontend dependencies installed
- IBKR/TWS not required

## 3. Start backend

```powershell
cd C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Expected:

- backend serves `http://127.0.0.1:8001`
- safety config remains read-only / dry-run

## 4. Start frontend

```powershell
cd C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\frontend
$env:VITE_API_BASE_URL = "http://127.0.0.1:8001/api"
npm run dev
```

Expected:

- frontend serves `http://127.0.0.1:5173`
- terminal routes are reachable

## 5. Run the smoke script

From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\demo_local_readonly_smoke.ps1
```

Optional flags:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\demo_local_readonly_smoke.ps1 -NoStart
powershell -ExecutionPolicy Bypass -File .\scripts\demo_local_readonly_smoke.ps1 -SkipFrontend
powershell -ExecutionPolicy Bypass -File .\scripts\demo_local_readonly_smoke.ps1 -SkipBackend
powershell -ExecutionPolicy Bypass -File .\scripts\demo_local_readonly_smoke.ps1 -BackendUrl http://127.0.0.1:8001 -FrontendUrl http://127.0.0.1:5173
```

## 6. What the script checks

### Repo safety check

- Runs `py -3.11 scripts/validate_safety_config.py`
- Fails if the validator does not report `OVERALL: PASS`

### Backend GET checks

- `GET /api/brokers`
- `GET /api/signals/scanner/preview`
- `GET /api/signals/scanner/preview?symbols=AAPL,NVDA,EURUSD,XAUUSD`

Expected scanner preview contract:

- `read_only=true`
- `execution_mode="dry_run_only"`
- `results` array exists
- requested symbols normalize to `AAPL`, `NVDA`, `EURUSD`, `XAUUSD`
- response does not expose:
  `account_id`, `order_id`, `execution_id`, `trade_id`, `secret`,
  `token`, `api_key`, `credential`

### Frontend reachability

- `GET /`
- `GET /terminal`
- `GET /signals`
- `GET /brokers`
- `GET /portfolio`

Notes:

- The frontend is client-hydrated.
- The smoke script only checks for HTTP `200` on these routes.
- It does not assert rendered card text from raw HTML.

## 7. Expected output

The script prints only these status prefixes:

- `[PASS]`
- `[WARN]`
- `[FAIL]`

It ends with a summary for:

- backend status
- scanner preview status
- frontend status
- safety posture
- overall PASS/FAIL

The script exits non-zero on hard failures.

## 8. Safety posture

The demo must remain:

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- max risk `<= 1%`

The demo must not expose or require:

- live trading
- execution routes
- order placement
- broker execution
- connect-live UX
- autotrade controls
- credentials or secrets

## 9. Manual UI checklist

Open these routes in the browser if you want a quick visual pass:

- `http://127.0.0.1:5173/`
- `http://127.0.0.1:5173/terminal`
- `http://127.0.0.1:5173/signals`
- `http://127.0.0.1:5173/brokers`
- `http://127.0.0.1:5173/portfolio`

Confirm:

- the app loads without execution prompts
- scanner preview remains advisory-only
- no order buttons are present
- no connect-live controls are present
- no autotrade controls are present
- no credentials or account IDs are shown in the demo flow

## 10. Troubleshooting

- If the safety validator fails, stop and inspect the repo safety posture before continuing.
- If backend checks fail, confirm FastAPI is running on `127.0.0.1:8001`.
- If frontend checks fail, confirm Vite is running on `127.0.0.1:5173`.
- If the script is run with `-NoStart`, it will not try to start missing local services.
- If scanner preview checks fail, stop and inspect the GET-only contract before using the demo.
