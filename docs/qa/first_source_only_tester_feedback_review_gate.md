# First Source-Only Tester Feedback Review Gate

## Purpose

Review the first tester feedback before deciding whether the source-only beta
can expand to a second tester.

This gate is manual and docs-only.

It does not:
- grant access
- send invites
- enable live trading
- connect brokers
- execute orders
- create release artifacts

## Required inputs

- completed `docs/beta/first_source_only_tester_feedback_tracker.md`
- tester screenshots/logs, if provided
- source-only tester feedback form
- local demo smoke checklist result
- local demo 404 regression checklist result

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

## Review steps

### Step 1 - Confirm feedback was received

PASS if:

- tester completed setup section
- tester reported launch result
- tester reported safety banner result
- tester reported endpoint result

BLOCKED if:

- no feedback received
- safety section missing
- tester did not run the app

### Step 2 - Check safety blockers

BLOCKED if tester reports:

- live trading enabled
- order/execution controls
- broker credential prompt
- missing safety banner
- `dry_run=false`
- `read_only=false`
- account ID exposed
- investment advice claim
- guaranteed profit claim

### Step 3 - Check launch blockers

BLOCKED or HOLD if:

- app does not start
- backend crashes
- frontend does not load
- `/terminal` cannot be opened
- required endpoint returns 404 or 500

### Step 4 - Review P0/P1 issues

PASS only if:

- zero unresolved `P0`
- zero unresolved launch-blocking `P1`

HOLD if:

- `P1` exists but workaround is acceptable

BLOCKED if:

- any `P0` exists

### Step 5 - Review P2/P3 issues

PASS WITH NOTES if:

- only `P2` / `P3` issues remain
- none weaken safety posture
- none confuse tester into thinking this is live trading

### Step 6 - Expansion decision

Choose one:

- PASS - safe to consider one second tester.
- HOLD - collect/fix more information before expanding.
- BLOCKED - do not expand; fix safety or launch issues first.

## Explicit non-goals

This gate does not:

- no public release
- no ZIP
- no EXE
- no installer
- approve public release
- approve ZIP distribution
- approve EXE distribution
- approve installer distribution
- approve live trading
- approve broker connection
- approve investment advice
- approve auto-trading

## Red flags

Stop immediately if:

- tester mentions placing orders
- tester entered broker credentials
- tester saw live trading language
- app asked for API keys
- app exposed account IDs
- app provided buy/sell instructions
- app claimed guaranteed profit
- app looked like investment advice
- generated artifacts were shared as a public release
