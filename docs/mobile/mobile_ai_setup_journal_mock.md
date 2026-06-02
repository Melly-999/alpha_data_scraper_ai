# Mobile AI Setup Journal Mock (MOBILE-AI-004)

**Type:** frontend-only mock (no backend, no persistence, no provider keys)

This note records the frontend-only Setup Journal expansion on `/mobile`,
building on the MOBILE-AI-003 chart-review mock. It is display-only /
paper-simulation only.

## Scope

Modified files only:

- `frontend/src/pages/MobileAppPage.tsx`
- `frontend/src/pages/mobile-app.css`

## Setup Journal sections added/expanded

1. **Journal dashboard summary** — saved setups, pending review, reviewed this
   week, best setup type, most common risk pattern, safety mode (Paper only).
2. **Saved setup cards** — XAUUSD M15, US100 M5, EURUSD H1, WTI M15 with setup,
   bias, risk, status, emotion tag, plan, and outcome (static labels only).
3. **Outcome review panel** — status chips: TP1 / TP2 / SL / Skipped /
   Invalidated / Still waiting (static, non-mutating).
4. **Emotion / behavior tag cloud** — Calm, FOMO risk, Revenge risk, News
   caution, Patient, Over-analysis, Chased entry avoided, Waited for candle
   close (links FOMO Guard + Weekly Review).
5. **Weekly learning summary** — best setup, best behavior, mistake avoided,
   highest risk pattern, next focus + metric chips (discipline 78/100,
   overtrading Medium, review completion 7/10, paper-only compliance 100%).
6. **Journal timeline** — chronological display-only event list.
7. **Melly Pet journal coach copy** — reviews saved setups, flags FOMO
   behavior, learns from paper outcomes; never places orders.
8. **Empty-state example** — "No journal entries yet. Save an analysis to
   review the setup later." (mock card, does not replace current data).

## Design

"Claude Café Terminal Theme", CSS-only: warm beige page background, dark
terminal cards, amber accents, green success highlights, blue info accents.
No image assets, no font files, no external UI libraries.

## Safety

- Analysis only. Not financial advice.
- Paper plan only. No live orders.
- Human review required.
- Max simulated risk 1%.
- No broker execution.
- No guaranteed profit.
- No wallet/private keys.
- No AI provider keys in frontend.

The journal is display-only / mock: no backend persistence, no database
writes, no screenshot upload, no AI provider calls, no `fetch`/network calls,
no buy/sell/order/execute controls. All chips and labels are static /
`aria-disabled` placeholders.
