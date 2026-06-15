# Paper-Sim UI Polish 001

SOURCE STATUS: Public-safe, frontend display-only polish. No secrets, no
credentials, no account IDs. This task only clarifies read-only / simulated /
demo labelling. It adds no controls and changes no backend behavior.

## 1. Purpose

Make it immediately obvious to a demo viewer that the broker / paper surfaces are
**read-only, simulated/demo, and not live trading**. Closes the one labelling gap
found on the rendered broker surface.

## 2. Scope

Frontend display/copy polish only. No backend/API, no endpoints, no scripts, no
workflows, no package changes. No new controls or mutating calls.

## 3. Components reviewed

Rendered broker / paper surfaces (via `App.tsx` routes → `TerminalShell`):

- **`IBKRBrokerCard`** — rendered on the terminal dashboard view and the
  dedicated `/brokers` route. **Gap found:** showed status flags + permissions
  but no plain-language "simulated / not live" caption. **Polished.**
- **`AlpacaPaperReadOnlyCard`** — already clearly labelled ("PAPER ONLY",
  "Advisory / demo status only — not live trading", fallback note). No change.
- **`PaperRunPreviewPanel`** (`/terminal/paper-run-preview`) — already strongly
  labelled (READ ONLY / DRY RUN / LIVE ORDERS BLOCKED / HUMAN REVIEW REQUIRED /
  EXECUTION OFF chips; "GET-only · display-only"; "No broker execution, no order
  placement, no persistence"; `Load Preview` button is GET-only). No change.
- **`SafetyBadges`** — global safety posture chips. No change.
- **`BrokerCard`** (`components/BrokerCard.tsx`) — the canonical read-only broker
  card, but its only host (`DashboardPage`) is **not routed** (`/dashboard`
  redirects to `/terminal`), so it is not rendered in the live app. Intentionally
  **left unchanged** to keep this polish scoped to verifiable, rendered surfaces.

## 4. UI changes

- `IBKRBrokerCard`: added a single display-only caption below the diagnostics
  list:

  > Paper / simulated — read-only preview. No live execution, no credentials,
  > not live trading.

  Reuses the existing `panel-note` class already used by the adjacent
  `AlpacaPaperReadOnlyCard`, so styling is consistent.

No other UI changes.

## 5. Safety labels added or confirmed

- **Added** (IBKRBrokerCard): "Paper / simulated — read-only preview. No live
  execution, no credentials, not live trading."
- **Confirmed present** elsewhere: PAPER ONLY; READ ONLY / DRY RUN / LIVE ORDERS
  BLOCKED / EXECUTION OFF / HUMAN REVIEW REQUIRED chips; "Advisory / demo status
  only"; "No broker execution, no order placement, no persistence".

## 6. Forbidden controls check

Confirmed the change adds none of, and the reviewed surface contains none of:

- Buy / Sell / Order / Execute buttons — none added.
- connect-live CTA — none.
- broker-credential input UI — none.
- order-placement / trade-submission logic — none.
- new mutating frontend calls (POST/PUT/PATCH/DELETE) — none.

The change is a static `<p>` caption only — no buttons, forms, inputs, or
handlers.

## 7. Validation

- `npm run build` (`tsc -b && vite build`) → **success** (typecheck clean; caption
  ships in the built bundle).
- `python scripts/validate_safety_config.py` → **OVERALL: PASS**.
- `git diff --check` → clean.
- No unit-test runner is configured (only Playwright e2e; no `test` script), so a
  unit test was not added (would require a new test runner / package changes,
  which are out of scope). Build + validator + static scan were run instead.

## 8. Static scan

Changed file (`IBKRBrokerCard.tsx`):

- No secrets / tokens / DB URLs / API keys / credentials / account IDs / emails /
  phones / Neon identifiers.
- No `placeOrder` / `submitOrder` / `executeTrade` / `cancelOrder` /
  `enableAutotrade` / "connect live"; no `<button>` / `<form>` / `<input>` /
  `onClick`.
- No profit / ROI / win-rate / live-trading assertions.
- buy/sell/order/execution terms appear only in read-only permission/flag
  displays (pre-existing) and the new prohibition-context caption.

## 9. Safety confirmation

- no backend/API changes ✅
- no workflows ✅
- no package changes ✅ (deps reused via a temporary, gitignored junction for the
  build only)
- no broker credentials ✅
- no env vars touched ✅
- no broker API calls ✅
- no order/execution routes added ✅
- no Buy/Sell/Order/Execute UI added ✅
- no secrets ✅
- no live-trading claims ✅
- no profit/ROI/win-rate claims ✅
- safety posture unchanged (autotrade=false, dry_run=true, read_only=true,
  live_orders_blocked=true, max risk ≤ 1%) ✅

## 10. Recommended next step

**PAPER-SIM-UI-POLISH-001-PUBLISH** (push + Draft PR), or
**BROKER-SIM-SCREENSHOT-EVIDENCE-001** to capture the labelled surfaces as demo
evidence.

---

*MellyTrade is a read-only, dry-run, paper-only portfolio project. It is not a
commercial platform, not a live trading system, and not financial advice.*
