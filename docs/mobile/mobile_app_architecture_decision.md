# Mobile App Architecture Decision

**Task:** MOBILE-AI-000
**Type:** Architecture decision record (docs-only)
**Status:** Accepted (first run)

This document records the architecture decision for the MellyTrade Mobile AI
workstream. It is documentation only. It does not add, wire, or modify any
runtime code, frontend component, backend endpoint, provider key, or
deployment artifact.

Safety posture for this decision and everything it describes:

- Analysis only. Not financial advice.
- Paper plan only. No live orders.
- Human review required.
- Max simulated risk 1%.
- Wait for confirmation. Do not chase.
- No broker execution.
- No guaranteed profit.
- No wallet/private keys.
- No AI provider keys in frontend.

---

## A. Decision

- Keep **MellyTrade Mobile** inside the existing `alpha_data_scraper_ai`
  repository as **PWA-first** for now.
- Use the existing `/mobile` shell (`frontend/src/pages/MobileAppPage.tsx`,
  routed in `frontend/src/App.tsx`) as the initial delivery surface.
- A future native iOS/Android app **can** become a separate project later,
  but only when native complexity actually requires it (see Section C).

The current mobile shell stays read-only / display-only. The existing safety
badges remain in place:

- READ ONLY
- DRY RUN
- LIVE ORDERS BLOCKED
- HUMAN REVIEW REQUIRED

---

## B. Why this decision

- **Fastest path to a usable demo** — the `/mobile` shell already exists and
  already renders.
- **Shared backend** — no second API surface or duplicate contracts.
- **Shared design system** — one component library, one theme, one style.
- **Shared safety contract** — the same read-only / dry-run / no-execution
  guarantees apply automatically.
- **Less repo/workflow overhead** — one CI pipeline, one review process.
- **Easier portfolio/demo iteration** — one place to screenshot, deploy, and
  show.
- **Safer than starting a new native app immediately** — no premature app
  store, payments, or native permission surface to secure.

---

## C. When to split into a separate project

Split MellyTrade Mobile into its own repo/project only when one or more of
these is genuinely required:

- App Store / Google Play release
- Capacitor / Expo / React Native wrapper
- native camera / photo picker
- push notifications
- subscriptions / payments
- separate privacy policy / release process
- separate CI/CD pipeline
- a dedicated mobile team / project lifecycle

Until then, the mobile app stays inside `alpha_data_scraper_ai`.

---

## D. Current mobile principle

- **frontend-first**
- **mock-first**
- **safety-first**
- **PWA-first**
- **paper/simulation only**
- **no execution surface**

The mobile app is a premium-feeling mobile trading terminal, an AI risk coach,
a setup journal, and a portfolio/showcase surface — **not** a signal-selling
app and **not** a live trading execution app.

---

## E. Explicit prohibitions

The MellyTrade Mobile app must never include:

- no live trading
- no broker execution
- no wallet / private keys
- no buy / sell / order / execute controls
- no AI provider keys in frontend
- no profit claims
- no investment advice claims
- no hidden execution path
- no broker credentials in the mobile app

These prohibitions are non-negotiable and apply to every phase of the Mobile
AI roadmap.
