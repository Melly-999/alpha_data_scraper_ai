"""ALPACA-PAPER-ORDER-PREVIEW-003 — Service for GET /api/alpaca-paper/order-preview.

Deterministic, local-only Alpaca paper order preview generator.

This service:
- Validates trade geometry and risk parameters.
- Returns a blocked response (allowed=false) on validation failure.
- Returns an allowed response (allowed=true) with a synthetic order on success.
- Never calls any broker, network service, or database.
- Never reads environment variables or external config.
- Never submits, places, routes, or executes any order.
- Never returns account_id, broker_order_id, execution_id, trade_id,
  secret, token, api_key, or password.

Safety invariants maintained at every point:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  execution_enabled      = False
  submitted              = False
  max_risk_pct           <= 1.0
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from app.schemas.alpaca_paper_order_preview import (
    AlpacaPaperOrderPreviewOrder,
    AlpacaPaperOrderPreviewResponse,
)

# ---------------------------------------------------------------------------
# Safety constants — never mutated at runtime.
# ---------------------------------------------------------------------------

_MAX_RISK_PCT: float = 1.0


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _short_hash(value: str) -> str:
    """Return a 12-char hex prefix of SHA-256(value).

    Used to generate deterministic paper-scoped IDs from canonical input keys.
    The result is NOT a broker order ID, fill ID, or execution ID.
    """
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def _blocked(reason: str) -> AlpacaPaperOrderPreviewResponse:
    """Return a safe blocked response with ``order=None``.

    All six safety flags, ``submitted=False``, ``label``, and ``broker`` are
    always set.  This is an HTTP 200 response — it is not an error.
    """
    return AlpacaPaperOrderPreviewResponse(
        allowed=False,
        reason=reason,
        order=None,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_alpaca_paper_order_preview(
    *,
    symbol: str,
    side: str,
    quantity: float,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    max_risk_pct: float,
) -> AlpacaPaperOrderPreviewResponse:
    """Generate a deterministic Alpaca paper-only order preview.

    Validation failures return ``allowed=False`` with a descriptive reason
    (HTTP 200).  No exception is raised for invalid geometry or risk values.

    This function never calls any broker, network service, or database.
    It never submits, places, routes, or executes any order.
    All returned IDs use a ``paper-alpaca-`` / ``paper-alpaca-run-`` prefix.

    Args:
        symbol:       Trading symbol (e.g. "AAPL").
        side:         Direction — "BUY" or "SELL".
        quantity:     Trade size (positive float).
        entry_price:  Simulated entry price (positive float).
        stop_loss:    Simulated stop-loss level (positive float).
        take_profit:  Simulated take-profit level (positive float).
        max_risk_pct: Requested risk per trade.  Must not exceed 1.0.

    Returns:
        AlpacaPaperOrderPreviewResponse with allowed=True and an order on
        success, or allowed=False with order=None on validation failure.
    """
    # --- 1. Risk cap ---
    if max_risk_pct > _MAX_RISK_PCT:
        return _blocked(
            f"max_risk_pct {max_risk_pct:.4f} exceeds the maximum permitted "
            f"per-trade risk of {_MAX_RISK_PCT:.1f}. "
            "Alpaca paper order preview blocked by risk cap."
        )

    # --- 2. Price geometry ---
    if side == "BUY":
        if not (stop_loss < entry_price < take_profit):
            return _blocked(
                "Risk geometry check failed for BUY: "
                f"stop_loss ({stop_loss}) must be less than "
                f"entry_price ({entry_price}) which must be less than "
                f"take_profit ({take_profit}). "
                "Alpaca paper order preview blocked — invalid long geometry."
            )
    elif side == "SELL":
        if not (take_profit < entry_price < stop_loss):
            return _blocked(
                "Risk geometry check failed for SELL: "
                f"take_profit ({take_profit}) must be less than "
                f"entry_price ({entry_price}) which must be less than "
                f"stop_loss ({stop_loss}). "
                "Alpaca paper order preview blocked — invalid short geometry."
            )
    else:
        return _blocked(f"Unknown side '{side}'. Must be BUY or SELL. Preview blocked.")

    # --- 3. All checks passed — build synthetic Alpaca paper order preview ---

    now_utc = datetime.now(timezone.utc).isoformat()

    canonical_key = (
        f"alpaca:{symbol}:{side}:{entry_price}:{stop_loss}:{take_profit}"
        f":{quantity}:{max_risk_pct}"
    )
    h = _short_hash(canonical_key)

    paper_order_id = f"paper-alpaca-{h}"
    run_id = f"paper-alpaca-run-{h}"

    order = AlpacaPaperOrderPreviewOrder(
        paper_order_id=paper_order_id,
        run_id=run_id,
        created_at=now_utc,
        symbol=symbol,
        direction=side,  # type: ignore[arg-type]
        quantity=quantity,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        max_risk_pct=max_risk_pct,
        status="preview",
    )

    return AlpacaPaperOrderPreviewResponse(
        allowed=True,
        reason=(
            "All risk checks passed. Alpaca paper order preview approved for "
            "display. Paper-only, not submitted, dry-run, no broker execution, "
            "human review required."
        ),
        order=order,
    )
