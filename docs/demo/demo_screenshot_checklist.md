# Demo Screenshot Checklist — MellyTrade Read-Only AI Ops Layer

Curated capture plan for the MERGE #100 milestone. Every screenshot below
is **safe to publish on GitHub, LinkedIn, OpenAI Showcase, or a portfolio
site** because every page is read-only.

## Pre-shot setup

1. **Backend on**: `py -3.11 -m uvicorn app.main:app --reload`
2. **Frontend on**: `cd frontend && npm run dev`
3. **Hard refresh** each page before capturing (Ctrl+Shift+R).
4. **Browser zoom**: 100%. Window width: 1440px minimum.
5. **DevTools closed** unless the screenshot is showing the network panel.
6. **Theme**: default dark — do not switch.
7. Confirm the safety banner is visible in every shot.

---

## Required shots (one each — for GitHub README)

| # | Page | Filename | What it must show |
|---|---|---|---|
| 1 | `/dashboard` | `01_dashboard.png` | Safety banner, system status card, equity curve, activity feed |
| 2 | `/signals` | `02_signals_overview.png` | Signal Review card + Decision History card + Lifecycle card visible together |
| 3 | `/signals` (1H filter) | `03_decision_history_1H.png` | Decision History with **1H quick-range chip active**, freshness label visible |
| 4 | `/signals` (custom range) | `04_decision_history_custom.png` | Decision History with from/to pickers set, "custom" range label |
| 5 | `/signals` (drawer open) | `05_reasoning_panel.png` | AI Reasoning panel open, **all four safety badges visible** |
| 6 | `/signals` (drawer, blocked) | `06_reasoning_blocked.png` | AI Reasoning panel for a blocked signal (RISK BLOCKED + HUMAN REVIEW REQUIRED badges) |
| 7 | `/audit` | `07_audit_trail.png` | Audit feed with stale_data_warning + scanner_evaluated + risk_blocked rows visible |

---

## Nice-to-have shots (portfolio + OpenAI Showcase)

| # | Page | Filename | What it must show |
|---|---|---|---|
| 8 | `/signals` (empty state) | `08_empty_state.png` | Future-only date range → "No decisions in the selected range" empty copy |
| 9 | `/signals` (lifecycle expanded) | `09_lifecycle_detail.png` | Signal lifecycle steps from `signal_received` through `audit_event_reference` |
| 10 | `/signals` (degraded badge) | `10_degraded_badge.png` | Decision History when seed-data path is active — `seed data` (amber) + `degraded` if applicable |
| 11 | `/risk` | `11_risk_manager.png` | Risk manager surface — `dry_run=true`, `auto_trade=false`, gates listed |
| 12 | `/audit` (filtered safety) | `12_audit_safety_severity.png` | Audit feed filtered to severity=safety — every row shows safety_note text |

---

## Ideal demo state for capture

To make the shots look like a real working desk:

- Use the **default in-memory seed** so the panel shows 15 decisions with
  varied symbols (AAPL, NVDA, MSFT, TSLA, AMZN, GOOG, EURUSD, GBPUSD,
  USDJPY, XAUUSD, SPY, QQQ, BTCUSD, ETHUSD, META, SPY).
- Pick a row with `confidence ≥ 80%` for the dry-run-allowed reasoning shot.
- Pick a row with `decision=blocked` and a populated `blocked_reason` for
  the blocked reasoning shot.

---

## Captioning template

Use this caption form for any screenshot posted publicly:

> *MellyTrade Read-Only AI Ops Layer — `[page name]`. Display-only:
> `autotrade=false`, `dry_run=true`, `read_only=true`,
> `live_orders_blocked=true`, max risk ≤ 1%. No live trading. No live
> broker execution. Open-source on GitHub.*

This sentence is short enough for a tweet, complete enough to defuse the
"is this an AI trading bot?" question on first read.

---

## What to NOT screenshot

- Browser DevTools showing real broker credentials (there are none in
  this repo, but never habituate to that risk).
- Anything that says `LIVE`, `executed`, or `order placed` — the system
  never produces those strings; if a screenshot would contain them,
  something is wrong.
- API request bodies showing service-role keys (no API key path exists in
  the frontend, but verify before capture).
- The `/risk` page if a user has manually edited `config.json` to flip
  any safety flag locally for testing.

---

## Output destinations

| Destination | Required shots | Format |
|---|---|---|
| `README.md` Screenshots section | 1, 2, 3, 5, 7 | PNG, 1440x900 max |
| GitHub repo `docs/assets/screenshots/` | All required + nice-to-have | PNG, lossless |
| LinkedIn / portfolio | 2, 3, 5 | PNG or WebP |
| OpenAI Showcase | 1, 2, 3, 5 | PNG, 16:9 |

---

## Verification before publishing

For every published screenshot:

- [ ] Safety banner visible
- [ ] No `LIVE` indicator anywhere on the page
- [ ] Every order-shaped row prefixed `[DRY-RUN]`
- [ ] Caption contains the safety contract
- [ ] No secrets, no account IDs, no order IDs
