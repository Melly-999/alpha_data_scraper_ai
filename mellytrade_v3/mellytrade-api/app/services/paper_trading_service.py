"""PAPER-M4-002 — Risk-gated paper trading service layer.

Pure simulation service that creates and validates paper trading objects
using the PAPER-M4-001 schema types.  This module:

  - Never imports MetaTrader5, ib_insync, or any broker adapter.
  - Never registers a route or modifies app/main.py.
  - Never writes to a database or external system.
  - Never enables live order execution.

Safety invariants (identical to schemas_paper_trading.py):
  paper_only             = True   (propagated from schema Literals)
  dry_run                = True   (propagated from schema Literals)
  live_orders_blocked    = True   (propagated from schema Literals)
  requires_human_review  = True   (propagated from schema Literals)
  execution_enabled      = False  (propagated from schema Literals)
  max_risk_pct           <= 1.0   (enforced by evaluate_paper_risk)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal

from app.schemas_paper_trading import (
    PaperFill,
    PaperOrder,
    PaperPosition,
    PaperRun,
)

# ---------------------------------------------------------------------------
# Risk decision
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RiskDecision:
    """Structured allow/block result from evaluate_paper_risk.

    ``execution_enabled`` is always False — it is a safety sentinel that
    must never be set to True.  Callers can assert it without additional
    logic.
    """

    allowed: bool
    reason: str
    execution_enabled: Literal[False] = False


# ---------------------------------------------------------------------------
# Deterministic preview helpers
# ---------------------------------------------------------------------------


_PREVIEW_TIMESTAMP = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _stable_id(prefix: str, *parts: object) -> str:
    payload = "|".join(str(part) for part in parts)
    digest = sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


# ---------------------------------------------------------------------------
# evaluate_paper_risk
# ---------------------------------------------------------------------------


def evaluate_paper_risk(
    *,
    direction: str,
    entry_price: float,
    stop_loss: float | None,
    take_profit: float | None,
    max_risk_pct: float,
) -> RiskDecision:
    """Return a RiskDecision for the given trade parameters.

    Checks are applied in order; the first failing check short-circuits.
    Execution is never enabled regardless of the outcome.
    """
    if max_risk_pct > 1.0:
        return RiskDecision(
            allowed=False,
            reason=f"max_risk_pct {max_risk_pct!r} exceeds the 1.0% safety cap",
        )
    if stop_loss is None:
        return RiskDecision(allowed=False, reason="stop_loss is required")
    if take_profit is None:
        return RiskDecision(allowed=False, reason="take_profit is required")

    if direction == "BUY":
        if stop_loss >= entry_price:
            return RiskDecision(
                allowed=False,
                reason="BUY: stop_loss must be strictly below entry_price",
            )
        if take_profit <= entry_price:
            return RiskDecision(
                allowed=False,
                reason="BUY: take_profit must be strictly above entry_price",
            )
    elif direction == "SELL":
        if stop_loss <= entry_price:
            return RiskDecision(
                allowed=False,
                reason="SELL: stop_loss must be strictly above entry_price",
            )
        if take_profit >= entry_price:
            return RiskDecision(
                allowed=False,
                reason="SELL: take_profit must be strictly below entry_price",
            )

    return RiskDecision(allowed=True, reason="all risk checks passed")


# ---------------------------------------------------------------------------
# create_paper_order
# ---------------------------------------------------------------------------


def create_paper_order(
    *,
    symbol: str,
    side: str,
    quantity: float,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    confidence: float,  # noqa: ARG001 — captured for audit/logging context
    max_risk_pct: float,
) -> PaperOrder:
    """Build a PaperOrder from raw signal parameters.

    Geometry and risk constraints are validated by the PaperOrder schema.
    Safety flags are fixed by the schema's Literal fields and cannot be
    overridden here or by any caller.
    """
    return PaperOrder(
        symbol=symbol,
        direction=side,  # type: ignore[arg-type]
        quantity=quantity,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        max_risk_pct=max_risk_pct,
    )


# ---------------------------------------------------------------------------
# create_paper_fill
# ---------------------------------------------------------------------------


def create_paper_fill(order: PaperOrder) -> PaperFill:
    """Create a deterministic simulated fill from a PaperOrder.

    Fill price equals the order's entry_price (no slippage simulation).
    No broker adapter is called.  No broker_order_id, account_id, or
    execution_id is generated or referenced.
    """
    return PaperFill(
        paper_order_ref=order.paper_order_id,
        symbol=order.symbol,
        direction=order.direction,
        fill_price=order.entry_price,
        quantity=order.quantity,
    )


# ---------------------------------------------------------------------------
# open_paper_position
# ---------------------------------------------------------------------------


def open_paper_position(order: PaperOrder, fill: PaperFill) -> PaperPosition:
    """Create a PaperPosition from a filled PaperOrder.

    No database write, no broker call, no live execution.  current_price
    is initialised to the fill price (zero unrealised P&L at open).
    """
    return PaperPosition(
        paper_order_ref=order.paper_order_id,
        symbol=order.symbol,
        direction=order.direction,
        quantity=order.quantity,
        entry_price=order.entry_price,
        current_price=fill.fill_price,
        stop_loss=order.stop_loss,
        take_profit=order.take_profit,
        max_risk_pct=order.max_risk_pct,
    )


# ---------------------------------------------------------------------------
# create_paper_run
# ---------------------------------------------------------------------------


def create_paper_run(
    orders: list[PaperOrder],
    fills: list[PaperFill],
    positions: list[PaperPosition],
    *,
    max_risk_pct: float = 1.0,
) -> PaperRun:
    """Group orders, fills, and positions into a PaperRun session.

    Summary counts are derived from the supplied collections.  Safety flags
    are fixed by PaperRun schema Literals and cannot be changed here.
    """
    accepted = sum(1 for o in orders if o.status != "rejected")
    rejected = sum(1 for o in orders if o.status == "rejected")
    open_count = sum(1 for p in positions if p.status == "open")
    closed_count = sum(1 for p in positions if p.status == "closed")
    return PaperRun(
        orders=orders,
        fills=fills,
        positions=positions,
        total_signals=len(orders),
        accepted_signals=accepted,
        rejected_signals=rejected,
        open_positions_count=open_count,
        closed_positions_count=closed_count,
        max_risk_pct=max_risk_pct,
    )


# ---------------------------------------------------------------------------
# Preview stabilization
# ---------------------------------------------------------------------------


def stabilize_paper_run_preview(
    order: PaperOrder,
    fill: PaperFill,
    position: PaperPosition,
    run: PaperRun,
) -> PaperRun:
    """Return a deterministic paper-run preview without changing public APIs.

    The core service functions stay unchanged.  This helper rewrites the
    generated paper-scoped identifiers and timestamps to fixed preview
    values so GET /paper/run/preview remains deterministic for the same
    inputs while preserving the original PAPER-M4-002 contracts.
    """
    preview_order_id = _stable_id(
        "po",
        order.symbol,
        order.direction,
        order.quantity,
        order.entry_price,
        order.stop_loss,
        order.take_profit,
        order.max_risk_pct,
    )
    preview_fill_id = _stable_id("pf", preview_order_id, order.symbol)
    preview_position_id = _stable_id("pp", preview_order_id, preview_fill_id)
    preview_run_id = _stable_id(
        "run",
        run.max_risk_pct,
        (preview_order_id,),
        (preview_fill_id,),
        (preview_position_id,),
    )

    preview_order = order.model_copy(
        update={
            "paper_order_id": preview_order_id,
            "created_at": _PREVIEW_TIMESTAMP,
        }
    )
    preview_fill = fill.model_copy(
        update={
            "paper_fill_id": preview_fill_id,
            "paper_order_ref": preview_order_id,
            "fill_timestamp": _PREVIEW_TIMESTAMP,
        }
    )
    preview_position = position.model_copy(
        update={
            "paper_position_id": preview_position_id,
            "paper_order_ref": preview_order_id,
            "opened_at": _PREVIEW_TIMESTAMP,
        }
    )
    return run.model_copy(
        update={
            "run_id": preview_run_id,
            "started_at": _PREVIEW_TIMESTAMP,
            "orders": [preview_order],
            "fills": [preview_fill],
            "positions": [preview_position],
        }
    )
