# Source-Only Beta Rollout Gate

> Gate to complete before granting source-only GitHub repository access to
> the first trusted tester. All steps must PASS.

---

## Purpose

This gate confirms the repository, docs, tests, and safety posture are ready
before any tester receives read-only GitHub access.

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

## Step 1 - Align local main

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

## Step 3 - Source-only beta rollout docs tests

Run:

```powershell
py -3.11 -m pytest tests/app/test_source_only_beta_rollout_docs_static.py tests/app/test_source_only_beta_docs_static.py -q
```

Expected:

- [ ] All tests PASS
- [ ] No failures

---

## Step 4 - Desktop launcher static tests

Run:

```powershell
py -3.11 -m pytest tests/app/test_desktop_launcher_static.py tests/app/test_desktop_launcher_build_static.py tests/app/test_desktop_launcher_runtime_smoke_static.py tests/app/test_desktop_launcher_shortcut_static.py tests/app/test_desktop_distribution_docs_static.py -q
```

Expected:

- [ ] All tests PASS
- [ ] No failures

---

## Step 5 - Safety invariants and OpenAPI forbidden paths

Run:

```powershell
py -3.11 -m pytest tests/app/test_safety_invariants.py tests/app/test_openapi_forbidden_paths.py -q
```

Expected:

- [ ] All tests PASS
- [ ] No forbidden paths exposed

---

## Step 6 - Artifact validation

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

## Step 7 - Tester invite reviewed

Confirm before proceeding:

- [ ] Tester invite message reviewed (`docs/beta/source_only_tester_invite_message.md`)
- [ ] Tester feedback form ready (`docs/beta/source_only_tester_feedback_form.md`)
- [ ] Tester source access guide confirmed present (`docs/product/beta_tester_source_access_guide.md`)
- [ ] Tester desktop launcher quick start confirmed present (`docs/product/beta_tester_desktop_launcher_quick_start.md`)
- [ ] No secrets, broker credentials, or account IDs in any doc to be shared
- [ ] No generated EXE, ZIP, or MSI to be sent — source-only access only

---

## Approval result

Record one of the following before granting access:

- [ ] **PASS** — all steps above completed, safe to grant source-only read access to 1 trusted tester
- [ ] **BLOCKED** — one or more steps failed, do not grant access until fixed

Signed off by: _______________  Date: _______________

---

## Expansion rule

Do not invite a second tester until:

- [ ] First tester feedback reviewed
- [ ] All P0 issues resolved or explicitly accepted with documented rationale
- [ ] All P1 issues resolved or deferred with documented plan
- [ ] Safety validator still PASS
- [ ] All static tests still PASS
- [ ] No new execution-like controls introduced

---

## Red flags — stop rollout immediately if any of the following occur

- [ ] Safety validator fails
- [ ] Any static test fails
- [ ] Safety invariant test fails
- [ ] Secrets appear in the repository
- [ ] Broker credentials are requested by the application
- [ ] Live trading appears enabled
- [ ] Dry-run mode appears disabled
- [ ] Read-only mode appears disabled
- [ ] Order or execution controls appear in the UI
- [ ] Generated artifact staged or committed
- [ ] Tester reports investment advice copy in the UI
- [ ] Tester reports guaranteed-profit copy in the UI
- [ ] Tester reports the application connected outside `localhost`

---

## Related docs

- `docs/distribution/source_only_beta_package_review.md` - safe sharing model
- `docs/qa/source_only_beta_preflight_checklist.md` - detailed preflight checklist
- `docs/beta/source_only_first_tester_rollout.md` - rollout steps
- `docs/beta/source_only_tester_invite_message.md` - invite templates
- `docs/beta/source_only_tester_feedback_form.md` - feedback form
- `docs/product/beta_tester_source_access_guide.md` - tester-facing guide
- `docs/tasks/desktop_launcher_exe_plan.md` - DESKTOP-001 plan and BETA-ACCESS-001 status

---

*MellyTrade BETA-ACCESS-001 - Source-Only Beta Rollout Gate - local-only, read-only, advisory.*
