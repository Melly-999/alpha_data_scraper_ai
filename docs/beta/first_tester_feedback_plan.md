# First Tester Feedback Plan

> Plan for collecting and reviewing feedback from the first 1–3 trusted testers
> of MellyTrade Closed Beta Demo v0.1.

---

## Purpose

This document defines the feedback collection and review process for the initial
closed beta rollout. It is docs-only and does not change any runtime behaviour.

---

## Feedback window

Recommended initial feedback window:

- **Duration:** 3–7 days
- **Tester count:** 1–3 trusted testers
- **Focus:** safety, clarity, and broken UI — not trading performance

---

## Feedback priorities

### P0 — Safety issue

Immediate stop. Do not invite more testers until resolved.

Examples:

- execution-like control visible (Buy / Sell / Execute button)
- Place order button visible
- Connect live broker control visible
- account ID or secret visible in the UI
- copy sounds like investment advice or implies profit guarantees
- live order routing appears to be active

Action:

- stop rollout immediately
- document the issue using `docs/product/closed_beta_bug_report_template.md`
- resolve and re-validate before continuing

---

### P1 — App broken

Fix before inviting more testers.

Examples:

- terminal does not load
- scanner panel broken or blank
- risk page unusable
- core navigation broken
- repeated console errors on load
- backend not starting correctly

Action:

- document in bug report
- fix and re-run smoke checklist before continuing rollout

---

### P2 — Confusing / unclear

Collect notes, batch into a UI/copy polish PR.

Examples:

- tester does not understand the demo/fallback state
- scanner explanation unclear or misleading
- safety labels (DRY RUN / READ ONLY / LIVE ORDERS BLOCKED) not obvious enough
- broker degraded state confusing
- risk posture unclear to non-technical tester
- tester unsure what the confidence bar means

Action:

- collect all notes
- group by area (scanner, risk, broker, audit rail)
- batch into v0.2 UX/copy improvement PRs

---

### P3 — Polish

Backlog for v0.2. Non-blocking.

Examples:

- spacing or contrast issue
- wording tweak
- screenshot mismatch vs live UI
- small layout issue on a specific browser
- tooltip wording unclear
- minor colour or alignment issue

Action:

- add to v0.2 polish backlog
- do not block rollout expansion for P3 items

---

## Feedback collection format

Request testers use this structure:

```
Tester:
Date:
Version/tag: v0.1-beta
Area:
Severity: P0 / P1 / P2 / P3
Summary:
Expected:
Actual:
Safety labels visible: yes / no
Screenshot attached: yes / no
Console errors:
Notes:
```

Testers may also send freeform notes — convert to the structured format during review.

---

## Operator review cadence

After each tester submits feedback:

- [ ] Review all P0 items immediately (same day)
- [ ] Review all P1 items within 24 hours
- [ ] Group P2/P3 items by area for batched review
- [ ] Update `docs/product/closed_beta_limitations.md` if new known limitations emerge
- [ ] Decide whether rollout expansion is safe before inviting the next tester

---

## Rollout expansion gate

Before inviting additional testers (beyond the first 1–3), confirm:

- [ ] No open P0 issues
- [ ] No open P1 issues
- [ ] Safety validator still passes
- [ ] README and screenshots remain accurate
- [ ] Disclaimer and limitations remain clear and current
- [ ] No new execution-like controls have been introduced
- [ ] Smoke checklist still passes

---

## Rollout log template

Track each tester:

```
Tester:
GitHub username:
Invite date:
Access granted: yes / no
First feedback date:
Feedback severity summary:
P0 issues:
P1 issues:
P2 issues:
P3 issues:
Rollout continue: yes / no
Notes:
```

---

## Candidate v0.2 themes

Potential v0.2 improvements informed by beta feedback:

- hosted staging deployment
- auth / access-control plan
- cleaner tester access flow
- better onboarding page or modal
- in-app feedback form
- deployment smoke checklist
- monitoring and logging plan
- privacy / data handling note
- mobile / responsive layout
- dark / Navy theme toggle in UI (CSS tokens already in place — PR #114)

---

## Related docs

- `docs/beta/first_tester_rollout_pack.md`
- `docs/beta/first_tester_invite_messages.md`
- `docs/beta/beta_tester_quick_start.md`
- `docs/beta/beta_tester_feedback_guide.md`
- `docs/product/closed_beta_bug_report_template.md`
- `docs/product/closed_beta_limitations.md`
- `docs/release/closed_beta_demo_v0_1_next_steps.md`

---

*MellyTrade Closed Beta Demo v0.1 — First tester feedback plan*
