# Second Source-Only Tester Pre-Access Checklist

## Purpose

Manual checklist before granting read-only repository access to one second
source-only beta tester.

This checklist does not grant access or send invites automatically.

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

## Step 1 - Confirm first tester review result

Required:

- first tester feedback tracker completed
- first tester feedback review gate completed
- review gate result is PASS

BLOCKED if:

- review gate is HOLD
- review gate is BLOCKED
- feedback is missing
- safety result is unclear

## Step 2 - Confirm no blockers

Required:

- no unresolved P0
- no unresolved launch-blocking P1
- no safety banner issue
- no order/execution controls reported
- no broker credential prompt reported
- no live trading language reported
- no investment advice claim
- no guaranteed profit claim

## Step 3 - Confirm local validation

Run:

```bash
py -3.11 scripts/validate_safety_config.py
py -3.11 -m pytest tests/app/test_local_demo_readonly_endpoints.py -q
py -3.11 -m pytest tests/app/test_local_demo_smoke_docs_static.py -q
py -3.11 -m pytest tests/app/test_safety_invariants.py tests/app/test_openapi_forbidden_paths.py -q
```

Expected:

- all pass

## Step 4 - Confirm artifacts are not staged

Run:

```bash
git status --short dist build
git status --short *.spec
git status --short *.exe
git status --short *.lnk
git status --short *.msi
git status --short *.zip
```

Expected:

- no generated artifacts staged

## Step 5 - Review second tester invite

Before sending:

- customize tester name
- state source-only beta
- state read-only local demo
- state not live trading
- state not broker execution
- state not investment advice
- state no broker credentials required
- state stop/report conditions

## Approval result

Choose one:

- PASS - safe to manually grant read-only repo access to exactly one second tester.
- HOLD - wait for more info or fixes.
- BLOCKED - do not invite second tester.

## Red flags

Stop if:

- any P0 remains open
- any launch-blocking P1 remains open
- operator cannot verify first tester feedback
- generated artifact is staged
- invite suggests live trading
- invite asks for broker credentials
- invite implies investment advice
- invite claims guaranteed profit
- app safety posture is unclear

