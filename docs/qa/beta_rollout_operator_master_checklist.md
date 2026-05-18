# Beta Rollout Operator Master Checklist

## Purpose

Single operator checklist for the full safe source-only beta rollout.

This checklist is manual and docs-only.

It does not grant access or send invites automatically.

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

## Step 1 - Preflight

Required:

- main aligned with origin/main
- safety validator PASS
- generated artifacts not staged
- `.opencode` stash untouched
- no secrets or broker credentials
- source-only beta preflight checklist PASS

Result:

- PASS
- HOLD
- BLOCKED

## Step 2 - First tester gate

Required:

- source-only rollout gate PASS
- tester invite reviewed manually
- tester receives read-only repository access only
- no generated artifacts shared
- no broker credentials requested
- no live trading promised
- no investment advice promised

Result:

- PASS
- HOLD
- BLOCKED

## Step 3 - Local demo smoke

Required:

- safety banner visible
- terminal opens
- three local-demo endpoints return 200:
  - `/api/backtest/summary`
  - `/api/investment`
  - `/api/signals/feed`
- no 404s for required endpoints
- no order/execution controls
- no broker credential prompt

Result:

- PASS
- PASS WITH NOTES
- BLOCKED

## Step 4 - Feedback review

Required:

- first tester feedback tracker completed
- feedback review gate result PASS
- no unresolved P0
- no launch-blocking P1
- P2/P3 documented

Result:

- PASS
- HOLD
- BLOCKED

## Step 5 - Second tester expansion

Required:

- second tester expansion gate PASS
- second tester pre-access checklist PASS
- exactly one second tester
- invite reviewed manually
- read-only access only

Result:

- PASS
- HOLD
- BLOCKED

## Step 6 - Stop conditions

Stop immediately if:

- live trading appears enabled
- order/execution controls appear
- broker credentials are requested
- safety banner is missing
- dry_run=false
- read_only=false
- account IDs are exposed
- generated artifacts are committed or shared incorrectly
- app claims guaranteed profit
- app provides investment advice

## Severity reference

Use the rollout severity model:

- P0 - safety blocker
- P1 - launch blocker
- P2 - confusing but usable
- P3 - polish

## Final operator decision

Choose one:

- PASS - continue to next manual step.
- HOLD - wait for more information or fixes.
- BLOCKED - stop rollout and fix blockers first.

## Evidence to keep

Keep:

- test command results
- screenshots of safety banner
- endpoint smoke results
- tester feedback form
- P0/P1/P2/P3 log
- PASS/HOLD/BLOCKED decision notes

Do not keep:

- broker credentials
- API keys
- passwords
- tokens
- account IDs
- live portfolio screenshots
- personal financial details
