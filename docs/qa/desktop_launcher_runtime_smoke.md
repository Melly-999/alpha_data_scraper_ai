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

**PARTIAL PASS**

Safety banner appeared correctly with all required safety flags.
Launcher exited with code 1 due to a PyInstaller `--onefile` repo-root detection
issue (see Observations below). Backend and frontend helpers did not start.
No unsafe behaviour observed.

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

### Backend helper

- [ ] Backend helper started — NOT reached
- [x] No broker credentials requested
- [x] No live trading enabled
- [x] No order/execution controls added

**Root cause:** PyInstaller `--onefile` extracts the EXE to a temporary directory
(`sys._MEIPASS`, e.g. `C:\Users\...\AppData\Local\Temp`). The launcher computes
its repo root from `__file__`, which resolves to the temp extraction path instead
of the actual repository root.

Exact error observed:

```text
[INFO] Repo root: C:\Users\highe\AppData\Local\Temp
[ERROR] Backend helper script not found at:
        C:\Users\highe\AppData\Local\Temp\scripts\start_backend_local.ps1
Check that the repo root is correct and the file exists.
```

**Required fix (DESKTOP-001C-BUG):** Detect `getattr(sys, 'frozen', False)` in
`scripts/desktop_launcher.py` and compute repo root from
`Path(sys.executable).parent.parent` when running as a frozen PyInstaller EXE,
rather than from `__file__`. Not patched in this run — tracked as a follow-up.

### Frontend helper

- [ ] Frontend helper started — NOT reached (backend failed first)

### Browser

- [x] Browser did not open (`--no-browser` respected; EXE exited before browser step)

### Ctrl+C shutdown

- [x] Not applicable — EXE exited with code 1 before reaching process management

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

`1` — launcher exited with error due to repo-root detection bug.

---

## Follow-up

**PARTIAL PASS — blocked by DESKTOP-001C-BUG: PyInstaller frozen repo-root detection.**

Fix required in `scripts/desktop_launcher.py` before marking runtime smoke PASS:

```python
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # Running as PyInstaller --onefile EXE
    # sys.executable = dist/MellyTradeLauncher.exe
    # .parent = dist/
    # .parent.parent = repo root
    _REPO_ROOT = Path(sys.executable).parent.parent
else:
    _REPO_ROOT = Path(__file__).resolve().parent.parent
```

After fix:

- Re-run `.\scripts\build_desktop_launcher.ps1 -Build`
- Re-run `.\dist\MellyTradeLauncher.exe --no-browser`
- Confirm safety banner + backend helper startup + Ctrl+C clean shutdown

If PASS after fix:

- DESKTOP-001D can plan icon/shortcut packaging or user-facing run instructions.

If still failing:

- Open a bugfix task with exact logs before continuing packaging.

---

*MellyTrade DESKTOP-001C — Launcher Runtime Smoke — local-only, read-only, advisory.*
