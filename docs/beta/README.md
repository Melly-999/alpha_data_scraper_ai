# MellyTrade Beta Docs Index

## Purpose

This is the entrypoint for MellyTrade source-only beta rollout documentation.

Start here before granting tester access, sending invites, reviewing tester feedback, or expanding to additional testers.

This index is docs-only and manual.

It does not grant access, send invites automatically.

It does not:
- grant access
- send invites
- approve testers automatically
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

## Start Here

Primary operator entrypoint:

- [Beta Rollout Operator Command Center](../beta/beta_rollout_operator_command_center.md)

Master checklist:

- [Beta Rollout Operator Master Checklist](../qa/beta_rollout_operator_master_checklist.md)

Source-only beta preflight:

- [Source-Only Beta Package Review](../distribution/source_only_beta_package_review.md)
- [Source-Only Beta Preflight Checklist](../qa/source_only_beta_preflight_checklist.md)

First tester rollout:

- [Source-Only First Tester Rollout](../beta/source_only_first_tester_rollout.md)
- [Source-Only Beta Rollout Gate](../qa/source_only_beta_rollout_gate.md)
- [Source-Only Tester Invite Message](../beta/source_only_tester_invite_message.md)
- [Source-Only Tester Feedback Form](../beta/source_only_tester_feedback_form.md)

Local demo QA:

- [Local Demo Tester Smoke Checklist](../qa/local_demo_tester_smoke_checklist.md)
- [Local Demo 404 Regression Checklist](../qa/local_demo_404_regression_checklist.md)

First tester feedback:

- [First Source-Only Tester Feedback Tracker](../beta/first_source_only_tester_feedback_tracker.md)
- [First Source-Only Tester Feedback Review Gate](../qa/first_source_only_tester_feedback_review_gate.md)

Second tester expansion:

- [Second Source-Only Tester Expansion Gate](../beta/second_source_only_tester_expansion_gate.md)
- [Second Source-Only Tester Pre-Access Checklist](../qa/second_source_only_tester_pre_access_checklist.md)

## Decision Model

Use:

- `PASS` - continue to the next manual step
- `HOLD` - wait for more information or fixes
- `BLOCKED` - stop rollout and fix blockers first

When uncertain, choose `HOLD` or `BLOCKED`.

## Severity Model

Use:

- `P0` - safety blocker
- `P1` - launch blocker
- `P2` - confusing but usable
- `P3` - polish

Do not expand tester access with unresolved `P0` or launch-blocking `P1`.

## Absolute Non-Goals

This beta docs index does not approve:

- public launch
- ZIP release
- EXE release
- MSI installer
- code signing
- auto-update
- live trading
- broker execution
- investment advice
- auto-trading
