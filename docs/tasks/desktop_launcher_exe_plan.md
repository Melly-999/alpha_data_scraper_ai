# DESKTOP-001 — Windows Local Launcher EXE Plan

> Planning document only. Does not implement any executable, change runtime
> behaviour, or alter safety posture.

---

## Goal

Create a Windows `.exe` launcher for local MellyTrade demo usage that:

- starts the FastAPI backend locally
- starts the Vite frontend locally
- opens a browser to `/terminal`
- shows local process status
- keeps safety posture visible
- stops only processes it started

---

## Context

MellyTrade Closed Beta Demo v0.1 requires the operator to start backend and
frontend manually in two terminal windows. A launcher removes this friction for
local demo sessions without adding any hosted, networked, or live-trading path.

---

## Required safety posture (enforced by launcher)

```text
autotrade      = false
dry_run        = true
read_only      = true
live_orders_blocked = true
max risk       <= 1%
```

The launcher must start the application with these defaults active. It must not
expose controls that change these values at launch time.

---

## Recommended implementation

### Phase 1 — Python launcher script

A single `launcher.py` script that:

1. Validates Python version and dependencies
2. Starts FastAPI backend (`uvicorn app.main:app --reload --port 8000`)
3. Starts Vite frontend (`npm run dev --prefix frontend`)
4. Waits for backend health check (`GET /health`) to pass
5. Opens default browser to `http://localhost:5173/terminal`
6. Shows PID and status for each child process
7. Traps `Ctrl+C` / `SIGINT` and cleanly terminates both child processes
8. Exits with non-zero code if either child process fails

**Package with PyInstaller:**

```bash
pyinstaller --onefile --name MellyTrade_Launcher launcher.py
```

Output: `dist/MellyTrade_Launcher.exe`

### Phase 2 — Optional app window wrapper

- Tauri or Electron wrapper for a proper app window with a local health panel
- Requires separate UX/implementation review before adoption
- Not a target for v0.2

---

## Safety constraints

The launcher must NOT:

- bundle `.env` files or secrets
- bundle broker credentials
- enable autotrade
- disable dry-run
- connect to live broker execution
- add order buttons
- expose account IDs
- write config files that change safety values
- start any network service beyond `localhost`

---

## Acceptance criteria

- [ ] starts FastAPI backend on `localhost:8000`
- [ ] starts Vite frontend on `localhost:5173`
- [ ] opens `http://localhost:5173/terminal` in the default browser
- [ ] safety validator passes after startup (`py -3.11 scripts/validate_safety_config.py`)
- [ ] smoke script passes after startup
- [ ] `Ctrl+C` cleanly terminates both child processes
- [ ] no secrets bundled in the executable
- [ ] no mutation/execution controls introduced

---

## What this PR does NOT do

This document is a plan only. The launcher script and EXE are not implemented
in this PR. Implementation is tracked as DESKTOP-001 in
`docs/tasks/v0_2_implementation_queue.md`.

---

## Related docs

- `docs/tasks/v0_2_implementation_queue.md` — task queue
- `docs/demo/final_local_demo_smoke_report.md` — local smoke checklist
- `docs/beta/beta_tester_quick_start.md` — current manual start instructions
- `docs/release/closed_beta_demo_v0_1_next_steps.md` — v0.1 next steps

---

---

## DESKTOP-001A — Implementation status

This section records what was added in the initial launcher foundation PR
(`feature/desktop-local-launcher-v1`). Docs-only update — no runtime behavior
or safety posture changed.

### This PR adds

- `scripts/desktop_launcher.py` — Python local launcher (stdlib only, Windows-first)
- `scripts/build_desktop_launcher.ps1` — PyInstaller check/build wrapper
- `docs/qa/desktop_launcher_smoke_checklist.md` — manual smoke validation checklist

### Status

- [x] Launcher foundation implemented
- [x] Local-only — loopback only, no external network calls
- [x] Browser-based UI — opens `/terminal` in default browser
- [x] PyInstaller build path prepared (`-CheckOnly` / `-Build` modes)
- [x] Safety posture banner printed at launch
- [x] Ctrl+C clean shutdown — stops only processes it started
- [ ] Full installer — not yet (Phase 2)
- [x] No secrets bundled
- [x] No broker execution
- [x] No live trading

### Remaining work (DESKTOP-001B onwards)

- PyInstaller build validation and EXE smoke test
- `.gitignore` audit for `dist/`, `build/`, `*.spec`
- Optional: desktop shortcut / Start Menu integration
- Optional: Tauri/Electron wrapper (Phase 2 — not planned for v0.2)

---

---

## DESKTOP-001B — PyInstaller build validation status

This step validates the PyInstaller build path locally.

It may generate:

- `dist/MellyTradeLauncher.exe`
- `build/`
- `MellyTradeLauncher.spec`

These artifacts are local-only and must not be committed.

### Status

- [x] PyInstaller build validation
- [x] local-only
- [ ] no installer yet
- [ ] no code signing yet
- [ ] no auto-update
- [x] no secrets bundled
- [x] no broker execution
- [x] no live trading

### Remaining work (DESKTOP-001C onwards)

- Launcher runtime smoke test (`.\dist\MellyTradeLauncher.exe --no-browser`)
- Optional: desktop shortcut / Start Menu integration
- Optional: Tauri/Electron wrapper (Phase 2 — not planned for v0.2)

---

*MellyTrade DESKTOP-001 — Windows Local Launcher EXE Plan*
