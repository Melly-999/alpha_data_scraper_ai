# MellyTrade — IBKR Read-Only Phase Plan

A focused, phased plan for adding Interactive Brokers as a **read-only,
paper-first** broker behind the broker abstraction. **None of the
phases below are implemented as of `main` at `e758f18`.** This document
is a roadmap, not a record of completed work.

> 🚫 **Do not implement IBKR before the broker abstraction is merged.**
> See `docs/architecture/broker_abstraction_implementation_plan.md` and
> roadmap Steps 8–13.

---

## Top-level safety rules (apply to every phase below)

- IBKR is **paper-only** in V1. The adapter must refuse to run against a
  live account even if a live connection string is configured.
- IBKR is **read-only**. The adapter exposes status, account snapshot,
  and positions. **No `place_order` / `cancel_order` / `modify_order` /
  `submit_order` / `execute` methods.**
- The adapter must report `execution_enabled=False` and
  `live_orders_blocked=True` via `BrokerCapabilities`.
- When TWS / IB Gateway is unavailable, the adapter must return a
  populated `BrokerStatus(connected=False, degraded_reason=...)` —
  **not** raise to the route handler.
- No IBKR credentials in the repo. Connection parameters live in env
  vars / `.env` (git-ignored). The repo only ships an example file.
- No external network access in tests. Every IBKR test must mock the
  client.

---

## Phase 0 — Prerequisites (must merge before any IBKR work)

| Prerequisite | Status |
|---|---|
| PR #57 (SAFE-001 `/api/safety/status`) merged | open / pending |
| `BrokerAdapter` Protocol merged (Step 8 / BRK-001) | not started |
| `SafeDisconnectedBrokerAdapter` merged (Step 9 / BRK-002) | not started |
| Broker schemas merged (Step 10 / BRK-003..006) | not started |
| Broker registry merged (Step 11 / BRK-007) | not started |
| `GET /api/brokers/*` endpoints merged (Step 12 / BRK-008..011) | not started |
| Frontend `<BrokerCard>` merged (Step 13 / BRK-012..013) | not started |

**Acceptance:** all six rows show "merged" before opening any IBKR PR.

If any prerequisite isn't met, IBKR work on `main` is rejected. Stack
on the unmerged PR only if a hard scheduling pressure exists; otherwise
wait.

---

## Phase 1 — IBKR skeleton (Sprint 1 of 5)

**Goal:** wire up an adapter object and registration path, with no real
network calls. Disconnected fallback is the default.

| Item | Detail |
|---|---|
| **Recommended branch** | `feature/ibkr-readonly-skeleton` |
| **Files** | `brokers/ibkr_paper.py` (extend existing or rewrite), `brokers/ibkr_config.py` (new), `app/core/container.py` (conditional registration), `tests/app/test_ibkr_skeleton.py` (new), `.env.example` (placeholder vars only) |
| **What to implement** | Config model (host, port, client_id, paper-only flag); a `IBKRPaperAdapter` class implementing `BrokerAdapter`; `connect()` wrapper with try/except; disconnected fallback path; conditional registration in the container if config is present and import of `ib_insync` succeeds. |
| **What NOT to implement** | No order placement methods. No live mode. No real network in tests. No background reconnect loop. No persistence. |
| **Acceptance criteria** | (1) Adapter satisfies the `BrokerAdapter` Protocol (`runtime_checkable` test). (2) Adapter source file contains zero references to `placeOrder`/`Order`/`MarketOrder`/`LimitOrder` from `ib_insync` (grep test). (3) When `ib_insync` import fails, adapter is **not registered** and registry still works. (4) When `connect()` raises, adapter `status()` returns `connected=False` with a populated `degraded_reason`. (5) `capabilities()` reports `read_only=True`, `paper=True`, `execution_enabled=False`, `live_orders_blocked=True`. |
| **Tests required** | At least 8 assertions, all with mocked `ib_insync`. Specifically: protocol satisfaction; capabilities flags; disconnected fallback returns expected status; missing-import path doesn't register; **no order-execution symbol in adapter source**. |
| **Validation** | `py -3.11 -m pytest tests/app/test_ibkr_skeleton.py -v` ≥ 8 passed; full suite ≥ baseline. |
| **Safety rules** | All Top-level safety rules above. Plus: no live host/port allowed in `IBKRConfig` (validate `paper=True` at the schema level). |
| **Bundle?** | No. Single PR. |
| **Risk** | Med — first network-aware adapter. Mitigated by mocked tests + disconnected default. |

---

## Phase 2 — Read-only account snapshot (Sprint 2 of 5)

**Goal:** map IB's `accountValues()` to `BrokerAccount` schema.

| Item | Detail |
|---|---|
| **Recommended branch** | `feature/ibkr-readonly-account` |
| **Files** | `brokers/ibkr_paper.py` (extend), `tests/app/test_ibkr_account.py` (new) |
| **What to implement** | `account_snapshot()` method that pulls `cash`, `buying_power`, `equity`, `currency`. Maps IB tag names (`TotalCashValue`, `BuyingPower`, `EquityWithLoanValue`, `BaseCurrency`) to schema fields. Tolerates missing tags by returning safe defaults (`0.0` / `"USD"`). |
| **What NOT to implement** | No account ID exposure in the schema. No multi-account selector (Phase 6+). No persistence. |
| **Acceptance criteria** | (1) `account_snapshot()` returns a valid `BrokerAccount`. (2) Missing IB tags don't raise — return zeros. (3) Currency parsed correctly when present. (4) Method is idempotent — multiple calls don't drift. (5) Disconnected adapter returns a zeroed `BrokerAccount` (the safe-disconnected behaviour). |
| **Tests required** | ≥ 6 assertions with mocked `accountValues()` returning various shapes (full / partial / empty / error). |
| **Validation** | `pytest tests/app/test_ibkr_account.py -v`; full suite still green. |
| **Safety rules** | Account snapshot must **never** include `account_id`, IB account number, or any other unique identifier in the response payload (privacy / screenshot risk). |
| **Bundle?** | No. |
| **Risk** | Low |

---

## Phase 3 — Read-only positions (Sprint 3 of 5)

**Goal:** map IB's `positions()` to `list[BrokerPosition]`.

| Item | Detail |
|---|---|
| **Recommended branch** | `feature/ibkr-readonly-positions` |
| **Files** | `brokers/ibkr_paper.py` (extend), `tests/app/test_ibkr_positions.py` (new) |
| **What to implement** | `positions()` method returning a list of `BrokerPosition(symbol, quantity, avg_price, unrealized_pnl)`. Filters to non-zero quantity. Sorts by symbol for stable output. Handles missing fields gracefully (zeros). |
| **What NOT to implement** | No order history (Phase 6+). No position close affordances. No `order_id` / `ticket` fields. |
| **Acceptance criteria** | (1) `positions()` returns the list (possibly empty). (2) Closed positions (qty=0) excluded. (3) Symbol displayed as a clean string (e.g. `"AAPL"`, not the full `Contract` repr). (4) Disconnected adapter returns `[]`. (5) Source file contains no order-execution symbols (grep test still passes). |
| **Tests required** | ≥ 5 assertions with mocked `positions()` returning multiple contracts of mixed asset types (stock, forex, futures-paper). |
| **Validation** | `pytest tests/app/test_ibkr_positions.py -v`; full suite still green. |
| **Safety rules** | All Top-level safety rules. |
| **Bundle?** | No. Can ship the same week as Phase 2. |
| **Risk** | Low |

---

## Phase 4 — Frontend: IBKR Paper BrokerCard (Sprint 4 of 5)

**Goal:** the dashboard renders an IBKR-specialised card backed by the
generic `<BrokerCard>` plus a small specialisation file.

| Item | Detail |
|---|---|
| **Recommended branch** | `feature/ibkr-frontend-card` |
| **Files** | `frontend/src/components/cards/IBKRBrokerCard.tsx` (new), `frontend/src/pages/DashboardPage.tsx` (wire one card), `frontend/src/index.css` (one-off styling) |
| **What to implement** | An `<IBKRBrokerCard>` that consumes `useBrokerStatus("ibkr-paper")` + `useBrokerAccount("ibkr-paper")` + `useBrokerPositions("ibkr-paper")` and renders into the shared `<BrokerCard>` shape. Disconnected UX: red dot, populated `degraded_reason`, capability pills still visible. **No buttons.** |
| **What NOT to implement** | No "Connect" button (the adapter auto-attempts connection at startup). No order entry. No clickable rows. No symbol search. |
| **Acceptance criteria** | (1) `IBKRBrokerCard` is GET-only — no `apiPost`/`apiPut`/`apiDelete` imports. (2) `<Badge>` text includes `READ-ONLY`, `PAPER`, `LIVE ORDERS BLOCKED`. (3) Disconnected variant renders without throwing. (4) `npm run build` clean. (5) Existing safety-invariants frontend scan still passes. |
| **Tests required** | Frontend test suite is not yet wired up; for this phase the contract is enforced by `tests/app/test_safety_invariants.py` (text-scan against the new file) — extend the page glob list to include `IBKRBrokerCard.tsx`. |
| **Validation** | `npm run build`; `pytest tests/app/test_safety_invariants.py -q` (still 39+ passing). |
| **Safety rules** | The card text must read `READ-ONLY` / `PAPER` / `NO ORDERS PLACED` (or similar copy that the existing safety scan accepts). |
| **Bundle?** | No. Last UI piece before docs/smoke. |
| **Risk** | Low |

---

## Phase 5 — Docs + smoke scripts (Sprint 5 of 5)

**Goal:** an operator can stand up TWS / IB Gateway in paper mode and
observe the dashboard pick it up. Then disconnect and confirm safe
degradation.

| Item | Detail |
|---|---|
| **Recommended branch** | `docs/ibkr-paper-runbook` |
| **Files** | `docs/IBKR_PAPER_ADAPTER.md` (extend existing), `scripts/smoke_ibkr_disconnected.ps1` (new), `scripts/smoke_ibkr_mocked.ps1` (new) |
| **What to implement** | (1) An updated runbook covering: TWS / Gateway paper login, port 7497 vs 4002, `.env` variables, expected dashboard state, troubleshooting. (2) A smoke script that runs the backend + frontend and asserts the IBKR card renders the disconnected state. (3) A smoke script that runs the backend + frontend with a mocked `ib_insync` client returning canned data. |
| **What NOT to implement** | No real-account smoke. No live-order smoke. No production deployment guide. |
| **Acceptance criteria** | (1) Runbook lists every env var by name with placeholder values. (2) Disconnected smoke script passes on a fresh checkout with no IB process running. (3) Mocked smoke script passes deterministically. (4) Runbook links to `docs/architecture/broker_abstraction_implementation_plan.md` for the underlying contract. |
| **Tests required** | Smoke scripts are themselves the test. |
| **Validation** | Run both scripts manually; expect 0 exit code. |
| **Safety rules** | The runbook must include a warning paragraph: *"This adapter is paper-only and read-only. Do not connect against a live IB account. The adapter will refuse to start if the configured `paper` flag is False."* |
| **Bundle?** | No. |
| **Risk** | Low |

---

## Acceptance criteria (rolled up across all phases)

A reviewer should be able to confirm all of the following before
declaring "IBKR Read-Only" complete:

- [ ] All five phases merged in order.
- [ ] `BrokerAdapter` Protocol has zero execution methods (Phase 0 prerequisite).
- [ ] `IBKRPaperAdapter` source file has zero references to `placeOrder` / `Order` / `MarketOrder` / `LimitOrder` (grep test passes).
- [ ] When TWS / Gateway is unreachable, the dashboard renders a degraded card with a populated `safety_note` — no exception leaks to the user.
- [ ] When mocked client is reachable, the dashboard renders a connected card showing zeros for cash/equity (since paper account starts empty) and a green status dot.
- [ ] The four `GET /api/brokers/*` endpoints work for `id="ibkr-paper"`.
- [ ] All 39+ safety-invariants assertions still pass.
- [ ] Backend test count ≥ baseline + IBKR phase additions.
- [ ] No IBKR credentials anywhere in the repo (grep + `.env.example` only).

---

## What NOT to implement (in any phase)

Each item below is intentionally out of scope; adding it would require a
separate, escalation-level review:

- ❌ **Live IBKR account support.** The adapter must refuse `paper=False`.
- ❌ **Order placement of any kind**, including dry-run order submission.
- ❌ **Bracket orders, OCO, OCA**, or any other order-management primitive.
- ❌ **Account ID, name, or any unique identifier** in the public schema.
- ❌ **Persisting IBKR data to disk** (positions, balances, etc.). Polling is in-memory only.
- ❌ **Multiple concurrent IBKR accounts** in V1 (one paper account is enough).
- ❌ **TWS / Gateway auto-launch** from the backend.
- ❌ **Any UI button labelled `Trade`, `Buy`, `Sell`, `Submit`, `Execute`, or similar.**

---

## Recommended branch names (summary)

| Phase | Branch |
|---|---|
| 1 — Skeleton | `feature/ibkr-readonly-skeleton` |
| 2 — Account | `feature/ibkr-readonly-account` |
| 3 — Positions | `feature/ibkr-readonly-positions` |
| 4 — Frontend card | `feature/ibkr-frontend-card` |
| 5 — Docs + smoke | `docs/ibkr-paper-runbook` |

Each branch is its own PR. None of them stack on each other; they all
branch off the latest `main` after the previous phase's PR has merged.

---

**Last updated**: 2026-05-09
