# MellyTrade Public Website QA 001

> **QA/review document.** No backend/runtime/broker/config/package/deployment
> files were changed. Three small, safe frontend CSS fixes were applied (touch
> target size, text contrast) — see Recommended Fixes. No push, merge, or
> deploy.
> **Run:** `MELLYTRADE-PUBLIC-WEBSITE-QA-001` · **Date:** 2026-07-05 · **Model:** Sonnet 5

## Outcome

**Pass, with 3 small fixes applied in this run.** The public `/` and
`/case-study` implementation from `MELLYTRADE-FRONTEND-READONLY-PROTOTYPE-001`
holds up under QA: all routes render correctly, no forbidden trading controls
exist, no live backend calls fire from either public page, and responsive
layout is clean at desktop/tablet/mobile widths. Found and fixed one
touch-target sizing issue and two text-contrast issues (both introduced by
the original implementation, both minor, both now resolved and verified).

## Branch / Commit Reviewed

- Branch: `feature/public-landing-case-study-001`
- Base commit reviewed: `da74565` (feat(frontend): add public landing and
  case-study routes)
- New commit from this QA run: adds 3 CSS-only fixes in
  `frontend/src/pages/public-site.css` (not pushed)

## Routes Checked

| Route | Result |
|---|---|
| `/` | Renders `PublicLandingPage` — hero, snapshot, AIOS preview, safety contract, product previews, GitHub evidence, mobile/PWA, CTA, footer. Pass. |
| `/case-study` | Renders `CaseStudyPage` — all 8 sections present, single `h1`. Pass. |
| `/terminal` | Unchanged, renders `.terminal-root`. Pass. |
| `/watchlist` | Unchanged. Renders its own read-only fallback state ("500 Internal Server Error… No watchlist rows available") because no backend was running in this QA session — this is `WatchlistPage`'s pre-existing graceful-degradation behavior, not a regression from this change (file untouched by the public-site work). |
| `/mobile` | Unchanged, renders fully. Pass. |
| `/terminal/paper-run-preview` | Unchanged, renders `.terminal-root`. Pass. |
| Public CTA "Enter terminal" | Confirmed `href="/terminal"` via DOM inspection. Pass. |

## Safety UI Review

Grepped the new pages, components, and fixtures for `buy`, `sell`, `execute`,
`order`, `place trade` (case-insensitive). Every match is descriptive safety
copy explicitly stating what is forbidden (e.g. "no order button", "no
execute()", "No control, button, or copy anywhere may say or imply Buy /
Sell / Execute / Order"), or the literal string `"BUY"` as a **non-interactive
text value** of a sample `SignalItem.direction` field, rendered as a plain
`<span>` inside `AISignalFeedPreview` — the same reused, props-only component
the internal terminal already uses for real signal data. It is not a button,
has no `onClick`, and sits directly under a panel header reading "no
execution controls." No Buy/Sell/Execute/Order/Place-trade control exists
anywhere in the new code.

## Public Data Review

All preview cards carry explicit `DEMO` / `PAPER` / `SIMULATED` / `READ ONLY`
labels (chips on every `ProductPreviewGrid` card, `DEMO DATA` watermark on the
terminal-preview frame, `SIMULATED` tag on the portfolio card, `PAPER` tag on
the sandbox card). Grepped for account IDs, order IDs, API keys, secrets,
tokens, passwords, and PnL — no matches except:

- `pnl: 0` in the static `demoPositions` fixture (`publicShowcaseFixtures.ts`).
  This field is **never rendered** on either public page (`positions` is not
  consumed by `ProductPreviewGrid`) — dead fixture data, not a UI-visible
  claim. No fix required; noted for cleanup in a future polish pass.
- The word "token(s)" appears only in a code comment ("Links only — no
  tokens, no secrets…") and in CSS design-token variable names — not a
  credential.

No broker logos implying live connectivity were found (`IBKRBrokerCard` is
reused with a static `data_freshness: "demo"` status and renders text/labels
only, no logo image).

## Backend Call Review

Started the local Vite dev server (`alpha-frontend` launch config) with no
backend running, and inspected the network panel on both `/` and
`/case-study`. Result: **zero requests to `/api/*` or the FastAPI proxy target
(`127.0.0.1:8001`)** on either page. All captured requests are Vite dev-server
module transforms (`/src/*.tsx`, `/node_modules/.vite/deps/*`) plus one
pre-existing, unrelated Google Fonts CSS/woff2 load declared in `index.html`
(not part of this change, not a trading/backend API).

This confirms the implementation's design choice: although `TerminalShell`,
`AIWorkspacePanel`, `SupabaseStatusCard`, `AlpacaPaperReadOnlyCard`,
`PortfolioRiskSummaryCard`, and the paper-sandbox panels are all
*transitively imported* (because `App.tsx` eagerly imports every route,
including `TerminalPage`, so Vite's dev server serves their source files
regardless of which route is active), none of them are actually **mounted**
in the render tree of `/` or `/case-study`. Their `useEffect`-based fetch
hooks (`useSupabaseStatus`, `useAlpacaPaperStatus`, `useMellyHealth`, etc.)
never fire because the owning components are never instantiated on the
public pages — confirmed by the total absence of `/api/*` traffic.

## Responsive Review

Checked `/` and `/case-study` at desktop (1280×900), tablet (768×1024), and
mobile (375×812):

| Width | Horizontal overflow | Nav | CTA | Grid |
|---|---|---|---|---|
| 1280 (desktop) | None | Full nav + HUD chip visible | Visible | 2-column preview grid |
| 768 (tablet) | None | Links hidden per design (HUD/links collapse ≤768px), CTA still visible | Visible | Single-column preview grid (matches ≤900px breakpoint) |
| 375 (mobile) | None | Links hidden, CTA visible and full touch-target size after fix | Visible | Single column, hero/CTAs stack full-width |

Hero heading and subheadline both render within viewport bounds at 375px
with no clipping or overlap. Cards stack correctly at all three widths.

## Accessibility / UX Notes

- Heading order: single `h1` per page, `h2` per section, `h3` for sub-cards —
  correct on both `/` (1×h1, 6×h2, 14×h3) and `/case-study` (1×h1, 8×h2).
- Skip-to-content links present on both pages (`#main-content` on landing,
  `#case-main` on case study) and both resolve to a real element.
- No `outline: none` or focus-suppressing CSS found anywhere in
  `index.css` or `public-site.css` — default browser focus rings are intact,
  so keyboard focus remains visible.
- `prefers-reduced-motion: reduce` rule present in `public-site.css` and
  disables animations/transitions/`scroll-behavior` globally.
- Color contrast (WCAG relative-luminance check against the `--bg` background
  `#070a0f`): `--text-primary` 16.78:1, `--amber` 9.71:1, `--amber-soft`
  11.53:1, `--cyan` 10.63:1, `--text-secondary` 6.44:1 — all pass AA (4.5:1)
  comfortably. `--text-muted` (`#5f6b7a`) measured **3.65:1, failing AA** —
  found in use on the footer disclaimer, footer pet-note, and portfolio-card
  metric labels; fixed in this run (see below).

## Validation Commands

```powershell
git diff --check                 # clean, both before and after fixes
npx tsc -b                       # clean, both before and after fixes
npm run build                    # clean, both before and after fixes
```

Not run: Playwright e2e suite (existing specs only target
`/terminal/paper-run-preview`, confirmed by source inspection to be
unaffected by this change) and the Python safety validator (no backend/Python
files were touched in either the original run or this QA run).

## Issues Found

1. **Touch target below 44px (fixed).** `.public-nav__cta` ("Enter
   terminal →") measured 37px tall on mobile — below the design pack's own
   ≥44px touch-target rule.
2. **Text contrast below WCAG AA (fixed).** `--text-muted` (3.65:1) was used
   for the footer safety disclaimer, the footer pet-note, and the portfolio
   preview card's metric labels ("Gross exposure", "Cash buffer", "Max risk /
   trade", "Posture") — all now `--text-secondary` (6.44:1).
3. **Minor, not fixed — dead CSS.** `.public-audit-mini-row` /
   `.public-audit-mini-row time` rules in `public-site.css` are unused; the
   audit-rail preview card ended up composing the real `AuditEventsPreview`
   component directly instead of this custom markup. No visual impact;
   candidate for removal in a future polish pass.
4. **Minor, not fixed — dead fixture field.** `pnl: 0` in
   `demoPositions` (`publicShowcaseFixtures.ts`) is never rendered on either
   public page. No visual impact.

## Recommended Fixes

Applied in this run (`frontend/src/pages/public-site.css` only):

- `.public-nav__cta`: added `display: inline-flex; align-items: center;
  min-height: 44px;`
- `.public-metric__label`: `color` changed from `var(--text-muted)` to
  `var(--text-secondary)`
- `.public-footer__disclaimer` and `.public-footer__pet-note`: `color`
  changed from `var(--text-muted)` to `var(--text-secondary)`

Deferred to a future polish run (low priority, no user-visible defect):
remove the unused `.public-audit-mini-row` CSS rules; remove or repurpose the
unused `pnl` field on the `demoPositions` fixture.

## Screenshots / Evidence Notes

The `preview_screenshot` tool produced an unreliable/garbled thumbnail in
this environment (unrelated to the app — DOM `getBoundingClientRect()`
confirmed correct full-width/full-height layout throughout). All visual and
layout verification in this QA pass was instead done via the accessibility
snapshot tree, `getComputedStyle`, and `getBoundingClientRect()` measurements
through `preview_eval`, which proved reliable and is the evidence basis for
every claim above.

## Next Recommended Run

`MELLYTRADE-MEDIA-GENERATION-001` — QA is clean enough to proceed to the
budgeted hero image + clip generation run. The two deferred minor items
(dead CSS, dead fixture field) do not block media work and can be swept up
in a future polish pass if desired.

## Safety Confirmation

```text
Safety confirmation:
- No broker execution or live trading enabled.
- No Buy/Sell/Execute/Order controls added.
- No secrets printed or exposed.
- No backend/runtime/broker/config/package/deployment files changed.
- No package or lock files changed.
- No external APIs called.
- No Higgsfield MCP/media generation performed.
- No push, merge, deploy, reset, clean, delete, or force operation performed.
```
