# Milestone 4 Fast Track — Paper Trading / Simulation

**Reorder notice (2026-05-26):** Milestone 4 (Paper Trading / Simulation) has
been fast-tracked to execute **before** Milestone 3 (Demo / Portfolio /
Recruiter Pack). Paper trading provides the most significant engineering value
for this phase and is the primary portfolio differentiator. A working simulation
layer makes the portfolio story stronger than a demo-only walkthrough.

**Foundation:** This milestone builds directly on the existing PDS and PAPER
series already merged into `main`. See
[`docs/paper_trading/paper_sandbox_safety_contract.md`](../paper_trading/paper_sandbox_safety_contract.md)
for the safety contract that governs all paper sandbox work.

**Execution entry point:** Start here after QUEUE-019 (watchlist salvage PR
reviewed and merged).

---

## Safety posture (invariant — applies to every task in this milestone)

| Flag | Required value | Enforcement |
|---|---|---|
| `autotrade.enabled` | `false` | `config.json`, `test_safety_invariants.py` |
| `autotrade.dry_run` | `true` | `config.json`, `test_safety_invariants.py` |
| `read_only` | `true` | Schema `Literal[True]`, every response |
| `live_orders_blocked` | `true` | Schema `Literal[True]`, every response |
| `execution_enabled` | `false` | Schema `Literal[False]`, every response |
| `requires_human_review` | `true` | Schema `Literal[True]`, every response |
| `max_risk_pct` | `<= 1.0` | Schema `le=1.0`, service validator |
| Stop loss | Required field | Schema required, geometry-validated |
| Take profit | Required field | Schema required, geometry-validated |

No task in this milestone may add real broker execution, live order placement,
MT5/IBKR execution calls, account credentials, autotrade toggles, or
buy/sell/execute buttons. Every simulated action must produce an audit event.

---

## What this milestone is NOT

| Capability | Status |
|---|---|
| Live trading | **NEVER** |
| Real broker execution | **NEVER** — no MT5, IBKR, or any real exchange API |
| MT5 / IBKR order routing | **NEVER** |
| Autotrade enablement | **NEVER** |
| `dry_run=false` path | **NEVER** |
| `live_orders_blocked=false` path | **NEVER** |
| Buy / Sell / Execute / Place-order buttons | **NEVER** |
| Automated order placement | **NEVER** |

---

## The signal → paper decision flow

```
GET /signals
    ↓
Risk Check
    max_risk_pct <= 1.0%
    stop_loss required (geometry-validated)
    take_profit required (geometry-validated)
    confidence >= 70
    ↓
Paper Decision
    ACCEPT  → produces PaperOrder (in-memory only)
    REJECT  → records rejection reason
    ↓
Simulated Position / Order record
    in-memory singleton, no broker call, no DB write
    ↓
Audit Event
    emitted to GET /events and GET /api/paper/sandbox/history
    carries full safety flag set
    ↓
UI Display
    GET-only panels
    no action buttons
    no order entry forms
```

---

## Task breakdown

### PAPER-M4-001 — Paper trading domain model

**Goal:** Define the core schemas for the simulation layer: `PaperOrder`,
`PaperPosition`, `PaperFill`, `PaperRun`. These must be completely separate
from broker execution schemas and must never reference real broker types.

**Files expected:**
- `app/schemas/paper_trading.py` (new)
- `tests/app/test_paper_trading_schemas.py` (new)

**Schema requirements:**
- `PaperOrder`: `symbol`, `direction`, `quantity`, `entry_price`,
  `stop_loss` (required, geometry-validated), `take_profit` (required,
  geometry-validated), `status`, `paper_only=Literal[True]`,
  `dry_run=Literal[True]`, `live_orders_blocked=Literal[True]`,
  `requires_human_review=Literal[True]`, `execution_enabled=Literal[False]`,
  `max_risk_pct` (`le=1.0`, `gt=0`)
- `PaperPosition`: derived from filled order; `unrealized_pnl`; full safety flags
- `PaperFill`: `fill_price`, `fill_timestamp`, `order_ref`; never a real broker
  `fill_id` or `execution_id`
- `PaperRun`: collection of paper orders and positions; `run_id`, `started_at`,
  summary statistics; safety flags on every run object

**What NOT to implement:**
- No `order_id` from a real broker. No `execution_id`. No `account_id`.
- No reference to `ib_insync`, `mt5_trader`, or any broker-execution module.
- No mutation route — schema file only.

**Acceptance criteria:**
- `extra="forbid"` on all four schemas.
- `Literal[True]` locks `paper_only`, `dry_run`, `live_orders_blocked`,
  `requires_human_review`.
- `Literal[False]` locks `execution_enabled`.
- `max_risk_pct` constrained with `le=1.0`.
- Stop loss and take profit are required fields with geometry validation
  (SL < entry for LONG; SL > entry for SHORT; TP > entry for LONG;
  TP < entry for SHORT).
- No forbidden execution fields (`order_id`, `fill_id`, `execution_id`,
  `broker_order_id`, `account_id`, `credential`, `token`, `secret`).
- All tests pass.

**Suggested branch:** `feat/paper-m4-001-domain-model`
**Validation:** `py -3.11 -m pytest tests/app/test_paper_trading_schemas.py -v`

---

### PAPER-M4-002 — Risk-gated paper decision service

**Goal:** Convert read-only signal summaries into simulated paper decisions with
full risk gate enforcement. The service never imports or calls broker execution
code.

**Files expected:**
- `app/services/paper_decision_service.py` (new)
- `tests/app/test_paper_decision_service.py` (new)

**Service logic:**
- Input: `SignalSummary` (or equivalent signal schema)
- Risk gate checks:
  - Reject if `max_risk_pct > 1.0`
  - Reject if stop loss missing or geometry-invalid
  - Reject if take profit missing or geometry-invalid
  - Reject if `confidence < 70` (below `min_confidence_threshold`)
- Output: `PaperDecision` — `{ status: "accepted"|"rejected", reason: str,
  order_draft: PaperOrder | None }`
- The service must contain a source-level import guard test: zero references to
  `ib_insync`, `mt5_trader`, `brokers/`, or any live-execution symbol.

**Acceptance criteria:**
- `max_risk_pct > 1.0` → rejected, reason includes "max_risk".
- Missing stop loss → rejected, reason includes "stop_loss".
- Missing take profit → rejected, reason includes "take_profit".
- Confidence < 70 → rejected, reason includes "confidence".
- Accepted signal produces a valid `PaperOrder` draft.
- Service source file imports zero broker-execution modules (grep test).
- All safety flags `True` / `False` as required on every output.
- Tests include at least 8 distinct acceptance/rejection scenarios.

**Suggested branch:** `feat/paper-m4-002-decision-service`
**Validation:** `py -3.11 -m pytest tests/app/test_paper_decision_service.py -v`

---

### PAPER-M4-003 — Paper run audit trail

**Goal:** Every simulated paper decision emits an audit event that appears in
both the system audit feed (`GET /events`) and the paper audit history
(`GET /api/paper/sandbox/history`).

**Files expected:**
- `app/services/paper_audit_bridge.py` (new)
- `tests/app/test_paper_audit_bridge.py` (new)

**Event types emitted:**
- `paper_decision_accepted` — `symbol`, `confidence`, `risk_pct`, full safety flags
- `paper_decision_rejected` — `symbol`, `reason`, full safety flags
- `paper_risk_gate_blocked` — `gate_name`, `symbol`, `value`, safety flags

**Acceptance criteria:**
- Every accepted decision emits a `paper_decision_accepted` event.
- Every rejected decision emits a `paper_decision_rejected` event.
- Every audit event carries: `paper_only=true`, `dry_run=true`,
  `live_orders_blocked=true`, `read_only=true`, `requires_human_review=true`.
- Events appear in `GET /events` response (`source="paper_audit_bridge"`).
- Events appear in `GET /api/paper/sandbox/history` response.
- No real broker data in event metadata.
- No forbidden fields (`order_id`, `fill_id`, `account_id`, `credential`).

**Suggested branch:** `feat/paper-m4-003-audit-trail`
**Validation:** `py -3.11 -m pytest tests/app/test_paper_audit_bridge.py -v`

---

### PAPER-M4-004 — GET-only paper state endpoints

**Goal:** Add read-only endpoints for current paper positions, recent simulated
orders, and paper run summary. GET-first. No mutation routes in this task.

**Files expected:**
- `app/api/routes/paper_trading.py` (new, or extend existing paper routes)
- `tests/app/test_paper_trading_endpoints.py` (new)

**Endpoints:**
- `GET /api/paper/positions` — current in-memory paper positions list
- `GET /api/paper/orders` — recent simulated orders (last 50 by default)
- `GET /api/paper/run/summary` — current paper run stats

**All endpoints must:**
- Return safety flags: `paper_only=true`, `dry_run=true`,
  `live_orders_blocked=true`, `read_only=true`, `execution_enabled=false`,
  `requires_human_review=true`.
- Require API key (`Depends(require_api_key)`).
- Return 405 on POST/PUT/PATCH/DELETE.
- Never import or call broker adapters.

**What NOT to implement:**
- No `POST /api/paper/orders`. No `POST /api/paper/execute`.
- No broker imports in the route file.
- No live-execution path of any kind.

**Acceptance criteria:**
- All three GET endpoints return correct response shapes.
- POST/PUT/PATCH/DELETE return 405 on all three paths.
- Forbidden route scan passes (no `/execute`, `/order`, `/live` outside
  paper namespace).
- Full backend suite ≥ baseline test count.

**Suggested branch:** `feat/paper-m4-004-state-endpoints`
**Validation:** `py -3.11 -m pytest tests/app/test_paper_trading_endpoints.py -v`

---

### PAPER-M4-005 — Paper sandbox UI panel

**Goal:** Frontend read-only panel showing simulated positions, orders, and
risk decisions. Display-only. No action buttons of any kind.

**Files expected:**
- `frontend/src/components/terminal/PaperTradingPanel.tsx` (new)
- `frontend/src/hooks/usePaperPositions.ts` (new)
- `frontend/src/hooks/usePaperOrders.ts` (new)
- `frontend/src/types/paper.ts` (new)

**UI requirements:**
- Positions table: symbol, direction, entry_price, unrealized_pnl, status
- Orders table: symbol, direction, status, rejection_reason (if rejected)
- Risk decisions: confidence %, risk %, gate result (accepted / rejected), reason
- Safety badge row: `PAPER ONLY` | `DRY RUN` | `READ-ONLY` | `LIVE ORDERS BLOCKED`
- Loading / error / empty states for each table
- **No buy/sell/execute/place-order/submit buttons. No order entry forms.**

**Acceptance criteria:**
- `npm run build` clean.
- `tsc --noEmit` exits 0.
- No `apiPost`, `apiPut`, or `apiDelete` imports in panel or hooks.
- Safety badge copy present in component source.
- Existing safety invariant text scan passes.

**Suggested branch:** `feat/paper-m4-005-ui-panel`
**Validation:** `tsc --noEmit` exits 0; `npm run build` clean.

---

### PAPER-M4-006 — Scenario replay

**Goal:** Replay a set of deterministic signal scenarios through the risk gate
and paper decision logic. Useful for demos and for deterministic test coverage.

**Files expected:**
- `app/services/paper_scenario_replay.py` (new)
- `tests/app/test_paper_scenario_replay.py` (new)
- `scripts/demo_paper_scenario_replay.ps1` (new)

**Required scenarios (minimum 3):**
1. High-confidence BUY signal with valid SL/TP and risk ≤ 1% → **accepted**,
   paper order created, audit event emitted.
2. Low-confidence signal (< 70) → **rejected** by confidence gate, audit event
   emitted.
3. Signal with missing stop loss → **rejected** by risk gate, audit event
   emitted.

**Acceptance criteria:**
- Replay is deterministic (same seed, same inputs → same output every run).
- Replay never imports or calls broker execution code.
- Each replay step emits an audit event with full safety flags.
- All three minimum scenarios have passing tests.
- Demo script exits 0 on a clean local setup in < 30 seconds.

**Suggested branch:** `feat/paper-m4-006-scenario-replay`
**Validation:** `py -3.11 -m pytest tests/app/test_paper_scenario_replay.py -v`

---

### PAPER-M4-007 — Exportable paper trading report

**Goal:** Markdown/JSON report generator that summarises a paper run's signals,
decisions, risk checks, and audit events into a human-readable and
machine-readable output.

**Files expected:**
- `app/services/paper_report_service.py` (new)
- `tests/app/test_paper_report_service.py` (new)
- `GET /api/paper/report` added to the paper routes file

**Report content:**
- Run metadata: `run_id`, `started_at`, scenario count, symbol set
- Signal summary: total, accepted, rejected, by direction
- Risk gate summary: blocked count, blocking reasons breakdown
- Safety posture snapshot: all required flags, `max_risk_pct`
- Audit event count
- Output formats: `?format=markdown` (default), `?format=json`

**Acceptance criteria:**
- Report includes safety posture block with all required flags.
- Report includes honest statistics — no fabricated wins/losses.
- GET endpoint returns report in both `markdown` and `json` formats.
- No secrets, credentials, or account IDs in report output.
- All tests pass.

**Suggested branch:** `feat/paper-m4-007-paper-report`
**Validation:** `py -3.11 -m pytest tests/app/test_paper_report_service.py -v`

---

### PAPER-M4-008 — End-to-end local demo script

**Goal:** Full backend + frontend smoke flow demonstrating the complete paper
trading path: signals → risk check → paper decision → audit feed → UI display.

**Files expected:**
- `scripts/demo_paper_m4_e2e.ps1` (new)
- `docs/demo/paper_trading_m4_demo.md` (new)

**Script steps:**
1. Safety config validation: `py -3.11 scripts/validate_safety_config.py`
   — **fails fast if safety misconfigured**
2. `GET /health` — assert backend online
3. `GET /api/safety/status` (if available) — assert safety flags
4. `GET /signals` — fetch current signals
5. Run scenario replay (local call, no broker) — trigger paper decisions
6. `GET /events` — assert `paper_decision_*` audit events present
7. `GET /api/paper/positions` — assert positions state returned
8. `GET /api/paper/orders` — assert orders state returned
9. `GET /api/paper/report` — assert report generates cleanly
10. Frontend smoke: assert paper panel route (`/paper` or `/workspace`) loads

**Acceptance criteria:**
- Script exits 0 on a clean local setup.
- Safety config assertion is STEP 1 (fails fast).
- No live broker calls anywhere in the script.
- Script includes a safety statement header block.
- Demo guide documents the full flow with screenshots checklist.

**Suggested branch:** `docs/paper-m4-008-e2e-demo`
**Validation:** Run `scripts/demo_paper_m4_e2e.ps1` locally; expect exit 0.

---

## Milestone acceptance criteria

- [ ] `py -3.11 scripts/validate_safety_config.py` passes.
- [ ] No live trading routes in paper services — `grep -r "place_order\|placeOrder\|live_order" app/services/paper_*` returns 0 results.
- [ ] No broker execution imports in paper services — `grep -r "ib_insync\|mt5_trader" app/services/paper_*` returns 0 results.
- [ ] No order/buy/sell/execute UI — `grep -r "execute\|placeOrder\|buy.*button\|sell.*button" frontend/src/components/terminal/Paper*` returns 0 results.
- [ ] All paper responses include safety flags (`paper_only`, `dry_run`, `live_orders_blocked`, `read_only` all `true`).
- [ ] Tests verify `max_risk_pct <= 1.0` enforcement (rejected when exceeded).
- [ ] Tests verify stop loss is required (rejected when missing).
- [ ] Tests verify take profit is required (rejected when missing).
- [ ] Tests verify `live_orders_blocked=true` in every response.
- [ ] Tests verify `execution_enabled=false` in every response.
- [ ] Full backend test suite ≥ baseline count + M4 additions.
- [ ] `npm run build` clean.
- [ ] `tsc --noEmit` exits 0.
- [ ] End-to-end demo script exits 0 on clean local setup.

---

## Recommended execution order

| Step | Task ID | Description | Branch |
|---|---|---|---|
| A | QUEUE-019 | Review and merge watchlist salvage PR #195; close PR #46 | (existing) |
| B | PAPER-M4-001 | Paper trading domain model | `feat/paper-m4-001-domain-model` |
| C | PAPER-M4-002 | Risk-gated paper decision service | `feat/paper-m4-002-decision-service` |
| D | PAPER-M4-003 | Paper run audit trail | `feat/paper-m4-003-audit-trail` |
| E | PAPER-M4-004 | GET-only paper state endpoints | `feat/paper-m4-004-state-endpoints` |
| F | PAPER-M4-005 | Paper sandbox UI panel | `feat/paper-m4-005-ui-panel` |
| G | PAPER-M4-006 | Scenario replay | `feat/paper-m4-006-scenario-replay` |
| H | PAPER-M4-007 | Exportable paper trading report | `feat/paper-m4-007-paper-report` |
| I | PAPER-M4-008 | End-to-end local demo script | `docs/paper-m4-008-e2e-demo` |
| J | — | Continue Milestone 3 — Demo / Portfolio / Recruiter Pack | (career_execution_board.md) |

Each step is its own PR. No stacking unless there is a hard dependency
(B must merge before C; C before D; D before E). F depends on E. G–I can
proceed in parallel with F once E is merged.

---

## Milestone ordering context

| Priority | Milestone | Status |
|---|---|---|
| ✅ 1 | Terminal V1 read-only (Direction B) | Merged on main |
| ✅ 2 | Audit feed + Watchlist (QUEUE-016 → QUEUE-019) | In progress (PR #195 open) |
| **⚡ 3** | **Milestone 4 FAST TRACK — Paper Trading / Simulation (this doc)** | **Next — start after QUEUE-019** |
| 4 | Milestone 3 — Demo / Portfolio / Recruiter Pack | Deferred — richer with working paper trading |
| 5 | Stale PR cleanup (PRs #40, #46 closed; remaining stale PRs) | As needed |
| 6 | Broker abstraction + IBKR read-only (Phase B/C of `mellytrade_next_20_steps.md`) | Deferred |
| 7 | Advanced AI features, backtesting, quant research | Long-term |

The Demo / Portfolio milestone is rescheduled to **after** paper trading
simulation. Paper trading provides more substantive engineering portfolio
evidence and makes the demo walkthrough significantly more compelling.

---

## Relation to existing paper sandbox work

The following series are already ✅ merged into `main` and provide the
foundation this milestone builds on:

| Series | Description |
|---|---|
| PDS-001 | `TradeTicketDraft` schema and validator |
| PDS-002 | Ticket draft service from scanner preview |
| PDS-003 | Draft endpoint `GET /api/paper/sandbox/preview` |
| PDS-004 | AI Workspace ticket preview panel |
| PAPER-001A | In-memory paper sandbox foundation |
| PAPER-001B | Preview endpoint |
| PAPER-001C | Preview panel |
| PAPER-002A | History service |
| PAPER-002B | History endpoint `GET /api/paper/sandbox/history` |
| PAPER-002C | Activity/audit rail panel |
| PAPER-GUARD-001 | Safety contract + guardrail tests |
| PAPER-003 | Local demo script (current) |

The M4 fast track adds the **signal-to-decision pipeline** on top of this
foundation: risk-gated decisions, simulated positions/orders, scenario replay,
and exportable reports — completing the full simulation layer that turns the
paper sandbox into a decision-support trading simulator.

---

**Last updated**: 2026-05-26
