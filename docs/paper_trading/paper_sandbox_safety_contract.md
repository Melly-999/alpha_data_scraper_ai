# PAPER-GUARD-001 — Paper Sandbox Safety Contract

## Purpose

This contract defines guardrails for future paper-only decision support and
controlled paper sandbox work.  It is enforced by
`tests/app/test_paper_sandbox_guardrails.py` and reviewed at every PR that
touches the paper trading namespace.

Any future paper-sandbox implementation must comply with every rule in this
document.  Adding an endpoint, service, or schema that violates a rule
requires an explicit review event and a corresponding update to this contract.

---

## What the paper sandbox is NOT

| Capability | Status |
|---|---|
| Live trading | **NEVER** |
| Real broker execution | **NEVER** — no MT5, IBKR, or any real broker |
| MT5 / IBKR order routing | **NEVER** |
| Autotrade enablement | **NEVER** |
| `dry_run=false` path | **NEVER** |
| `read_only=false` path | **NEVER** |
| `live_orders_blocked=false` | **NEVER** |
| Automated order placement | **NEVER** |

---

## Invariants that must never change

| Invariant | Required value | Enforced by |
|---|---|---|
| `autotrade.enabled` | `false` | `config.json`, `test_safety_invariants.py`, guardrails |
| `autotrade.dry_run` | `true` | `config.json`, `test_safety_invariants.py`, guardrails |
| `TradeTicketDraft.paper_only` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.dry_run` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.read_only` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.live_orders_blocked` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.requires_human_review` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.broker_execution_allowed` | `False` | `Literal[False]` in schema |
| `TradeTicketDraft.risk_allowed` | `False` | `Literal[False]` in schema |
| `max_risk_pct` | `<= 1.0` | Schema `le=1.0`, validator runtime check |
| Stop loss | required | Schema required field, `gt=0`, geometry-validated |
| Take profit | required | Schema required field, `gt=0`, geometry-validated |
| Human review | required | `requires_human_review=True` always |

---

## Allowed future namespace

All future paper sandbox endpoints must live within:

```
/api/paper/**
/paper/**          (if needed for non-API routing)
```

No paper-adjacent endpoint may be placed outside this namespace.

---

## Forbidden namespace

The following path patterns must **never** be added as execution routes:

```
/api/orders
/api/order
/api/execute
/api/execution
/api/trade
/api/trades
/api/broker/execute
/api/broker/order
/api/mt5/order
/api/ibkr/order
/api/autotrade/enable
/api/live
/api/live-trade
/api/live_trade
```

Any path containing these fragments outside `/api/paper` or `/paper` that
also uses a mutating HTTP method (`POST`, `PUT`, `PATCH`, `DELETE`) or
contains live-execution metadata will fail the guardrail tests.

---

## Rules for future paper endpoint design

Every endpoint under `/api/paper/**` must comply with all of the following:

### Identity rules
- Path name, `summary`, `description`, or `operationId` must include at
  least one of: `paper`, `sandbox`, `dry_run`, `simulated`.
- Must not contain `live broker`, `real broker`, `mt5 execution`,
  `ibkr execution`, `live order`, or `place live` in metadata unless in an
  explicit negative/safety context (e.g. "does NOT call live broker").

### Implementation rules
- Must never call real broker adapters (MT5, IBKR, or any real exchange API).
- Must require human approval before any simulated execution step.
- Must never bypass `TradeTicketValidator`.
- Must emit an audit event (enforced once SUPA-003 audit writer ships).
- Must return `paper_only=true` in every response.
- Must return `dry_run=true` in every response.
- Must return `read_only=true` in every response.
- Must return `live_orders_blocked=true` in every response.
- Must never return `broker_execution_allowed=true`.
- Must never return `risk_allowed=true` until a separate reviewed
  risk-gate design has been approved and merged.

### Field rules
- Must not include any of the following in response schemas:
  `order_id`, `fill_id`, `execution_id`, `broker_order_id`,
  `account_id`, `credential`, `token`, `secret`.

---

## OpenAPI guardrail test coverage

`tests/app/test_paper_sandbox_guardrails.py` asserts:

| Check | What it catches |
|---|---|
| Schema is non-empty | Prevents vacuous passes if OpenAPI breaks |
| No live execution route outside paper namespace | Catches accidentally-placed order/execute/broker paths |
| Paper namespace endpoints are paper-only | Catches paper endpoints that forget safety metadata |
| No mutating methods on trading paths outside paper namespace | Catches POST/PUT/PATCH/DELETE on order/broker/execute paths |
| No autotrade-enable route | Catches any route that could flip autotrade on |
| `config.json` invariants | Belt-and-braces: autotrade=false, dry_run=true |
| Schema safety fields cannot be overridden | Validates `Literal[True/False]` protection |
| Validator never flips risk_allowed | Prevents accidental validator weakening |
| Draft service always forces safety fields | End-to-end safety field invariant |
| No live execution fields in paper models | Prevents model drift toward execution semantics |

---

## Roadmap relation

| ID | Title | Status |
|---|---|---|
| **PDS-001** | Paper-only TradeTicket schema & validator | ✅ Merged |
| **PDS-002** | Ticket Draft Service from Scanner Preview | ✅ Merged |
| **PAPER-GUARD-001** | This document + guardrail tests | ✅ This PR |
| **PDS-003** | Draft endpoint (read-only, no execution) | ⬜ Planned |
| **PDS-004** | AI Workspace ticket preview | ⬜ Planned |
| **PAPER-001** | In-memory paper broker sandbox | ⬜ Planned |
| **PAPER-002** | PaperOrder / PaperFill / PaperPosition schemas | ⬜ Planned |
| **PAPER-003** | Paper-only execute endpoint behind human approval | ⬜ Planned |
| **PAPER-004** | Paper portfolio state and sandbox reset | ⬜ Planned |
| **SUPA-003** | Audit writer service | ⬜ Planned |
| **OPENCLAW-005** | Discord phone smoke tests | ⬜ Planned |

---

## Updating this contract

If a future PR needs to relax any rule above, the PR must:

1. Update this document with a clear justification.
2. Update the guardrail test to reflect the new approved rule.
3. Get explicit review and approval from the project owner before merging.

Silently bypassing a guardrail without updating this document is a
safety regression by definition.
