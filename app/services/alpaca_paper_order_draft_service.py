"""ALPACA-PAPER-ORDER-DRAFT-001 — service for POST /api/alpaca-paper/order-draft.

Builds a **local-only** Alpaca paper order draft from user input. This service:

- Validates symbol, side, order type, time-in-force, quantity/notional, the
  required stop-loss / take-profit / entry geometry, and the per-trade risk cap.
- Returns a blocked draft (``valid=false``) on any validation failure (HTTP 200).
- Returns an approved draft (``valid=true``) with a local ``paper-draft-*`` id.
- **Never** submits, places, routes, cancels, replaces, or executes any order.
- **Never** calls Alpaca, any broker, any network, any database.
- **Never** imports the Alpaca SDK and never reads environment variables.
- **Never** returns account_id, broker_order_id, execution_id, api_key, secret,
  or token.

Safety invariants are carried by ``AlpacaPaperOrderDraftResponse``:
``draft_only=true``, ``order_submission_enabled=false``,
``execution_enabled=false``, ``live_orders_blocked=true``, ``dry_run=true``,
``read_only=true``, ``requires_human_review=true``, ``max_risk_pct <= 1.0``.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from app.schemas.alpaca_paper_order_draft import (
    AlpacaPaperOrderDraft,
    AlpacaPaperOrderDraftRequest,
    AlpacaPaperOrderDraftResponse,
)

_MAX_RISK_PCT: float = 1.0
_ALLOWED_ORDER_TYPES: frozenset[str] = frozenset(
    {"market", "limit", "stop", "stop_limit"}
)
_ALLOWED_TIME_IN_FORCE: frozenset[str] = frozenset(
    {"day", "gtc", "ioc", "fok", "opg", "cls"}
)


def _short_hash(value: str) -> str:
    """Deterministic 12-char hex prefix of SHA-256(value).

    Used for a local paper-scoped draft id. Not a broker order/execution id.
    """
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def _blocked(reason: str) -> AlpacaPaperOrderDraftResponse:
    return AlpacaPaperOrderDraftResponse(valid=False, reason=reason, draft=None)


def build_alpaca_paper_order_draft(
    request: AlpacaPaperOrderDraftRequest,
) -> AlpacaPaperOrderDraftResponse:
    """Validate input and build a local paper order draft.

    Never raises for invalid input — returns ``valid=false`` with a reason.
    Never submits the draft to Alpaca or any broker.
    """
    symbol = request.symbol.strip().upper()
    side = (request.side or "").strip().upper()
    order_type = (request.order_type or "").strip().lower()
    tif = (request.time_in_force or "").strip().lower()

    if not symbol:
        return _blocked("symbol is required. Draft blocked.")

    if side not in ("BUY", "SELL"):
        return _blocked(
            f"Unknown side '{request.side}'. Must be BUY or SELL. Draft blocked."
        )

    if order_type not in _ALLOWED_ORDER_TYPES:
        return _blocked(
            f"Unknown order_type '{request.order_type}'. Must be one of "
            f"{sorted(_ALLOWED_ORDER_TYPES)}. Draft blocked."
        )

    if tif not in _ALLOWED_TIME_IN_FORCE:
        return _blocked(
            f"Unknown time_in_force '{request.time_in_force}'. Must be one of "
            f"{sorted(_ALLOWED_TIME_IN_FORCE)}. Draft blocked."
        )

    has_qty = request.quantity is not None and request.quantity > 0
    has_notional = request.notional is not None and request.notional > 0
    if has_qty == has_notional:
        return _blocked(
            "Provide exactly one positive quantity or notional "
            "(not both, not neither). Draft blocked."
        )

    entry_price = request.entry_price
    stop_loss = request.stop_loss
    take_profit = request.take_profit
    for label, value in (
        ("entry_price", entry_price),
        ("stop_loss", stop_loss),
        ("take_profit", take_profit),
    ):
        if value is None or value <= 0:
            return _blocked(f"{label} is required and must be positive. Draft blocked.")

    # mypy: the loop above guarantees these are non-None positive floats.
    assert entry_price is not None and stop_loss is not None
    assert take_profit is not None

    if not (0 < request.max_risk_pct <= _MAX_RISK_PCT):
        return _blocked(
            f"max_risk_pct {request.max_risk_pct:.4f} must be > 0 and <= "
            f"{_MAX_RISK_PCT:.1f}. Draft blocked by risk cap."
        )

    if side == "BUY" and not (stop_loss < entry_price < take_profit):
        return _blocked(
            "BUY geometry check failed: require "
            f"stop_loss ({stop_loss}) < entry_price ({entry_price}) < "
            f"take_profit ({take_profit}). Draft blocked."
        )
    if side == "SELL" and not (take_profit < entry_price < stop_loss):
        return _blocked(
            "SELL geometry check failed: require "
            f"take_profit ({take_profit}) < entry_price ({entry_price}) < "
            f"stop_loss ({stop_loss}). Draft blocked."
        )

    now_utc = datetime.now(timezone.utc).isoformat()
    canonical_key = (
        f"alpaca-draft:{symbol}:{side}:{order_type}:{tif}"
        f":{request.quantity}:{request.notional}"
        f":{entry_price}:{stop_loss}:{take_profit}:{request.max_risk_pct}"
    )
    draft = AlpacaPaperOrderDraft(
        draft_id=f"paper-draft-{_short_hash(canonical_key)}",
        created_at=now_utc,
        symbol=symbol,
        side=side,  # type: ignore[arg-type]
        order_type=order_type,  # type: ignore[arg-type]
        time_in_force=tif,  # type: ignore[arg-type]
        quantity=request.quantity,
        notional=request.notional,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        max_risk_pct=request.max_risk_pct,
    )
    return AlpacaPaperOrderDraftResponse(
        valid=True,
        reason=(
            "All checks passed. Local paper order draft built for human review. "
            "Not submitted to Alpaca; no broker execution."
        ),
        draft=draft,
    )
