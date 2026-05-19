# PDS-002 — Ticket Draft Service from Scanner Preview

## Purpose

This service converts scanner preview data or manual setup input into
**paper-only `TradeTicketDraft` objects** for human decision support.

The service is a pure Python layer that takes structured setup data,
generates a deterministic ticket ID, constructs the PDS-001 schema, and
runs the PDS-001 validator — all without any network, broker, or database
calls.

---

## What this is NOT

| Capability | Status |
|---|---|
| Live trading | **NEVER** |
| Broker execution | **NEVER** — no MT5, IBKR, or any broker network call |
| MT5 / IBKR order routing | **NEVER** |
| REST endpoint | **Not added in this PDS** — see PDS-003 |
| Frontend execution button | **Not added** |
| Autotrade trigger | **NEVER** |
| `dry_run=false` path | **NEVER** |
| Automated order placement | **NEVER** |

---

## Safety contract (always enforced)

All safety fields are forced by the service unconditionally.  Callers
cannot override them — the PDS-001 schema rejects any attempt at the type
level.

| Field | Forced value |
|---|---|
| `paper_only` | `True` |
| `dry_run` | `True` |
| `read_only` | `True` |
| `live_orders_blocked` | `True` |
| `requires_human_review` | `True` |
| `broker_execution_allowed` | `False` |
| `risk_allowed` | `False` |
| `execution_mode` | `"paper_only_draft"` |
| `max_risk_pct` (safety_contract) | `1.0` |

`risk_allowed` and `broker_execution_allowed` are **never** flipped to
`True` anywhere in this service.

---

## Ticket ID generation

`ticket_id` is **deterministic** — the same logical setup always produces
the same ID:

```
paper-{source}-{SYMBOL}-{timeframe}-{side}-{sha256[:10]}
```

The hash is derived from `source:SYMBOL:timeframe:side`.  No randomness,
no timestamps, no UUIDs.

---

## Sample scanner-like input

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
  "confidence": 82.0,
  "reason": "Strong bullish momentum on H1; MTF alignment on H4 and D1",
  "setup_notes": "Wait for 09:00 UTC open candle confirmation",
  "scanner_signal_id": "SCAN-EURUSD-H1-2024-001",
  "source": "scanner_preview"
}
```

---

## Sample safe output shape

```json
{
  "accepted": true,
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
  },
  "draft": {
    "ticket_id": "paper-scanner_preview-EURUSD-H1-long-3f9a1b2c4d",
    "symbol": "EURUSD",
    "side": "long",
    "entry_type": "market_simulated",
    "timeframe": "H1",
    "entry_price": 1.1,
    "stop_loss": 1.095,
    "take_profit_1": 1.11,
    "take_profit_2": 1.12,
    "risk_pct": 0.5,
    "confidence": 82.0,
    "reason": "Strong bullish momentum on H1; MTF alignment on H4 and D1",
    "paper_only": true,
    "dry_run": true,
    "read_only": true,
    "live_orders_blocked": true,
    "requires_human_review": true,
    "risk_allowed": false,
    "broker_execution_allowed": false,
    "execution_mode": "paper_only_draft",
    "status": "draft",
    "risk_validation_status": "passed"
  },
  "validation": {
    "accepted": true,
    "status": "passed",
    "rejection_reasons": [],
    "warnings": []
  }
}
```

Note: no `order_id`, `fill_id`, `execution_id`, `broker_order_id`,
`account_id`, or credential fields appear in output.

---

## Rejection examples

### 1. `risk_pct > 1`

```json
{ "risk_pct": 1.5, ... }
```

**Result**: `accepted: false`
`rejection_reasons: ["risk_pct: Input should be less than or equal to 1"]`

---

### 2. Invalid long geometry — SL above entry

```json
{ "side": "long", "entry_price": 1.1000, "stop_loss": 1.1050, ... }
```

**Result**: `accepted: false`
`rejection_reasons: ["long setup: stop_loss must be below entry_price"]`

---

### 3. Invalid short geometry — TP above entry

```json
{ "side": "short", "entry_price": 1.3000, "take_profit_1": 1.3100, ... }
```

**Result**: `accepted: false`
`rejection_reasons: ["short setup: take_profit_1 must be below entry_price"]`

---

### 4. Missing stop loss

```json
{ "stop_loss": null, ... }
```

**Result**: `accepted: false`
`rejection_reasons: ["stop_loss: Input should be greater than 0"]`

---

### 5. Missing take profit

```json
{ "take_profit_1": null, ... }
```

**Result**: `accepted: false`
`rejection_reasons: ["take_profit_1: Input should be greater than 0"]`

---

### 6. Live execution fields (cannot be injected)

Any attempt to pass `broker_execution_allowed=true` or `dry_run=false`:

**Result**: the service ignores these fields entirely — they are never
present in `TradeTicketDraftInput`.  The output draft always has
`broker_execution_allowed=false` and `dry_run=true`, forced by the
PDS-001 schema.

---

## Files added by this PDS

| File | Purpose |
|---|---|
| `app/services/trade_ticket_draft_service.py` | Draft service — `TradeTicketDraftInput`, `TradeTicketDraftResult`, `TradeTicketDraftService` |
| `tests/app/test_trade_ticket_draft_service.py` | Service tests |
| `docs/paper_trading/pds_002_ticket_draft_service.md` | This document |

---

## Next planned steps

| ID | Title | Description |
|---|---|---|
| **PDS-003** | Draft endpoint (read-only, no execution) | `GET /paper/tickets/{id}` — returns stored draft for human review.  No `POST` execution endpoint. |
| **PDS-004** | AI Workspace ticket preview | Surface scanner → draft ticket pipeline in the AI Workspace tool. Advisory-only. |
| **PAPER-001** | In-memory paper broker sandbox | Simulated fill engine tracking paper P&L with no real broker connection. |
| **PAPER-002** | Paper-only execution behind human approval | Paper-only `execute` path gated on explicit human approval token.  No live orders. |
