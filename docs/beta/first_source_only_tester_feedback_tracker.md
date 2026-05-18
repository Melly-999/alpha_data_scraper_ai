# First Source-Only Tester Feedback Tracker

## Purpose

Track the first trusted source-only beta tester feedback before deciding
whether to invite any second tester.

This tracker is manual and docs-only.

It does not:
- no live trading
- no broker credentials
- no order/execution controls
- no investment advice
- no guaranteed profit
- grant access
- send invites
- connect brokers
- execute orders
- create release artifacts

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

## Tester identity

Use non-sensitive identifiers only.

Fields:

- Tester handle:
- Date access granted:
- Access type: read-only GitHub repository access
- Invite message sent manually: yes/no
- Feedback received: yes/no
- Screenshots/logs received: yes/no

Do not record:

- broker account IDs
- API keys
- passwords
- tokens
- personal financial details
- live account screenshots

## Setup result

Checklist:

- repository cloned successfully
- Python 3.11 available
- Node.js LTS available
- safety validator PASS
- launcher started
- terminal UI opened
- `/terminal` visible
- no broker credentials requested

Result:

- PASS
- PASS WITH NOTES
- BLOCKED

Notes:

## Safety banner result

Checklist:

- READ ONLY visible
- DRY RUN visible
- AUTO TRADE OFF visible
- LIVE ORDERS BLOCKED visible
- NO ORDER ROUTING or equivalent visible

Stop if:

- safety banner is missing
- dry_run appears false
- read_only appears false
- live trading appears enabled
- order/execution controls appear

Result:

- PASS
- PASS WITH NOTES
- BLOCKED

Notes:

## Local-demo endpoint result

Expected endpoints:

- `GET /api/backtest/summary`
- `GET /api/investment`
- `GET /api/signals/feed`

Checklist:

- `/api/backtest/summary` returns 200
- `/api/investment` returns 200
- `/api/signals/feed` returns 200
- no 404s remain for these three endpoints
- responses are read-only / dry-run / degraded local-demo
- no account IDs exposed
- no broker credentials requested
- no order/execution fields

Result:

- PASS
- PASS WITH NOTES
- BLOCKED

Notes:

## UI feedback

Collect:

- what was clear
- what was confusing
- what looked broken
- what looked like live trading, if anything
- screenshots attached: yes/no
- browser used:
- OS:
- screen resolution, optional:

Do not collect:

- broker account screenshots
- API keys
- credentials
- personal portfolio values

## Bug log

Use severity:

- `P0` - safety blocker

Examples:

- live trading appears enabled
- order/execution button appears
- app asks for broker credentials
- safety banner missing
- `dry_run=false`
- `read_only=false`
- account IDs exposed

Action:

- stop rollout
- do not invite second tester
- fix before continuing

- `P1` - launch blocker

Examples:

- app does not start
- frontend cannot load
- backend crashes
- required endpoint returns 500
- repeated required endpoint 404

Action:

- fix before expanding testers

- `P2` - confusing but usable

Examples:

- confusing degraded warnings
- unclear wording
- layout issue
- missing explanation
- endpoint works but UI message is unclear

Action:

- track and prioritize

- `P3` - polish

Examples:

- typo
- spacing
- minor copy improvement
- small UX suggestion

Action:

- backlog

## Bug table

| ID | Severity | Area | Description | Evidence | Status | Owner | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BETA-001 | P? | setup/ui/api/docs | TBD | screenshot/log | open | TBD | TBD |

## Expansion decision

Before inviting a second tester:

Required:

- no unresolved `P0`
- no unresolved launch-blocking `P1`
- safety banner confirmed
- no order/execution controls
- no broker credentials requested
- no generated artifacts shared
- first tester feedback reviewed

Decision:

- PASS - safe to consider second tester
- HOLD - resolve issues first
- BLOCKED - safety issue, stop rollout

Decision notes:

## Related docs

- `docs/beta/source_only_first_tester_rollout.md`
- `docs/beta/source_only_tester_feedback_form.md`
- `docs/qa/source_only_beta_rollout_gate.md`
- `docs/qa/local_demo_tester_smoke_checklist.md`
- `docs/qa/local_demo_404_regression_checklist.md`
