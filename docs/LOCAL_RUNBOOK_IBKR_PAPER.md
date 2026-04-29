# Local Runbook: IBKR Paper Adapter

This workstation can run the merged IBKR Paper Adapter v1 in a safe
paper/dry-run mode.

## Safe status

- IBKR Paper Adapter v1 is available through the FastAPI backend.
- Live orders remain blocked by the adapter.
- The default runtime posture remains dry-run only.
- Do not use real money until manual approval mode and paper soak tests
  are implemented and reviewed.

## Start backend

From the repository root:

```powershell
.\scripts\start_backend_ibkr_paper.ps1
```

The script sets:

```powershell
$env:BROKER_ADAPTER = "ibkr-paper"
$env:IBKR_ENABLED = "true"
```

It does not set live-trading flags.

If needed, pass a specific Python:

```powershell
.\scripts\start_backend_ibkr_paper.ps1 -PythonPath "C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\.venv\Scripts\python.exe"
```

## Run smoke checks

In a second terminal:

```powershell
.\scripts\smoke_ibkr_paper.ps1
```

Expected safe results:

- `/health` returns `200`.
- `/api/health` returns `200`.
- `/api/broker/health` returns `adapter=ibkr_paper`.
- `supports_live_orders=false` is required.
- `/api/broker/account` returns a safe snapshot.
- `/api/broker/dry-run-report` returns `dry_run=true`.

## Start frontend

```powershell
.\scripts\start_frontend.ps1
```

The script runs `npm install` only when `frontend\node_modules` is
missing, then starts the Vite dev server.

## Local environment check

```powershell
.\scripts\check_local_env.ps1
```

This prints the current branch, Python availability, local `.venv`
health, fallback venv availability, IBKR files, and whether `.env`
exists. It never prints secret contents.

## Known local venv issue

The local `.venv` may be broken or incomplete. Rebuilding dependencies
can fail on `greenlet` with a Microsoft C++ Build Tools requirement.

For today, the known working fallback venv is:

```text
C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\.venv
```

Permanent fixes:

- Rebuild with Python 3.11 or 3.12 and current binary wheels.
- Install Microsoft C++ Build Tools if a source build is unavoidable.
- Prefer binary wheels for native dependencies when possible.

## TWS Paper checklist

- Log in to IBKR PaperTrader.
- Enable API socket clients.
- Use paper TWS port `7497`.
- Add trusted IP `127.0.0.1`.
- Keep Read-Only API ON initially.

## Safe disconnected behavior

Without TWS or `ib_insync`, the adapter may report disconnected,
`missing_dependency`, or not connected. That is acceptable for local
smoke testing.

The required safety invariant is:

```text
supports_live_orders=false
```

## Using MellyTrade without TWS Paper

You can keep using MellyTrade locally even when you cannot configure
TWS Paper API yet. Nothing in this mode places an order, contacts a
real broker, or risks money.

What works without TWS Paper:

- The FastAPI backend starts normally with
  `scripts/start_backend_ibkr_paper.ps1`.
- The dashboard at `http://127.0.0.1:5173/dashboard` renders fully.
- The Broker Card displays a typed disconnected status (one of
  `missing_dependency`, `connect_failed`, `disabled`, or `live_blocked`)
  together with a passive TWS Paper setup checklist so you know what is
  needed when you choose to wire it up later.
- All other passive pages (Signals, Positions, Risk, Logs, MT5 Bridge,
  Trade Blotter, Settings) keep working against the demo data path.

What does not work without TWS Paper:

- `/api/broker/account` reports `connected=false` and zeroed balances -
  by design.
- `/api/broker/health` reports a non-`connected` status - by design.
- `scripts/smoke_ibkr_paper.ps1` will exit early with a friendly hint
  if the backend itself is not running, and will otherwise pass as long
  as the typed disconnected snapshot is safe.

Safety invariants that always hold in disconnected mode:

- `supports_live_orders=false`.
- `Live orders: BLOCKED` chip is visible on the dashboard.
- No order, reconnect, or execution buttons exist anywhere in the UI.
- `autotrade.enabled=false` and `dry_run=true` in `config.json`.
- MT5 execution behaviour is untouched.

When you are ready to wire TWS Paper, follow the `TWS Paper checklist`
above and the validation flow below. Until then, you can keep
developing safely.

## TWS Paper validation flow

After the backend is up (`start_backend_ibkr_paper.ps1`) walk through the
states below. Each one keeps the system read-only and dry-run; none of
them places an order.

| State | How to reproduce | Health response (key fields) |
| --- | --- | --- |
| Without TWS | Start backend, leave TWS closed | `connected=false`, `status` in `{connect_failed, missing_dependency}`, `supports_live_orders=false` |
| TWS Paper running | Login to PaperTrader, enable ActiveX/Socket Clients, port `7497`, trusted IP `127.0.0.1`, restart TWS | `connected=true`, `mode=paper`, `port=7497`, `supports_live_orders=false` |
| Live port misconfigured | `$env:IBKR_PORT="7496"` (the start script will refuse) | start script aborts before contacting TWS |
| Live port via raw env | Set live port and start uvicorn manually | `connected=false`, `status=live_blocked`, `last_error` starts with `live_port_blocked` |

After each state, fetch:

```powershell
Invoke-WebRequest http://127.0.0.1:8001/api/broker/health  | ConvertFrom-Json | ConvertTo-Json -Depth 6
Invoke-WebRequest http://127.0.0.1:8001/api/broker/account | ConvertFrom-Json | ConvertTo-Json -Depth 6
```

Open the dashboard at `http://127.0.0.1:5173/dashboard` and confirm:

* `Live orders: BLOCKED` chip is visible.
* `supports_live_orders=false` chip is visible.
* The Broker card matches the adapter health (mode/port/account).
* No order, reconnect, or execution buttons are present anywhere on the
  page. The dashboard remains read-only.

If any of these invariants is violated, stop and report - do not bypass
the gate, do not enable live orders, do not modify the risk settings.
