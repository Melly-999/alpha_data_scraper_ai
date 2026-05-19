# PDS-001 — Paper-only Trade Ticket Contract

## Purpose

Trade tickets in this system are **advisory, paper-only drafts** used exclusively for
human decision support.  A `TradeTicketDraft` represents a signal or setup that a
human analyst can review and act on manually — it is **not** a live order, not an
instruction to a broker, and not a trigger for any automated execution.

The ticket schema and validator enforce this contract at the type level so that it
cannot be violated by accident or by a downstream caller passing wrong values.

---

## What this is NOT

| Capability | Status |
|---|---|
| Live trading | **NEVER** — no real order is placed |
| Broker execution | **NEVER** — no MT5, IBKR, or any broker network call |
| MT5 / IBKR order routing | **NEVER** |
| Autotrade | **NEVER** — `autotrade=false` is preserved |
| `dry_run=false` | **NEVER** — `dry_run` is hardcoded `True` in the schema |
| Automated execution of any kind | **NEVER** |
| Execution endpoint (POST/PUT/PATCH/DELETE) | **NOT added in this PDS** |

---

## Safety contract (always enforced)

Every `TradeTicketDraft` carries immutable fields that cannot be overridden:

| Field | Required value | Effect if violated |
|---|---|---|
| `paper_only` | `True` | `ValidationError` at schema level |
| `dry_run` | `True` | `ValidationError` at schema level |
| `read_only` | `True` | `ValidationError` at schema level |
| `live_orders_blocked` | `True` | `ValidationError` at schema level |
| `requires_human_review` | `True` | `ValidationError` at schema level |
| `broker_execution_allowed` | `False` | `ValidationError` at schema level |
| `risk_allowed` | `False` | `ValidationError` at schema level |
| `execution_mode` | `"paper_only_draft"` | `ValidationError` at schema level |

The `TradeTicketValidator` additionally checks these at runtime and rejects any
ticket where a safety field has been tampered with after schema construction.

---

## Risk rules (always enforced)

- **Max risk per trade: `<= 1.0%`** — `risk_pct > 1.0` is rejected
- **Stop loss required** — `stop_loss` must be present and valid (> 0)
- **Take profit required** — `take_profit_1` must be present and valid (> 0)
- **Human review required** — `requires_human_review = True` always
- **Confidence must be in `[0, 100]`**
- A warning is issued when `confidence < 70`

---

## Validation rules

### Price geometry — long setup

```
stop_loss    < entry_price          (SL must be below entry)
take_profit_1 > entry_price         (TP1 must be above entry)
take_profit_2 > entry_price         (TP2 must be above entry, if provided)
```

### Price geometry — short setup

```
stop_loss    > entry_price          (SL must be above entry)
take_profit_1 < entry_price         (TP1 must be below entry)
take_profit_2 < entry_price         (TP2 must be below entry, if provided)
```

### Warnings (non-blocking)

- `confidence < 70` → warning: below recommended threshold
- `take_profit_2` not set → warning: consider adding a second target

---

## Sample paper-only ticket (JSON)

```json
{
  "ticket_id": "TKT-2024-001",
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
  "reason": "Strong bullish momentum on H1; MTF alignment confirmed on H4 and D1",
  "setup_notes": "Wait for 09:00 UTC open candle confirmation before entry",
  "source": "scanner",
  "status": "draft",
  "risk_validation_status": "not_checked",
  "paper_only": true,
  "dry_run": true,
  "read_only": true,
  "live_orders_blocked": true,
  "requires_human_review": true,
  "risk_allowed": false,
  "broker_execution_allowed": false,
  "execution_mode": "paper_only_draft"
}
```

---

## Rejected examples

### 1. `risk_pct > 1`

```json
{ "risk_pct": 1.5, ... }
```

**Rejected**: `risk_pct 1.5 exceeds maximum 1.0`

---

### 2. Missing stop loss

```json
{ "stop_loss": null, ... }
```

**Rejected**: `stop_loss` is a required field and must be `> 0`.

---

### 3. Missing take profit

```json
{ "take_profit_1": null, ... }
```

**Rejected**: `take_profit_1` is a required field and must be `> 0`.

---

### 4. Live execution request

Any attempt to set `dry_run=false`:

```json
{ "dry_run": false, ... }
```

**Rejected at schema level**: `Input should be True` (`Literal[True]` constraint).

---

### 5. Broker execution allowed

```json
{ "broker_execution_allowed": true, ... }
```

**Rejected at schema level**: `Input should be False` (`Literal[False]` constraint).

---

### 6. Invalid long geometry (SL above entry)

```json
{
  "side": "long",
  "entry_price": 1.1000,
  "stop_loss": 1.1050,
  "take_profit_1": 1.1100
}
```

**Rejected**: `long setup: stop_loss must be below entry_price`

---

## Files added by this PDS

| File | Purpose |
|---|---|
| `app/schemas/trade_ticket.py` | Pydantic v2 schema — `TradeTicketDraft` and supporting enums |
| `app/services/trade_ticket_validator.py` | Pure deterministic validator service |
| `tests/app/test_trade_ticket_schema.py` | Schema validation tests |
| `tests/app/test_trade_ticket_validator.py` | Validator service tests |
| `docs/paper_trading/pds_001_trade_ticket_contract.md` | This document |

---

## Next planned steps

| ID | Title | Description |
|---|---|---|
| **PDS-002** | Ticket draft service from scanner preview | Wire `TradeTicketDraft` generation into the scanner preview pipeline. Still advisory, no execution. |
| **PDS-003** | Draft endpoint (read-only, no execution) | `GET /paper/tickets/{id}` — returns a stored draft for human review. No `POST` execution endpoint. |
| **PAPER-001** | In-memory paper broker sandbox | Simulated fill engine that tracks paper P&L without touching any real broker connection. |

---

## Glossary

| Term | Definition |
|---|---|
| Paper-only draft | An advisory ticket with no broker execution semantics |
| `dry_run=true` | Backend posture: no live orders are placed |
| `live_orders_blocked=true` | All live-order code paths are disabled |
| `requires_human_review=true` | A human must review and act manually; the system will not auto-execute |
| `execution_mode="paper_only_draft"` | Canonical label for this ticket type; cannot be changed |
