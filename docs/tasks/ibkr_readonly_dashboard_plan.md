# IBKR-READ-002 — IBKR Paper Read-only Dashboard Plan

> Planning document only. Does not implement any broker connection, change
> runtime behaviour, or alter safety posture.

---

## Goal

Plan a safe IBKR Paper read-only dashboard for MellyTrade that surfaces
paper account status, cash/equity summary, and positions — without any
order placement, live execution, or broker credential exposure.

---

## Context

MellyTrade v0.1 shows a "safe-disconnected" broker status. IBKR-READ-002
plans the path to a richer paper account dashboard that remains read-only
and dry-run throughout. No live broker execution is ever targeted.

---

## Intended visible data

The read-only dashboard may show:

- connection status (paper / disconnected / degraded)
- paper account mode indicator
- cash balance and net equity (summary, no full account ID)
- open positions count
- positions table (symbol, quantity, unrealized PnL — no order IDs)
- unrealized PnL summary
- degraded state reason if disconnected
- safety note (DRY RUN / READ ONLY / LIVE ORDERS BLOCKED banner)

---

## Data must NOT show

- full account IDs
- secrets or API keys
- broker credentials
- TWS session tokens
- live execution controls
- order IDs or execution IDs

---

## Safety constraints

IBKR integration must remain enforced at all layers:

```text
read_only            = true
dry_run              = true
live_orders_blocked  = true
execution_enabled    = false
```

The adapter must:

- use IBKR Paper account only (not live)
- use read-only API calls only (account summary, positions)
- never call `placeOrder`, `cancelOrder`, `modifyOrder`, or equivalent
- redact any full account IDs in API responses before surfacing to the UI
- degrade gracefully if TWS/Gateway is unavailable (show disconnected state)

---

## Non-goals

IBKR-READ-002 explicitly excludes:

- order placement
- order cancellation
- order modification
- live broker execution
- connect-live broker control in the UI
- auto-trading
- account credentials stored in the app

---

## Recommended implementation phases

### Phase 1 — Better safe-disconnected UX

Surface the existing safe-disconnected / paper read-only status more clearly
in the UI. No new broker integration required.

- improve degraded-state wording and visual hierarchy
- confirm DRY RUN / READ ONLY banners are prominent
- add "paper mode only" tooltip or note

### Phase 2 — Read-only account snapshot (local TWS/Gateway Paper)

Read-only account summary from a locally running TWS or IB Gateway (Paper
account only):

- `reqAccountSummary` — cash, net equity
- Redact account ID before response leaves service layer
- Degrade gracefully if TWS not running

### Phase 3 — Read-only positions table

Read-only positions from the paper account:

- `reqPositions` — symbol, quantity, avg cost, unrealized PnL
- No order details, no execution IDs
- Display-only table in the UI — no action buttons

### Phase 4 — Dry-run trade intent preview

Display what a dry-run signal would look like as a position intent — without
sending anything to the broker. Advisory label required on every row.

---

## Existing adapter reference

The IBKR Paper adapter foundation exists in:

- `app/` — IBKR paper adapter files (see `tests/app/test_ibkr_paper_*.py`)
- `docs/IBKR_PAPER_ADAPTER.md` — adapter documentation
- `docs/LOCAL_RUNBOOK_IBKR_PAPER.md` — local runbook

Review these before implementing Phase 2 to avoid duplicating safe-disconnect
logic already in place.

---

## Acceptance criteria (Phase 2 minimum)

- [ ] paper account mode shown clearly in UI
- [ ] account ID redacted before any API response
- [ ] no order placement routes added
- [ ] no execution-like controls in UI
- [ ] degraded state shown correctly when TWS is offline
- [ ] safety validator passes
- [ ] existing IBKR paper tests still pass

---

## What this PR does NOT do

This document is a plan only. No IBKR adapter changes, no route changes, and
no UI changes are implemented here. Implementation is tracked as IBKR-READ-002
in `docs/tasks/v0_2_implementation_queue.md`.

---

## Related docs

- `docs/tasks/v0_2_implementation_queue.md` — task queue
- `docs/IBKR_PAPER_ADAPTER.md` — existing adapter documentation
- `docs/LOCAL_RUNBOOK_IBKR_PAPER.md` — local operator runbook
- `docs/BROKER_ADAPTER_PLAN.md` — broker adapter plan
- `docs/release/closed_beta_demo_v0_1_next_steps.md` — v0.1 next steps

---

*MellyTrade IBKR-READ-002 — IBKR Paper Read-only Dashboard Plan*
