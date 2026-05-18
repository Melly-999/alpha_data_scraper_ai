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

---

## DESKTOP-001C — Launcher runtime smoke status

This step validates the locally built EXE against a runtime smoke test.

Command tested:

```powershell
.\dist\MellyTradeLauncher.exe --no-browser
```

### Status

- [x] local-only runtime smoke
- [x] no browser mode
- [x] safety banner verification — all 5 flags confirmed
- [x] backend helper startup — HTTP 200 after 1 attempt
- [x] frontend helper startup — HTTP 200 after 1 attempt
- [x] Ctrl+C shutdown state reached (launcher entered running state)
- [x] frozen repo-root bug fixed (DESKTOP-001C-BUG resolved)
- [x] no secrets
- [x] no broker execution
- [x] no live trading

### Result: PASS

DESKTOP-001C-BUG resolved: `resolve_repo_root()` in `scripts/desktop_launcher.py`
now detects `getattr(sys, "frozen", False)` and uses
`Path(sys.executable).resolve().parent.parent` when running as a frozen
PyInstaller `--onefile` EXE. Repo root resolves to the actual repo, not the
PyInstaller temp extraction directory.

Endpoint checks (GET-only): `/health` HTTP 200, `/api/health` HTTP 200,
`/terminal` HTTP 200.

### Remaining work (DESKTOP-001D onwards)

- Optional: desktop shortcut / Start Menu integration
- Optional: icon/shortcut packaging plan
- Optional: Tauri/Electron wrapper (Phase 2 — not planned for v0.2)

---

---

## DESKTOP-001D — Shortcut packaging status

This step adds a local Windows shortcut helper and tester-facing run instructions.

### This PR adds

- `scripts/create_desktop_shortcut.ps1` — PowerShell shortcut creator (WScript.Shell, no admin)
- `docs/qa/desktop_launcher_shortcut_smoke_checklist.md` — manual shortcut validation checklist
- `docs/product/beta_tester_desktop_launcher_quick_start.md` — tester-facing quick start guide
- `tests/app/test_desktop_launcher_shortcut_static.py` — static inspection tests

### Status

- [x] Local shortcut helper (`create_desktop_shortcut.ps1`)
- [x] No admin required
- [x] `-WhatIfOnly` mode — preview without creating `.lnk`
- [x] `-NoBrowser` switch — creates shortcut with `--no-browser` argument
- [x] Safety banner printed at shortcut creation time
- [x] Tester-facing quick start doc
- [x] Shortcut smoke checklist
- [x] Static tests — read-only, no EXE/shortcut execution
- [ ] No full installer yet
- [ ] No code signing yet
- [ ] No auto-update
- [x] No secrets bundled
- [x] No broker execution
- [x] No live trading
- [x] `.lnk` files are local-only and must not be committed

### Remaining work (DESKTOP-001E onwards)

- Installer / distribution plan
- Optional: icon asset design
- Optional: signed build plan
- Optional: Start Menu integration
- Optional: Tauri/Electron wrapper (Phase 2 — not planned for v0.2)

---

---

## DESKTOP-001E — Distribution Planning status

This step adds a distribution planning guide for the MellyTrade Windows desktop
launcher. Docs-only update — no runtime behavior or safety posture changed.

### This PR adds

- `docs/distribution/desktop_distribution_plan.md` — distribution options and recommended ZIP path for v0.2 beta
- `docs/qa/desktop_distribution_smoke_checklist.md` — operator smoke checklist for validating the distribution ZIP
- `docs/product/beta_tester_desktop_distribution_notes.md` — tester-facing install and launch notes
- `tests/app/test_desktop_distribution_docs_static.py` — static inspection tests (read-only, no artifact creation)

### Status

- [x] Distribution plan doc — options A/B/C/D compared, Option A (ZIP) recommended for v0.2
- [x] ZIP pack steps documented (PowerShell `Compress-Archive`)
- [x] ZIP verify steps documented
- [x] Safety constraints documented
- [x] Artifact policy documented (`dist/`, `build/`, `*.spec`, `*.exe`, `*.zip`, `*.msi` local-only)
- [x] SmartScreen workaround documented
- [x] Tester-facing install and launch notes
- [x] Operator smoke checklist
- [x] Static tests — read-only, no EXE/shortcut/ZIP execution
- [ ] No installer implemented (planning only)
- [ ] No code signing (tracked for v0.3+)
- [ ] No auto-update
- [x] No secrets bundled
- [x] No broker execution
- [x] No live trading

### Remaining work (DESKTOP-001F onwards)

- Actual ZIP packaging operational step (out-of-band, not a code change)
- Optional: icon asset design
- Optional: signed build plan (v0.3+)
- Optional: NSIS/Inno Setup installer (v0.3+)
- Optional: winget / Microsoft Store (post-launch)
- Optional: Tauri/Electron wrapper (Phase 2 — not planned for v0.2)

---

---

## DESKTOP-001F — Source-Only Beta Package Review status

This step defines the safe source-only beta access model for the first cohort
of trusted testers. Docs-only update — no runtime behavior or safety posture
changed.

### This PR adds

- `docs/distribution/source_only_beta_package_review.md` — safe sharing model, pre-share checks, stop conditions
- `docs/qa/source_only_beta_preflight_checklist.md` — operator preflight checklist before granting access
- `docs/product/beta_tester_source_access_guide.md` — tester-facing safe first run guide
- `tests/app/test_source_only_beta_docs_static.py` — static inspection tests (read-only, no artifact creation)

### Status

- [x] Source-only beta review doc
- [x] Preflight checklist
- [x] Tester source access guide
- [x] Static tests — read-only, no EXE/ZIP/network execution
- [x] No generated artifacts committed
- [x] No installer
- [x] No public EXE release artifact
- [x] No live trading
- [x] No broker execution
- [x] No secrets bundled

### Recommended

- Source-only beta for first trusted testers (preflight checklist must PASS)
- Local build beta only after preflight passes

### Deferred

- Generated ZIP bundle distribution
- Public EXE release artifact
- Installer (NSIS/Inno — tracked for v0.3+)
- Code signing (tracked for v0.3+)
- Auto-update

### Next

- DESKTOP-001G installer tool comparison
- or BETA-ACCESS-001 first source-only tester rollout

---

---

## BETA-ACCESS-001 — First Source-Only Tester Rollout status

This step prepares the first trusted tester access using source-only GitHub
repository access. Docs-only update — no runtime behavior or safety posture
changed.

### This PR adds

- `docs/beta/source_only_first_tester_rollout.md` — rollout steps and tester selection criteria
- `docs/beta/source_only_tester_invite_message.md` — ready-to-send invite message templates
- `docs/beta/source_only_tester_feedback_form.md` — structured feedback form with P0/P1/P2/P3 severity
- `docs/qa/source_only_beta_rollout_gate.md` — pre-access gate with PASS/BLOCKED approval
- `tests/app/test_source_only_beta_rollout_docs_static.py` — static inspection tests (read-only)

### Status

- [x] First tester rollout doc
- [x] Invite message templates (short, technical, follow-up)
- [x] Feedback form (P0/P1/P2/P3 severity)
- [x] Rollout gate (PASS/BLOCKED approval)
- [x] Static tests — read-only, no access granted, no messages sent
- [x] Read-only access only
- [x] No generated artifacts shared
- [x] No installer
- [x] No live trading
- [x] No broker execution
- [x] No secrets bundled

### Next steps (manual, out-of-band)

- Run rollout gate (`docs/qa/source_only_beta_rollout_gate.md`) — gate must PASS
- Grant read-only repository access manually via GitHub settings
- Send invite manually using `docs/beta/source_only_tester_invite_message.md`
- Collect feedback using `docs/beta/source_only_tester_feedback_form.md`
- Review feedback before inviting second tester

### Deferred

- Second tester rollout (blocked until first feedback reviewed)
- DESKTOP-001G installer tool comparison
- Installer (NSIS/Inno — tracked for v0.3+)
- Code signing (tracked for v0.3+)
- Auto-update

---

*MellyTrade DESKTOP-001 — Windows Local Launcher EXE Plan*

---

## QA-LOCAL-DEMO-001 — Tester smoke checklist after local-demo endpoint fix

Status:

- Tester smoke checklist added
- 404 regression checklist added
- Static docs tests added
- No runtime behavior changed
- No backend routes added in this task
- No frontend runtime changed in this task
- No generated artifacts committed
- No tester access granted
- No invite sent

Docs added:

- `docs/beta/first_source_only_tester_feedback_tracker.md`
- `docs/qa/first_source_only_tester_feedback_review_gate.md`
- `docs/qa/local_demo_tester_smoke_checklist.md`
- `docs/qa/local_demo_404_regression_checklist.md`
- `tests/app/test_local_demo_smoke_docs_static.py`
- `tests/app/test_first_source_only_tester_feedback_tracker_static.py`

Purpose:

Verify from a tester perspective that the local source-only beta launches
cleanly and no longer logs 404s for:

- `/api/backtest/summary`
- `/api/investment`
- `/api/signals/feed`

Next:

- Run checklist manually after each local-demo endpoint change.
- Collect first tester feedback using
  `docs/beta/source_only_tester_feedback_form.md`.
- Track findings in future `BETA-FEEDBACK-001`.

---

## BETA-FEEDBACK-001 — First tester feedback tracker status

Status:

- First tester feedback tracker added
- First tester feedback review gate added
- Static docs tests added
- No runtime behavior changed
- No backend routes added
- No frontend runtime changed
- No generated artifacts committed
- No tester access granted
- No invite sent
- No second tester approved

Purpose:

Track and review feedback from the first trusted source-only beta tester before
deciding whether a second tester can be invited.

Expansion rule:

Do not invite a second tester until the first tester feedback review gate
returns PASS.

Next:

- Run feedback review gate after first tester returns feedback.
- If PASS, prepare `BETA-ACCESS-002` second tester expansion gate.
- If HOLD/BLOCKED, resolve issues first.

---

## BETA-ACCESS-002 — Second tester expansion gate status

Status:

- Second tester expansion gate added
- Second tester pre-access checklist added
- Static docs tests added
- No runtime behavior changed
- No backend routes added
- No frontend runtime changed
- No generated artifacts committed
- No tester access granted
- No invite sent
- No second tester approved automatically

Purpose:

Define the manual conditions for inviting exactly one second trusted
source-only beta tester after first tester feedback review passes.

Expansion rule:

Do not invite a second tester unless
`docs/qa/first_source_only_tester_feedback_review_gate.md` returns PASS.

Next:

- Run this gate manually before granting any second tester access.
- If PASS, operator may manually grant read-only repository access to exactly
  one second tester.
- If HOLD/BLOCKED, resolve issues first.

---

## BETA-OPS-001 - Beta rollout operator command center status

Status:

- Operator command center added
- Master checklist added
- Static docs tests added
- No runtime behavior changed
- No backend routes added
- No frontend runtime changed
- No generated artifacts committed
- No tester access granted
- No invite sent
- No tester approved automatically

Purpose:

Provide one central operator entry point for the safe source-only beta rollout,
including PASS/HOLD/BLOCKED gates, P0/P1/P2/P3 severity model, and links to
all beta rollout docs.

Next:

- Use this command center before any beta tester access decision.
- Keep all expansion actions manual.
- If rollout grows beyond two testers, create `BETA-ACCESS-003` for cohort
  management.
