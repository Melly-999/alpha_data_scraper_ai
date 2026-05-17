# MellyTrade Closed Beta — Invite Instructions

> These instructions are for the **operator** sending invitations to beta testers.
> Share only the relevant sections with each tester — do not share secrets,
> internal keys, or production config.

---

## Who should receive a closed beta invite

Beta testers for v0.1 should be:

- Trusted individuals who understand this is experimental software
- Comfortable running a local dev environment (Node + Python)
- Willing to read disclaimers and provide honest feedback
- Not expecting a live trading product or investment advice

**Do not invite** anyone who:

- Expects real trading signals to execute automatically
- Is not willing to acknowledge the advisory-only disclaimer
- Does not have a suitable dev environment (see system requirements)

---

## Before sending an invite

Complete this checklist before sending any invite link:

- [ ] Local smoke test passes (`docs/demo/final_local_demo_smoke_report.md`)
- [ ] Safety validator passes (`py -3.11 scripts/validate_safety_config.py`)
- [ ] Frontend build is green (`cd frontend && npm run build`)
- [ ] Safety banner visible in browser (`DRY RUN` label present)
- [ ] No live order buttons present anywhere in the UI
- [ ] Disclaimer doc is current (`docs/product/closed_beta_disclaimer.md`)
- [ ] Limitations doc is current (`docs/product/closed_beta_limitations.md`)
- [ ] Bug report template is ready (`docs/product/closed_beta_bug_report_template.md`)
- [ ] Tester has been briefed that this is advisory only, no execution

---

## What to send to the tester

### Invite message template

```
Subject: MellyTrade Closed Beta v0.1 — Invite

Hi [Name],

You're invited to test MellyTrade Closed Beta v0.1 — a local read-only
AI trading research terminal.

IMPORTANT: This is an experimental advisory-only tool.
- It does not place trades, route orders, or provide investment advice.
- All outputs are for educational and observational purposes only.
- You must acknowledge the disclaimer before using the terminal.

Your access:
- Repository: [private repo URL]
- Branch: main

Getting started:
1. Read the disclaimer: docs/product/closed_beta_disclaimer.md
2. Follow the quick start: docs/beta/beta_tester_quick_start.md
3. Submit feedback using: docs/beta/beta_tester_feedback_guide.md

System requirements: Node 18+, Python 3.11+, 4 GB RAM, desktop browser.

Thank you for helping test MellyTrade.
```

---

## Repository access

Grant access via GitHub:

1. Go to the repository settings → Collaborators
2. Add the tester's GitHub username with **Read** access only
3. Do not grant Write or Admin access to external testers
4. Record the invite in your tester log (name, date invited, GitHub user)

---

## What to share

| Share | Do not share |
|---|---|
| Repository URL (after granting Read access) | Any `.env` file or secret keys |
| `docs/beta/beta_tester_quick_start.md` | `profiles/real_*.json` configs |
| `docs/beta/beta_tester_feedback_guide.md` | MT5 credentials |
| `docs/product/closed_beta_disclaimer.md` | Production API keys |
| `docs/product/closed_beta_limitations.md` | Internal architecture docs |
| `docs/product/closed_beta_bug_report_template.md` | Any live broker account details |

---

## Tester onboarding checklist

After the tester accepts the invite:

- [ ] Confirm tester has read and acknowledged the disclaimer
- [ ] Confirm tester has followed the quick start guide
- [ ] Confirm tester can see the DRY RUN safety banner in the UI
- [ ] Confirm tester knows how to submit feedback
- [ ] Confirm tester knows the bug report process
- [ ] Record tester's first feedback/smoke report date

---

## Revoking access

If a tester should no longer have access:

1. Go to repository settings → Collaborators
2. Remove the tester's GitHub username
3. Record the removal date in your tester log

---

## Safety reminder

The terminal must always display these postures when running:

```
autotrade    = false
dry_run      = true
read_only    = true
live_orders_blocked = true
```

If any tester reports seeing an order placement button, a live trade
execution surface, or any output that implies actual trade execution —
**do not continue the beta session** until the issue is investigated and
resolved.

Report safety anomalies immediately using the bug report template.

---

*MellyTrade Closed Beta v0.1 — Operator invite guide*
