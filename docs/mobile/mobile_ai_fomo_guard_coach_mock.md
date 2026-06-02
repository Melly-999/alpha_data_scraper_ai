# Mobile AI FOMO Guard + Risk Coach Mock (MOBILE-AI-005)

**Type:** frontend-only mock (no backend, no AI provider, no real alerts)

This note records the frontend-only polish of the FOMO Guard and Melly Pet
Risk Coach on `/mobile`, building on MOBILE-AI-003 (chart review) and
MOBILE-AI-004 (setup journal). It is display-only / paper-simulation only.

## Scope

Modified files only:

- `frontend/src/pages/MobileAppPage.tsx`
- `frontend/src/pages/mobile-app.css`

## Sections added / expanded

1. **FOMO Guard dashboard** — status ACTIVE, repeated-analysis warning,
   candle-close recommendation, and static metrics (repeated analysis,
   candle-close discipline, news-risk awareness, overtrading risk, cooldown
   suggestion, current mode = Paper only).
2. **Cooldown meter** — static visual meter (no timers/intervals/state):
   15 min suggested, waiting for confirmation, next review after candle close.
3. **Behavior rules panel** — static check-style rules ("one clean setup >
   five rushed analyses", "wait for candle close", etc.).
4. **Risk Coach Score card** — 78/100 with sub-metrics (discipline, patience,
   over-analysis control, news caution, journal completion, paper-only
   compliance) plus strongest/weakest behavior copy.
5. **Melly Pet coach messages** — 4 static coaching messages; clarifies Melly
   Pet never places orders and never enables live trading.
6. **Anti-FOMO review script** — static "before you review again" checklist.
7. **Watchlist risk nudges** — static per-asset nudges (XAUUSD, US100, EURUSD,
   WTI, BTC); no network data.
8. **Journal connection copy** — static copy linking FOMO Guard to the mock
   Setup Journal (not actual data reading).
9. **Weekly coach summary** — best behavior, risk improvement, FOMO pattern,
   next focus.

## Design

"Claude Café Terminal Theme", CSS-only: warm beige page background, dark
terminal cards, amber accents, green success highlights, blue info accents,
red/pink warning accents for risk states. No image assets, no font files, no
external UI libraries.

## Safety

- Analysis only. Not financial advice.
- Paper plan only. No live orders. Live orders blocked.
- Human review required.
- Max simulated risk 1%.
- No broker execution.
- No guaranteed profit.
- No wallet/private keys.
- No AI provider keys in frontend.

FOMO Guard and the Risk Coach are display-only / mock behavior feedback: no
backend, no persistence, no AI provider calls, no real alerts/notifications,
no timers/intervals, no `fetch`/network calls, and no buy/sell/order/execute
controls. All chips and meters are static placeholders.

## Next recommended task

MOBILE-AI-006 — Backend schemas only (typed schemas, no endpoints, no provider
calls, no DB writes).
