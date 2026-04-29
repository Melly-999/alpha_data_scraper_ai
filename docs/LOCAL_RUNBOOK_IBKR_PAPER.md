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
