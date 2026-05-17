# Desktop Launcher Smoke Checklist

## Purpose

Checklist for validating the Windows local MellyTrade launcher
(`scripts/desktop_launcher.py` + `scripts/build_desktop_launcher.ps1`).

---

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

No live trading. No broker execution. Advisory output only.

---

## Preconditions

- [ ] `main` is clean (`git status --short` shows no tracked changes)
- [ ] `py -3.11 scripts/validate_safety_config.py` passes
- [ ] Backend Python dependencies are installed (`.venv` or system Python with uvicorn)
- [ ] Frontend dependencies are installed (`frontend/node_modules` exists or `npm install` will run)
- [ ] No secrets are required
- [ ] No broker credentials are required
- [ ] No live trading is enabled

---

## Check-only build script

```powershell
.\scripts\build_desktop_launcher.ps1 -CheckOnly
```

**Expected:**

- [ ] `desktop_launcher.py` exists — `[PASS]`
- [ ] Python 3.11 is available — `[PASS]`
- [ ] PyInstaller availability is reported (`[PASS]` if installed, `[SKIP]` with install instruction if missing)
- [ ] No files are created or modified
- [ ] Script exits 0 (or 0 with `[SKIP]` if PyInstaller missing — acceptable)

---

## Launcher local run

```powershell
py -3.11 .\scripts\desktop_launcher.py
```

**Expected:**

- [ ] Safety banner printed:
  ```
  SAFETY: autotrade=false
  SAFETY: dry_run=true
  SAFETY: read_only=true
  SAFETY: live_orders_blocked=true
  SAFETY: max risk <=1%
  ```
- [ ] Backend helper (`start_backend_local.ps1`) starts
- [ ] Frontend helper (`start_frontend_local.ps1`) starts
- [ ] Launcher waits for backend readiness (`/api/health` or `/health` fallback)
- [ ] Launcher waits for frontend readiness
- [ ] Browser opens to `http://127.0.0.1:5173/terminal`
- [ ] Terminal UI loads — `READ ONLY / DRY RUN / LIVE ORDERS BLOCKED` visible
- [ ] No Buy / Sell / Execute buttons visible
- [ ] No Connect Live control visible

---

## Optional — no-browser run

```powershell
py -3.11 .\scripts\desktop_launcher.py --no-browser
```

**Expected:**

- [ ] Launcher starts backend and frontend as normal
- [ ] No browser window opens
- [ ] URL is printed to console for manual navigation
- [ ] Safety banner still printed

---

## Optional — skip-backend / skip-frontend

```powershell
# If backend is already running in another terminal:
py -3.11 .\scripts\desktop_launcher.py --skip-backend

# If both are already running:
py -3.11 .\scripts\desktop_launcher.py --skip-backend --skip-frontend
```

**Expected:**

- [ ] Launcher skips starting the specified helper(s)
- [ ] Readiness check still runs for whatever is running
- [ ] Safety banner still printed

---

## Stop behavior

Press **Ctrl+C** in the launcher terminal.

**Expected:**

- [ ] Launcher prints shutdown message
- [ ] Only processes started by this launcher are stopped
- [ ] No unrelated processes are killed
- [ ] Launcher exits with code 0
- [ ] Console returns cleanly

---

## Build EXE manually

Only if PyInstaller is installed:

```powershell
.\scripts\build_desktop_launcher.ps1 -Build
```

**Expected:**

- [ ] `dist/MellyTradeLauncher.exe` created locally
- [ ] Build completes without errors
- [ ] Safety reminder printed: "do NOT commit dist/, build/, *.spec"
- [ ] `dist/` is **not** committed to git
- [ ] `build/` is **not** committed to git
- [ ] `MellyTradeLauncher.spec` is **not** committed (unless explicitly reviewed)

**Post-build check:**

```powershell
git status --short
```

Expected: `dist/`, `build/`, `*.spec` should appear as untracked (`??`) or ignored (`!!`), **never staged**.

---

## Validation commands

```powershell
# Safety validator
py -3.11 scripts/validate_safety_config.py

# Static launcher tests
py -3.11 -m pytest tests/app/test_desktop_launcher_static.py -q

# Full local smoke (requires backend running)
.\scripts\smoke_local_readonly.ps1
```

---

## Red flags — stop and report if any of the following occur

- [ ] Launcher asks for broker credentials
- [ ] Launcher asks for API keys or secrets
- [ ] Launcher enables live trading (`autotrade=true`)
- [ ] Launcher disables dry-run (`dry_run=false`)
- [ ] Launcher shows order/execution controls
- [ ] Launcher modifies `config.json` or any config file
- [ ] Launcher kills processes it did not start
- [ ] Launcher calls any non-localhost URL
- [ ] Launcher calls any POST / PUT / PATCH / DELETE endpoint
- [ ] `dist/`, `build/`, or `*.spec` files appear as staged or committed

---

*MellyTrade Desktop Launcher Smoke Checklist — local-only, read-only, advisory.*
