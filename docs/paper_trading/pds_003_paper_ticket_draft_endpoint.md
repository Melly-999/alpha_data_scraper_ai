# PDS-003 — Paper-only Ticket Draft Endpoint

## Purpose

This document describes the paper-only ticket draft endpoint added in PDS-003.

This endpoint exposes the PDS-002 draft service through a paper-only API route.
It allows scanner previews and manual setups to submit trade ideas for
validation and human review without triggering any execution.

---

## Endpoint

```
POST /api/paper/tickets/draft
```

---

## What this endpoint is NOT

| Capability | Status |
|---|---|
| Live trading | **NEVER** |
| Real broker execution | **NEVER** — no MT5, IBKR, or any real broker |
| MT5 / IBKR order routing | **NEVER** |
| Paper fills | **Not yet** — planned in PAPER-003 |
| Paper positions | **Not yet** — planned in PAPER-004 |
| Frontend order button | **NEVER on this surface** |
| Autotrade enablement | **NEVER** |
| risk_allowed=true | **NEVER** |
| broker_execution_allowed=true | **NEVER** |

---

## Safety invariants (always enforced)

| Field | Required value |
|---|---|
| `paper_only` | `true` |
| `dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| `requires_human_review` | `true` |
| `risk_allowed` | `false` |
| `broker_execution_allowed` | `false` |
| `execution_mode` | `"paper_only_draft"` |
| `max_risk_pct` | `<= 1.0` |
| Stop loss | Required, `> 0`, geometry-validated |
| Take profit | Required, `> 0`, geometry-validated |
| Human review | Always required |

---

## Implementation

| Layer | File |
|---|---|
| Route | `app/api/routes/paper_tickets.py` |
| Service | `app/services/trade_ticket_draft_service.py` (PDS-002) |
| Schema | `app/schemas/trade_ticket.py` (PDS-001) |
| Validator | `app/services/trade_ticket_validator.py` (PDS-001) |
| Tests | `tests/app/test_paper_ticket_draft_endpoint.py` |
| Guardrails | `tests/app/test_paper_sandbox_guardrails.py` (PAPER-GUARD-001) |

---

## Sample request

```json
{
  "symbol": "EURUSD",
  "side": "long",
  "entry_type": "market_simulated",
  "timeframe": "H1",
  "entry_price": 1.1000,
  "stop_loss": 1.0950,
  "take_profit_1": 1.1100,
  "take_profit_2": 1.1200,
  "risk_pct": 0.5,
  "confidence": 80.0,
  "reason": "Strong H1 bullish momentum with RSI confirmation",
  "source": "scanner_preview"
}
```

---

## Sample accepted response

```json
{
  "accepted": true,
  "draft": {
    "ticket_id": "paper-scanner_preview-EURUSD-H1-long-a3f2c91d4b",
    "symbol": "EURUSD",
    "side": "long",
    "entry_type": "market_simulated",
    "timeframe": "H1",
    "entry_price": 1.1000,
    "stop_loss": 1.0950,
    "take_profit_1": 1.1100,
    "take_profit_2": 1.1200,
    "risk_pct": 0.5,
    "confidence": 80.0,
    "reason": "Strong H1 bullish momentum with RSI confirmation",
    "source": "scanner_preview",
    "paper_only": true,
    "dry_run": true,
    "read_only": true,
    "live_orders_blocked": true,
    "requires_human_review": true,
    "risk_allowed": false,
    "broker_execution_allowed": false,
    "execution_mode": "paper_only_draft",
    "status": "pending_review"
  },
  "validation": {
    "accepted": true,
    "status": "passed",
    "rejection_reasons": [],
    "warnings": [],
    "safety_contract": {
      "paper_only": true,
      "dry_run": true,
      "read_only": true,
      "live_orders_blocked": true,
      "requires_human_review": true,
      "risk_allowed": false,
      "broker_execution_allowed": false,
      "execution_mode": "paper_only_draft",
      "max_risk_pct": 1.0
    }
  },
  "rejection_reasons": [],
  "warnings": [],
  "safety_contract": {
    "paper_only": true,
    "dry_run": true,
    "read_only": true,
    "live_orders_blocked": true,
    "requires_human_review": true,
    "risk_allowed": false,
    "broker_execution_allowed": false,
    "execution_mode": "paper_only_draft",
    "max_risk_pct": 1.0
  }
}
```

---

## Sample rejected response

```json
{
  "accepted": false,
  "draft": null,
  "validation": null,
  "rejection_reasons": [
    "risk_pct 1.5 exceeds maximum 1.0"
  ],
  "warnings": [],
  "safety_contract": {
    "paper_only": true,
    "dry_run": true,
    "read_only": true,
    "live_orders_blocked": true,
    "requires_human_review": true,
    "risk_allowed": false,
    "broker_execution_allowed": false,
    "execution_mode": "paper_only_draft",
    "max_risk_pct": 1.0
  }
}
```

---

## HTTP behaviour

| Scenario | Status code |
|---|---|
| Valid input, accepted draft | `200 OK` |
| Valid input, rejected draft (risk/geometry/reason fail) | `200 OK` with `accepted=false` |
| Malformed JSON or missing required fields | `422 Unprocessable Entity` |
| Internal service error | `500` (never leaks exception details) |

---

## Safety contract

The safety contract is invariant and is returned in every response regardless
of whether the draft was accepted or rejected:

```json
{
  "paper_only": true,
  "dry_run": true,
  "read_only": true,
  "live_orders_blocked": true,
  "requires_human_review": true,
  "risk_allowed": false,
  "broker_execution_allowed": false,
  "execution_mode": "paper_only_draft",
  "max_risk_pct": 1.0
}
```

---

## Guardrail compliance (PAPER-GUARD-001)

| Rule | Status |
|---|---|
| Endpoint lives under `/api/paper/**` | ✅ `/api/paper/tickets/draft` |
| Summary/description includes paper/sandbox/dry_run | ✅ |
| No live broker wording except in negative context | ✅ |
| No mutating method on trading path outside paper ns | ✅ |
| No autotrade-enable route | ✅ |
| No live execution fields in response | ✅ |
| Safety Literal fields cannot be overridden | ✅ |
| Validator never flips risk_allowed | ✅ |
| Draft service always forces safety fields | ✅ |

---

## Roadmap relation

| ID | Title | Status |
|---|---|---|
| **PDS-001** | Paper-only TradeTicket schema & validator | ✅ Merged |
| **PDS-002** | Ticket Draft Service from Scanner Preview | ✅ Merged |
| **PAPER-GUARD-001** | Guardrail tests + safety contract | ✅ Merged |
| **PDS-003** | This document — draft endpoint | ✅ This PR |
| **PDS-004** | AI Workspace ticket preview | ⬜ Planned |
| **PAPER-001** | In-memory paper broker sandbox | ⬜ Planned |
| **PAPER-002** | PaperOrder / PaperFill / PaperPosition schemas | ⬜ Planned |
| **PAPER-003** | Paper-only execute endpoint behind human approval | ⬜ Planned |
| **PAPER-004** | Paper portfolio state and sandbox reset | ⬜ Planned |
| **SUPA-003** | Audit writer service | ⬜ Planned |
| **OPENCLAW-005** | Discord phone smoke tests | ⬜ Planned |
