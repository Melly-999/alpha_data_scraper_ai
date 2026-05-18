# Beta Rollout Operator Command Center

## Purpose

Central operator index for the safe MellyTrade source-only beta rollout.

This document tells the operator what to run, what to review, and when to stop
before granting source-only tester access.

This document is manual and docs-only.

It does not grant access or send invites automatically.

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
- record secrets or account IDs

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

## Golden rule

When in doubt, choose BLOCKED or HOLD.

Do not grant or expand tester access unless the relevant gate returns PASS.

## Rollout sequence

### Phase 0 - Repository and artifact preflight

Use:

- `docs/qa/source_only_beta_preflight_checklist.md`
- `docs/distribution/source_only_beta_package_review.md`

Required result:

- PASS

Stop if:

- generated artifacts are staged
- secrets are present
- safety validator fails
- broker credentials are required

### Phase 1 - First tester access gate

Use:

- `docs/qa/source_only_beta_rollout_gate.md`
- `docs/beta/source_only_first_tester_rollout.md`
- `docs/beta/source_only_tester_invite_message.md`

Required result:

- PASS

Manual-only action:

- grant read-only repository access to exactly one trusted tester
- send invite manually

Stop if:

- gate is HOLD or BLOCKED
- invite suggests live trading
- invite asks for broker credentials
- invite implies investment advice
- generated artifacts are shared as public release

### Phase 2 - Local demo smoke

Use:

- `docs/qa/local_demo_tester_smoke_checklist.md`
- `docs/qa/local_demo_404_regression_checklist.md`

Required checks:

- safety banner visible
- `/terminal` opens
- `/api/backtest/summary` returns 200
- `/api/investment` returns 200
- `/api/signals/feed` returns 200
- no order/execution controls
- no broker credential prompts

Stop if:

- required endpoint returns 404 or 500
- safety banner is missing
- dry_run=false appears
- read_only=false appears
- live trading appears enabled
- order/execution controls appear

### Phase 3 - First tester feedback

Use:

- `docs/beta/source_only_tester_feedback_form.md`
- `docs/beta/first_source_only_tester_feedback_tracker.md`
- `docs/qa/first_source_only_tester_feedback_review_gate.md`

Required result:

- first tester feedback review gate returns PASS

Stop if:

- no feedback received
- unresolved P0 exists
- launch-blocking P1 exists
- feedback says live trading appeared enabled
- app asked for broker credentials
- app presented investment advice
- app claimed guaranteed profit

### Phase 4 - Second tester expansion

Use:

- `docs/beta/second_source_only_tester_expansion_gate.md`
- `docs/qa/second_source_only_tester_pre_access_checklist.md`

Required result:

- second tester expansion gate returns PASS

Manual-only action:

- invite exactly one second trusted source-only tester

Stop if:

- first tester review gate is not PASS
- unresolved P0 exists
- unresolved launch-blocking P1 exists
- safety state is unclear
- generated artifacts were shared
- invite is not reviewed manually

## Decision model

### PASS

Use PASS only when:

- all required checks passed
- safety posture is visible and unchanged
- no unresolved P0
- no launch-blocking P1
- no generated artifact release
- no secrets or broker credentials
- operator manually reviewed the next action

### HOLD

Use HOLD when:

- more information is needed
- screenshots or logs are unclear
- P1 issue has a workaround but needs review
- P2 or P3 issues remain but do not weaken safety
- tester feedback is incomplete

### BLOCKED

Use BLOCKED when:

- safety posture is missing or weakened
- live trading appears enabled
- order/execution controls appear
- broker credentials are requested
- account IDs are exposed
- guaranteed profit is claimed
- investment advice is shown
- required endpoint 404 or 500 persists
- generated artifacts were staged or shared incorrectly

## Severity model

### P0 - Safety blocker

Examples:

- live trading appears enabled
- order/execution controls appear
- app asks for broker credentials
- safety banner missing
- dry_run=false
- read_only=false
- account IDs exposed
- investment advice claim
- guaranteed profit claim

Action:

- stop rollout
- do not invite or expand testers
- fix before continuing

### P1 - Launch blocker

Examples:

- app does not start
- frontend cannot load
- backend crashes
- `/terminal` cannot open
- required endpoint returns 404 or 500

Action:

- fix before expanding testers

### P2 - Confusing but usable

Examples:

- confusing degraded warning
- unclear copy
- confusing local-demo state
- UI looks broken but safety is intact

Action:

- track and prioritize

### P3 - Polish

Examples:

- typo
- spacing
- minor UX copy
- documentation improvement

Action:

- backlog

## Operator quick links

- Source-only beta package review: `docs/distribution/source_only_beta_package_review.md`
- Source-only preflight: `docs/qa/source_only_beta_preflight_checklist.md`
- First tester rollout: `docs/beta/source_only_first_tester_rollout.md`
- First tester rollout gate: `docs/qa/source_only_beta_rollout_gate.md`
- Tester invite message: `docs/beta/source_only_tester_invite_message.md`
- Tester feedback form: `docs/beta/source_only_tester_feedback_form.md`
- Local demo tester smoke: `docs/qa/local_demo_tester_smoke_checklist.md`
- Local-demo 404 regression: `docs/qa/local_demo_404_regression_checklist.md`
- First tester feedback tracker: `docs/beta/first_source_only_tester_feedback_tracker.md`
- First tester feedback review gate: `docs/qa/first_source_only_tester_feedback_review_gate.md`
- Second tester expansion gate: `docs/beta/second_source_only_tester_expansion_gate.md`
- Second tester pre-access checklist: `docs/qa/second_source_only_tester_pre_access_checklist.md`

## Absolute non-goals

This operator command center does not approve:

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
