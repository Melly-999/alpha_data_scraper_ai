# Source-Only Beta Preflight Checklist

## Purpose

Checklist to complete before granting source-only beta access to a trusted tester.

All steps must PASS before sharing repository access instructions.

---

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

No broker credentials. No live trading. No order execution. Advisory output only.

---

## Step 1 - Repo state

Run:

```powershell
git switch main
git pull --ff-only origin main
git status --short
```

Expected:

- [ ] On branch `main`
- [ ] Local HEAD matches `origin/main`
- [ ] Clean tracked tree — no staged or modified tracked files
- [ ] No generated artifacts staged

---

## Step 2 - Safety validation

Run:

```powershell
py -3.11 scripts/validate_safety_config.py
```

Expected:

- [ ] `autotrade.enabled` is false
- [ ] `autotrade.dry_run` is true
- [ ] `autotrade.min_confidence` >= 70
- [ ] No forbidden execution segments found
- [ ] OVERALL: PASS

---

## Step 3 - Desktop launcher static tests

Run:

```powershell
py -3.11 -m pytest tests/app/test_desktop_launcher_static.py tests/app/test_desktop_launcher_build_static.py tests/app/test_desktop_launcher_runtime_smoke_static.py tests/app/test_desktop_launcher_shortcut_static.py tests/app/test_desktop_distribution_docs_static.py tests/app/test_source_only_beta_docs_static.py -q
```

Expected:

- [ ] All tests PASS
- [ ] No failures

---

## Step 4 - Safety invariants and OpenAPI forbidden paths

Run:

```powershell
py -3.11 -m pytest tests/app/test_safety_invariants.py tests/app/test_openapi_forbidden_paths.py -q
```

Expected:

- [ ] All tests PASS
- [ ] No forbidden paths exposed

---

## Step 5 - Artifact validation

Run:

```powershell
git status --short dist build
git status --short *.spec
git status --short *.exe
git status --short *.lnk
git status --short *.msi
git status --short *.zip
```

Expected:

- [ ] No generated artifact staged or committed
- [ ] Empty output for each command above

---

## Step 6 - Tester communication

Confirm the following have been communicated to the tester:

- [ ] This is a local read-only demo — not live trading
- [ ] This is not broker execution
- [ ] This is not investment advice
- [ ] This is not a production release
- [ ] Do not enter broker credentials into the app
- [ ] Do not use this app for live trading decisions
- [ ] Stop and report if the safety banner is missing at launch
- [ ] Stop and report if any order or execution control appears
- [ ] Stop and report if the app requests broker credentials
- [ ] Stop and report if the app makes investment-advice claims
- [ ] Stop and report if the app claims guaranteed profit

---

## Red flags - stop rollout immediately if any of the following occur

- [ ] Safety validator fails
- [ ] Any static test fails
- [ ] Safety invariant test fails
- [ ] Secrets appear in the repository
- [ ] Broker credentials are requested by the app
- [ ] Live trading appears enabled
- [ ] Dry-run mode appears disabled
- [ ] Read-only mode appears disabled
- [ ] Order or execution controls appear in UI
- [ ] Generated artifact staged or committed
- [ ] Tester reports investment-advice copy
- [ ] Tester reports guaranteed-profit copy

---

## Approval result

Record one of the following before granting access:

- [ ] **PASS** - all steps above completed, safe to grant source-only read access
- [ ] **BLOCKED** - one or more steps failed, do not grant access until fixed

Signed off by: _______________  Date: _______________

---

*MellyTrade DESKTOP-001F - Source-Only Beta Preflight Checklist - local-only, read-only, advisory.*
