# MellyTrade Closed Beta Demo v0.1 — Next Steps

> This document records the recommended actions after the Closed Beta Demo v0.1
> candidate was declared PASS. It is a planning and tracking reference for the
> operator — it does not change any safety posture or enable any execution path.

---

## Current state

Status: **Candidate PASS** — see `docs/release/closed_beta_demo_v0_1_candidate.md`

Safety posture (unchanged, enforced):

```
autotrade    = false
dry_run      = true
read_only    = true
live_orders_blocked = true
max risk     <= 1%
```

---

## Completed (as of v0.1 candidate)

- [x] Local backend/frontend startup path verified
- [x] Read-only smoke script passing
- [x] Safety badges and DRY RUN banner visible in UI
- [x] Scanner and watchlist visual polish (PR #115)
- [x] CSS theme tokens (Amber default, Navy optional, Crimson severity) (PR #114)
- [x] Risk manager read-only posture confirmed
- [x] Audit/event visibility with safety notes
- [x] Broker safe-disconnected/degraded state shown clearly
- [x] README screenshot pack published (PR #117)
- [x] Closed beta disclaimer and limitations docs (PR #116)
- [x] Bug report template available
- [x] Safety validator passes

---

## Immediate next steps (recommended)

### 1. Send closed beta invites

- Prepare final invite list (trusted testers, no more than 3–5 for v0.1)
- Follow `docs/beta/beta_tester_invite_instructions.md`
- Share `docs/beta/beta_tester_quick_start.md` with each tester
- Track who received invites and when

### 2. Monitor tester feedback

- Watch GitHub Issues for `beta-feedback`, `bug`, `ux`, `safety-concern` labels
- Triage bugs within 48 hours of report
- Escalate any `safety-concern` issues immediately

### 3. Optional — git tag v0.1-beta

After final operator review:

```bash
git tag -a v0.1-beta -m "MellyTrade Closed Beta v0.1 — read-only advisory terminal"
git push origin v0.1-beta
```

Only tag after confirming the safety validator and build are both green on main.

---

## Short-term roadmap (post-beta v0.1)

### Auth / access control

- Design a private access model (invite code, magic link, or OAuth)
- No public access until auth is in place
- Define session/user data separation model

### Hosted deployment

- Select hosting provider (Vercel frontend + Railway/Render backend, or VPS)
- Set up environment variables securely (no secrets in repo)
- Define staging vs production environments
- Add deployment smoke test checklist

### Privacy and legal

- Draft privacy policy (even minimal for beta)
- Draft terms of use (advisory-only, no guarantees)
- Document data handling: what is stored, for how long, who can see it

### UI improvements (informed by beta feedback)

- Mobile / responsive layout (not in v0.1)
- Dark/Navy theme toggle in the UI (CSS tokens are ready — PR #114)
- Settings screen stub
- Portfolio / reports panel improvements

### Backend improvements

- IBKR Paper adapter connection (currently safe-disconnected in demo)
- Live market data integration (read-only)
- Audit event persistence (Supabase wiring)
- Signal decision history panel

---

## Gates before v0.2 or any hosted deployment

| Gate | Status |
|---|---|
| Auth model defined | Pending |
| Privacy/data handling documented | Pending |
| Hosted deployment smoke test | Pending |
| Security review (secrets, logs, data) | Pending |
| Beta tester feedback reviewed | Pending |
| Safety validator green on deployment target | Required |

---

## What does NOT change

The following safety defaults must remain in place for all future
versions until explicitly reviewed and approved by the operator:

```
autotrade.enabled  = false
dry_run            = true
read_only          = true
live_orders_blocked = true
min_confidence     = 70
max_risk_per_trade = 1%
```

These are not product features to be toggled. They are safety controls.
Any PR that changes these values must go through explicit operator review
and approval before merge.

---

## Related documents

- `docs/release/closed_beta_demo_v0_1_candidate.md` — candidate pass report
- `docs/product/closed_beta_readiness.md` — readiness checklist and release gates
- `docs/product/closed_beta_disclaimer.md` — user-facing disclaimer
- `docs/product/closed_beta_limitations.md` — known limitations
- `docs/beta/beta_tester_invite_instructions.md` — operator invite guide
- `docs/beta/beta_tester_quick_start.md` — tester onboarding guide
- `docs/beta/beta_tester_feedback_guide.md` — feedback submission guide
- `docs/beta/first_tester_rollout_pack.md` — rollout plan and operator checklist
- `docs/beta/first_tester_invite_messages.md` — ready-to-send invite messages
- `docs/beta/first_tester_feedback_plan.md` — feedback collection and priority guide

---

*MellyTrade Closed Beta v0.1 — Next steps planning document*
