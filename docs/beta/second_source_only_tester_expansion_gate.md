# Second Source-Only Tester Expansion Gate

## Purpose

Define the manual gate for deciding whether it is safe to invite one second
trusted source-only beta tester.

This gate depends on completed first tester feedback review.

This document is docs-only and manual.

It does not:
- grant access
- send invites
- approve public release
- publish generated artifacts
- enable live trading
- connect brokers
- request broker credentials
- execute orders
- provide investment advice

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

## Required prerequisites

Before considering a second tester:

- first tester feedback tracker completed
- first tester feedback review gate completed
- local demo tester smoke checklist completed
- local demo 404 regression checklist completed
- no unresolved P0 issues
- no unresolved launch-blocking P1 issues
- safety banner confirmed visible
- no order/execution controls reported
- no broker credential prompt reported
- no generated artifacts shared
- no public EXE/ZIP/MSI released
- first tester feedback reviewed by operator

## Expansion rule

Only one second tester may be considered.

Do not invite more than one additional tester in this step.

Do not invite a second tester if:

- any P0 is open
- any launch-blocking P1 is open
- safety banner was missing
- dry_run=false was reported
- read_only=false was reported
- live trading appeared enabled
- order/execution controls appeared
- broker credentials were requested
- account IDs were exposed
- investment advice was shown
- guaranteed profit was claimed
- generated artifacts were shared as a public release

## Candidate criteria

Second tester should be:

- trusted
- able to follow written instructions
- willing to report bugs
- comfortable using a source-only local setup
- aware this is not live trading
- aware this is not investment advice
- aware this does not require broker credentials

Second tester should not be:

- expecting production software
- expecting live trading
- expecting broker execution
- expecting investment advice
- expecting guaranteed profits
- unwilling to report safety issues

## Pre-access checklist

Required before access:

- operator confirms first tester review gate returned PASS
- operator confirms no unresolved P0
- operator confirms no unresolved launch-blocking P1
- operator confirms source-only docs are current
- operator confirms safety validator passes on main
- operator confirms local demo endpoint tests pass
- operator confirms no generated artifacts are staged
- operator confirms no secrets or credentials are included
- operator confirms invite message was reviewed manually

## Decision

Choose one:

- PASS - safe to invite exactly one second trusted source-only tester.
- HOLD - wait; more first tester feedback or fixes needed.
- BLOCKED - do not invite second tester.

## If PASS

Manual operator steps only:

- Grant read-only repository access manually.
- Send invite manually using approved source-only invite text.
- Tell tester not to enter broker credentials.
- Tell tester this is not live trading.
- Tell tester this is not investment advice.
- Ask tester to run local demo smoke checklist.
- Ask tester to submit feedback using the feedback form.

## If HOLD

Do not invite a second tester yet.

Document what is missing:

- feedback missing
- unclear safety result
- unresolved P1
- unclear logs
- unclear screenshots
- confusing UI warnings

## If BLOCKED

Stop expansion.

Fix blockers before any additional tester access.

## Related docs

- `docs/beta/first_source_only_tester_feedback_tracker.md`
- `docs/qa/first_source_only_tester_feedback_review_gate.md`
- `docs/beta/source_only_tester_invite_message.md`
- `docs/beta/source_only_tester_feedback_form.md`
- `docs/qa/source_only_beta_rollout_gate.md`
- `docs/qa/local_demo_tester_smoke_checklist.md`
- `docs/qa/local_demo_404_regression_checklist.md`

