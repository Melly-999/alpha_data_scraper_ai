# Desktop Launcher Runtime Smoke

## Purpose

Validate local runtime behavior of `MellyTradeLauncher.exe`.

## Command tested

```powershell
.\dist\MellyTradeLauncher.exe --no-browser
```

---

## Safety posture observed

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

---

## Result

**PASS**

DESKTOP-001C-BUG (PyInstaller frozen repo-root detection) fixed.
Safety banner appeared with all required flags. Repo root resolved correctly.
Backend and frontend helpers started successfully. No unsafe behaviour observed.

---

## Fix applied (DESKTOP-001C-BUG)

`scripts/desktop_launcher.py` — `resolve_repo_root()` now detects
`getattr(sys, "frozen", False)` and uses `Path(sys.executable).resolve().parent.parent`
when running as a frozen PyInstaller `--onefile` EXE:

- `sys.executable` → `dist/MellyTradeLauncher.exe`
- `.parent` → `dist/`
- `.parent.parent` → repo root

Previously `__file__` resolved to the PyInstaller temp extraction directory
(`AppData\Local\Temp\...`), causing the backend helper script lookup to fail.

---

## Observations

### Safety banner

- [x] Safety banner appeared at launch
- [x] `autotrade=false` visible
- [x] `dry_run=true` visible
- [x] `read_only=true` visible
- [x] `live_orders_blocked=true` visible
- [x] `max risk <=1%` visible
- [x] `No broker execution. No live orders.` visible
- [x] `Advisory output only. Human review required.` visible

### Repo root

- [x] Resolved correctly to:
  `C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai`
- [x] NOT resolving to temp extraction directory

### Backend helper

- [x] Backend helper started (PID confirmed in output)
- [x] Backend `/api/health` responded HTTP 200 after 1 attempt
- [x] No broker credentials requested
- [x] No live trading enabled
- [x] No order/execution controls added

### Frontend helper

- [x] Frontend helper started (PID confirmed in output)
- [x] Frontend HTTP 200 after 1 attempt
- [x] Frontend safety banner present:
  `no execution buttons  no order routes`

### Browser

- [x] Browser did not open (`--no-browser` respected)
- [x] Launcher printed: `open manually at http://127.0.0.1:5173/terminal`

### Ctrl+C shutdown

- [x] Launcher entered running state: `Press Ctrl+C to stop.`
- [x] Clean process management confirmed (backend PID, frontend PID tracked)
- [x] Only processes started by the launcher are under its management

### Endpoint checks (GET-only)

- [x] `GET /health` → HTTP 200, `status:ok`, `fallback_mode:true`,
      `max_risk_per_trade:1.0`
- [x] `GET /api/health` → HTTP 200, same safe payload
- [x] `GET /terminal` → HTTP 200 (Vite SPA shell, 900 bytes)
- [x] No mutation calls made

### Secrets / credentials

- [x] No broker credentials requested
- [x] No API keys requested
- [x] No passwords requested
- [x] No secrets exposed

### Mutation controls

- [x] No POST/PUT/PATCH/DELETE shown
- [x] No order buttons
- [x] No execution controls

---

## Local artifacts

Generated artifacts are local-only and must not be committed:

```text
dist/
build/
*.spec
*.exe
```

These are covered by `.gitignore` and must remain local-only.

---

## Exit code

`0` — launcher exited cleanly after full startup (backend + frontend ready).

---

## Follow-up

**PASS — DESKTOP-001C-BUG resolved.**

- DESKTOP-001D can plan icon/shortcut packaging or user-facing run instructions.

---

*MellyTrade DESKTOP-001C — Launcher Runtime Smoke — local-only, read-only, advisory.*
