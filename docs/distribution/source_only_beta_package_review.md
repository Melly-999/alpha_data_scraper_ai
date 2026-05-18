# Source-Only Beta Package Review

> Planning document only. Does not implement any installer, package, or
> distribution artifact. Does not change runtime behaviour or safety posture.

---

## Purpose

Define the safe source-only beta sharing model for MellyTrade desktop launcher
testers.

This document describes what trusted beta testers can receive, what they must
not receive, the required pre-share validation steps, and the stop conditions
that must halt a rollout.

---

## Current recommendation

Use source-only beta or local-build beta for the first cohort of trusted testers.

**Do not** publish generated EXE artifacts yet.
**Do not** ship an installer yet.
**Do not** upload ZIP/MSI/release artifacts yet.

The reason: the launcher is locally validated (DESKTOP-001A through
DESKTOP-001E) but has not been through a code-signing or release pipeline.
Sharing source access to a small trusted cohort is safer than distributing an
unsigned EXE to a wider audience.

---

## What can be shared

### Allowed

- GitHub repository read access (trusted testers only)
- Setup instructions
- Beta tester quick start docs
- Local build instructions (PyInstaller, local-only)
- Launcher smoke checklist
- Shortcut helper instructions
- Distribution smoke checklist
- This review document

### Not allowed

- `.env` files or secrets
- Broker credentials
- MT5 account IDs or login details
- Supabase service role keys or API keys
- Generated EXE files committed to git
- Generated ZIP bundles committed to git
- Generated MSI/installer artifacts committed to git
- Any file that enables live trading
- Any file that exposes order buttons or broker execution controls
- Investment advice claims
- Guaranteed profit claims

---

## Required pre-share checks

Before adding a tester or sharing repository access instructions:

### 1. Safety validator

```powershell
py -3.11 scripts/validate_safety_config.py
```

Expected: PASS — all checks green.

### 2. Static test suites

```powershell
py -3.11 -m pytest tests/app/test_desktop_launcher_static.py tests/app/test_desktop_launcher_build_static.py tests/app/test_desktop_launcher_runtime_smoke_static.py tests/app/test_desktop_launcher_shortcut_static.py tests/app/test_desktop_distribution_docs_static.py tests/app/test_source_only_beta_docs_static.py -q
```

Expected: all tests PASS.

### 3. Safety invariants

```powershell
py -3.11 -m pytest tests/app/test_safety_invariants.py tests/app/test_openapi_forbidden_paths.py -q
```

Expected: all tests PASS.

### 4. Artifact check

Confirm the following are not staged or committed:

```powershell
git status --short dist build
git status --short *.spec
git status --short *.exe
git status --short *.lnk
git status --short *.msi
git status --short *.zip
```

Expected: empty output for each command (nothing staged).

---

## Tester access checklist

Before granting a tester read-only repository access:

- [ ] Add trusted tester with read-only repository access (not write access)
- [ ] Share `docs/product/beta_tester_desktop_launcher_quick_start.md`
- [ ] Share `docs/product/beta_tester_source_access_guide.md`
- [ ] Share `docs/product/beta_tester_desktop_distribution_notes.md`
- [ ] Tell tester this is a local read-only demo — not live trading
- [ ] Tell tester not to enter broker credentials into the app
- [ ] Tell tester not to use the app for live trading decisions
- [ ] Tell tester to stop and report if the safety banner is missing
- [ ] Tell tester to stop and report if any order/execution control appears
- [ ] Tell tester to stop and report if the app makes investment-advice claims
- [ ] Tell tester to stop and report if the app claims guaranteed profit

---

## Safety posture

All sessions must run with:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

No distribution artifact may expose controls that change these values.

---

## Stop conditions

Stop the source-only beta rollout immediately if any of the following occur:

- Safety validator fails
- Static tests fail
- Safety invariant tests fail
- Secrets appear in the repository (API keys, broker credentials, `.env` files)
- Broker credentials are requested by the app at startup
- Live trading appears enabled (`autotrade=true` in config)
- Dry-run mode is disabled (`dry_run=false` in config)
- Read-only mode is disabled (`read_only=false` in config)
- Order or execution controls appear in the UI
- Generated EXE, ZIP, or MSI artifacts are staged or committed
- A tester reports investment-advice-like copy in the UI
- A tester reports guaranteed-profit-like copy in the UI
- A tester reports that broker credentials were requested by the app

---

## Artifact policy

The following are local-only and must NOT be committed to the repository:

```text
dist/
build/
*.spec
*.exe
*.lnk
*.msi
*.zip
```

Verify before sharing:

```powershell
git status --short dist build
git status --short *.spec *.exe *.lnk *.msi *.zip
```

---

## Related docs

- `docs/tasks/desktop_launcher_exe_plan.md` - full DESKTOP-001 plan and status
- `docs/distribution/desktop_distribution_plan.md` - distribution options overview
- `docs/qa/source_only_beta_preflight_checklist.md` - operator preflight checklist
- `docs/product/beta_tester_source_access_guide.md` - tester-facing access guide
- `docs/product/beta_tester_desktop_launcher_quick_start.md` - launcher quick start
- `docs/qa/desktop_distribution_smoke_checklist.md` - distribution smoke checklist
- `docs/qa/desktop_launcher_shortcut_smoke_checklist.md` - shortcut smoke checklist

---

*MellyTrade DESKTOP-001F - Source-Only Beta Package Review - planning only.*
