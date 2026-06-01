# Mobile AI Context Snapshot

**Task:** MOBILE-AI-000
**Type:** Context / history snapshot (docs-only)

This document preserves the product/decision history for the MellyTrade Mobile
AI workstream in repo-safe wording. It is documentation only — no code, no
providers, no screenshot upload, no runtime edits.

Safety posture for everything below:

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

## A. Source inspiration

- The user reviewed an App Store "AI chart analyzer" style app for ideas.
- Useful inspiration taken from that category:
  - screenshot / chart review
  - quick AI analysis
  - market overview
  - history of analyses
  - game-plan style output
- MellyTrade should **not** copy that app directly.
- MellyTrade should be **safer, more professional, and risk-first**: a paper
  / simulation companion and risk coach, not a signal seller.

---

## B. Final product interpretation

**MellyTrade Mobile is:**

- an AI trading co-pilot
- a paper plan generator
- a risk coach
- a setup journal
- a mobile PWA terminal
- a read-only portfolio / demo surface

**MellyTrade Mobile is NOT:**

- a signal-selling app
- a live trading app
- a broker execution app
- an investment advice app
- a wallet app
- a hidden automation app

---

## C. User-requested feature set

- AI Chart Review
- Paper Game Plan
- Mobile Watchlist
- Setup Journal
- Safety Score
- Melly Pet Coach
- Before/After Review
- FOMO Guard / No FOMO mode
- Weekly Report
- Existing Monte Carlo Simulation Snapshot (reuse the existing Monte Carlo
  concept already in the project as a simulation / risk summary — do not build
  a new Monte Carlo engine)
- Future subscription / paywall strategy
- Future PWA → Capacitor / Expo / native path

---

## D. First-run constraint

This first run (MOBILE-AI-000) is **docs-only**:

- No code.
- No providers.
- No screenshot upload.
- No runtime edits.

It updates the roadmap, records the architecture decision, preserves this
context snapshot, and defines the ClickUp / OpenAI / Claude workspace setup
plus a concrete ordered implementation plan. Nothing in this run activates,
wires, or extends any older GitHub/Claude/trading automation material — that
is treated strictly as legacy context.
