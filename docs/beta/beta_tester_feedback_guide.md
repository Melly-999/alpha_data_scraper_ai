# MellyTrade Closed Beta — Feedback Guide

> Thank you for testing MellyTrade Closed Beta v0.1.
> Your feedback directly shapes the product roadmap.

---

## What we are looking for

In this closed beta we want feedback on:

1. **Setup experience** — Was the quick start guide clear? What was confusing?
2. **UI clarity** — Is it clear that this is a read-only advisory tool?
3. **Safety transparency** — Can you easily find the safety posture (DRY RUN, read-only)?
4. **Signal and scanner legibility** — Are the signal chips and scanner cards readable?
5. **Degraded state UX** — When the broker is disconnected, is the fallback state obvious?
6. **Bug reports** — Any errors, crashes, or unexpected behaviour.

---

## What we are NOT looking for (yet)

- Feedback on trade execution quality (there is none — advisory only)
- Requests for live order placement
- Investment strategy advice
- Performance of the LSTM model in live conditions

---

## How to submit feedback

### Option A — GitHub Issue (preferred)

1. Go to the repository Issues tab
2. Click **New Issue**
3. Choose the relevant label: `beta-feedback`, `bug`, or `ux`
4. Include:
   - What you were doing
   - What you expected
   - What actually happened
   - Browser + OS version
   - Screenshot if relevant

### Option B — Bug report template

For formal bug reports, use the template at:
`docs/product/closed_beta_bug_report_template.md`

Copy the template, fill it out, and submit as a GitHub issue or send
directly to the operator.

### Option C — Direct message to operator

If you cannot submit via GitHub, send feedback directly to the operator
contact provided in your invite email.

---

## Feedback categories

When you submit a GitHub issue, use these labels:

| Label | When to use |
|---|---|
| `beta-feedback` | General UX or experience observations |
| `bug` | Something is broken or not working as expected |
| `ux` | Layout, readability, or flow issues |
| `safety-concern` | Anything that looks like it could trigger real trading |
| `docs` | Quick start or guide is unclear or wrong |

---

## Safety concern — escalate immediately

If you see **any** of the following, stop testing and report immediately
using the `safety-concern` label:

- A button or control that appears to place a real order
- The UI showing `autotrade = true` or `dry_run = false`
- A confirmation dialog suggesting a real trade is about to execute
- Any output referencing "live execution" as active (not blocked)
- Real broker account balance or real P&L that you did not expect

These are high-priority issues. The operator will review immediately.

---

## Useful things to note when testing

When exploring the terminal, try to document:

- **Terminal overview panel**: Do the market cards and signal chips make sense?
- **AI Workspace panel**: Is the scanner output clearly advisory? Are confidence bars visible?
- **Risk Manager panel**: Is the read-only posture clearly displayed?
- **Audit / Event Rail**: Are boot events visible? Are safety confirmations shown?
- **Broker Status panel**: Is the "IBKR Paper — safe disconnected" state clear?
- **DRY RUN banner**: Is it visible on first load?

---

## Feedback timeline

| Phase | Date |
|---|---|
| Beta invites sent | TBD |
| First feedback window | 2 weeks after invite |
| Bug triage | Rolling during beta |
| Feedback review call | TBD |
| Beta close | TBD |

---

## What happens with your feedback

All feedback is reviewed by the operator. Bugs will be triaged and
prioritised. UX feedback will inform the next design iteration.
General experience feedback will be used to improve documentation
and onboarding.

You will not be publicly credited without your permission.

---

## Thank you

Your time testing MellyTrade is genuinely appreciated.
This is an early-stage product and your input makes it better.

*MellyTrade Closed Beta v0.1 — Feedback guide*
