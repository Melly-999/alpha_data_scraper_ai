# First Tester Rollout Pack

> **Advisory only.** MellyTrade is a read-only AI research terminal.
> It does not place orders, route trades, or provide investment advice.
> All outputs are educational and observational.

---

## Purpose

This document defines the safe rollout plan for the first 1–3 trusted MellyTrade closed beta testers.

MellyTrade Closed Beta Demo v0.1 is:

- read-only
- dry-run
- research-only
- not investment advice
- not a live trading bot
- not an execution platform

---

## Release reference

GitHub pre-release: `v0.1-beta`

Release URL:
`https://github.com/Melly-999/alpha_data_scraper_ai/releases/tag/v0.1-beta`

---

## Required safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

---

## Who to invite first

Invite only 1–3 trusted testers who:

- understand this is a demo / research prototype
- will not treat scanner output as trading advice
- will not enter broker credentials
- will not share account data
- can provide structured feedback
- can report confusing or unsafe wording

---

## Do not invite yet

Do not invite:

- public users
- paid subscribers
- users expecting live trading
- users expecting financial advice
- anyone who may treat demo signals as trade instructions

---

## What to send

Send testers:

- release link: `https://github.com/Melly-999/alpha_data_scraper_ai/releases/tag/v0.1-beta`
- quick start: `docs/beta/beta_tester_quick_start.md`
- disclaimer: `docs/product/closed_beta_disclaimer.md`
- limitations: `docs/product/closed_beta_limitations.md`
- feedback guide: `docs/beta/beta_tester_feedback_guide.md`
- bug report template: `docs/product/closed_beta_bug_report_template.md`
- screenshots: `docs/demo/readme_screenshot_pack.md`

Do not send:

- any `.env` file or secret keys
- `profiles/real_*.json` configs
- MT5 or broker credentials
- internal architecture docs
- any live account details

---

## Tester checklist

Before the tester starts, confirm:

- [ ] they understand this is not investment advice
- [ ] they understand no live trading occurs
- [ ] they understand it is read-only and dry-run
- [ ] they know not to enter broker credentials
- [ ] they know not to share secrets/account data
- [ ] they know how to report issues
- [ ] they have read the disclaimer
- [ ] they have read the limitations doc

---

## First review session flow

Recommended flow for each tester:

1. Tester opens the release page.
2. Tester reads disclaimer and limitations.
3. Tester opens screenshot pack.
4. Tester follows quick start if running locally.
5. Tester checks terminal overview.
6. Tester checks AI scanner workspace.
7. Tester checks risk manager.
8. Tester checks audit/event rail.
9. Tester checks broker status.
10. Tester submits feedback using the feedback guide.

---

## Immediate stop conditions

Stop the test and escalate if the tester sees:

- Buy/Sell button
- Execute button
- Place order button
- Connect live broker button
- Editable live risk control
- account ID
- secret/API key
- broker credential
- copy that sounds like guaranteed profit
- copy that sounds like personal investment advice

Report immediately using `docs/product/closed_beta_bug_report_template.md`
with severity: **P0 — Safety issue**.

---

## Operator checklist

Before inviting testers:

- [ ] main is clean and aligned with origin/main
- [ ] tag `v0.1-beta` exists on origin
- [ ] release is published as pre-release at `v0.1-beta`
- [ ] safety validator passes (`py -3.11 scripts/validate_safety_config.py`)
- [ ] smoke report exists (`docs/demo/final_local_demo_smoke_report.md`)
- [ ] screenshot pack exists (`docs/demo/readme_screenshot_pack.md`)
- [ ] disclaimer exists (`docs/product/closed_beta_disclaimer.md`)
- [ ] limitations doc exists (`docs/product/closed_beta_limitations.md`)
- [ ] bug report template exists (`docs/product/closed_beta_bug_report_template.md`)
- [ ] quick start exists (`docs/beta/beta_tester_quick_start.md`)
- [ ] invite instructions reviewed (`docs/beta/beta_tester_invite_instructions.md`)
- [ ] feedback guide exists (`docs/beta/beta_tester_feedback_guide.md`)
- [ ] feedback plan reviewed (`docs/beta/first_tester_feedback_plan.md`)
- [ ] invite messages prepared (`docs/beta/first_tester_invite_messages.md`)

---

## Related docs

- `docs/beta/beta_tester_quick_start.md`
- `docs/beta/beta_tester_invite_instructions.md`
- `docs/beta/beta_tester_feedback_guide.md`
- `docs/beta/first_tester_invite_messages.md`
- `docs/beta/first_tester_feedback_plan.md`
- `docs/product/closed_beta_disclaimer.md`
- `docs/product/closed_beta_limitations.md`
- `docs/product/closed_beta_bug_report_template.md`
- `docs/release/closed_beta_demo_v0_1_candidate.md`
- `docs/release/closed_beta_demo_v0_1_next_steps.md`

---

*MellyTrade Closed Beta Demo v0.1 — First tester rollout pack*
