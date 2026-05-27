"""PAPER-RUN-API-001 — Service for GET /api/paper/run/preview.

Deterministic, local-only paper run preview generator.

This service:
- Validates trade geometry and risk parameters.
- Returns a blocked response (allowed=false) on validation failure.
- Returns an allowed response (allowed=true) with a synthetic paper_run on success.
- Never calls any broker, network service, or database.
- Never reads environment variables or external config.
- Never creates paper fills, positions, or live trades.
- Never returns account_id, broker_order_id, execution_id, trade_id,
  secret, token, api_key, or password.

Safety invariants maintained at every point:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  execution_enabled      = False
  max_risk_pct           <= 1.0
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from app.schemas.paper_run_preview import (
    PaperRunPreviewFill,
    PaperRunPreviewOrder,
    PaperRunPreviewPosition,
    PaperRunPreviewResponse,
    PaperRunPreviewRun,
)

# ---------------------------------------------------------------------------
# Safety constants — never mutated at runtime.
# ---------------------------------------------------------------------------

_MAX_RISK_PCT: float = 1.0
_MIN_CONFIDENCE: float = 0.0
_MAX_CONFIDENCE: float = 100.0


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _short_hash(value: str) -> str:
    """Return a 12-char hex prefix of SHA-256(value).

    Used to generate deterministic paper-scoped IDs from canonical input
    keys.  The result is NOT a broker order ID, fill ID, or execution ID.
    """
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def _blocked(reason: str) -> PaperRunPreviewResponse:
    """Return a safe blocked response with ``paper_run=None``.

    All six safety flags are always set in the returned model.
    This is an HTTP 200 response — it is not an error.
    """
    return PaperRunPreviewResponse(
        allowed=False,
        reason=reason,
        paper_run=None,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_paper_run_preview(
    *,
    symbol: str,
    side: str,
    quantity: float,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    confidence: float,
    max_risk_pct: float,
) -> PaperRunPreviewResponse:
    """Generate a deterministic paper-only run preview for the given params.

    Validation failures return ``allowed=False`` with a descriptive reason
    (HTTP 200).  No exception is raised for invalid geometry or risk values.

    This function never calls any broker, network service, or database.
    It never creates live orders, fills, positions, or paper trades.
    All returned IDs use a ``paper-*`` prefix to distinguish them from any
    live broker identifier.

    Args:
        symbol:       Trading symbol (e.g. "EURUSD").
        side:         Direction — "BUY" or "SELL".
        quantity:     Trade size (positive float).
        entry_price:  Simulated entry price (positive float).
        stop_loss:    Simulated stop-loss level (positive float).
        take_profit:  Simulated take-profit level (positive float).
        confidence:   Signal confidence score in [0.0, 100.0].
        max_risk_pct: Requested risk per trade.  Must not exceed 1.0.

    Returns:
        PaperRunPreviewResponse with allowed=True and a paper_run on success,
        or allowed=False with paper_run=None on validation failure.
    """
    # --- 1. Risk cap ---
    if max_risk_pct > _MAX_RISK_PCT:
        return _blocked(
            f"max_risk_pct {max_risk_pct:.4f} exceeds the maximum permitted "
            f"per-trade risk of {_MAX_RISK_PCT:.1f}. "
            "Paper run blocked by risk cap."
        )

    # --- 2. Confidence bounds ---
    if confidence < _MIN_CONFIDENCE or confidence > _MAX_CONFIDENCE:
        return _blocked(
            f"confidence {confidence:.1f} is out of range "
            f"[{_MIN_CONFIDENCE:.0f}, {_MAX_CONFIDENCE:.0f}]. "
            "Paper run blocked."
        )

    # --- 3. Price geometry ---
    if side == "BUY":
        # Long: stop_loss < entry_price < take_profit
        if not (stop_loss < entry_price < take_profit):
            return _blocked(
                "Risk geometry check failed for BUY: "
                f"stop_loss ({stop_loss}) must be less than "
                f"entry_price ({entry_price}) which must be less than "
                f"take_profit ({take_profit}). "
                "Paper run blocked — invalid long geometry."
            )
    elif side == "SELL":
        # Short: take_profit < entry_price < stop_loss
        if not (take_profit < entry_price < stop_loss):
            return _blocked(
                "Risk geometry check failed for SELL: "
                f"take_profit ({take_profit}) must be less than "
                f"entry_price ({entry_price}) which must be less than "
                f"stop_loss ({stop_loss}). "
                "Paper run blocked — invalid short geometry."
            )
    else:
        # Should not be reachable — the route validates side via Query pattern.
        return _blocked(
            f"Unknown side '{side}'. Must be BUY or SELL. Paper run blocked."
        )

    # --- 4. All checks passed — build synthetic paper run preview ---

    now_utc = datetime.now(timezone.utc).isoformat()

    # Deterministic hash key from canonical params (excluding timestamps).
    canonical_key = (
        f"{symbol}:{side}:{entry_price}:{stop_loss}:{take_profit}"
        f":{quantity}:{max_risk_pct}"
    )
    h = _short_hash(canonical_key)

    paper_order_id = f"paper-order-{h}"
    paper_fill_id = f"paper-fill-{h}"
    paper_position_id = f"paper-pos-{h}"
    run_id = f"paper-run-preview-{h}"

    direction: str = side  # "BUY" or "SELL"

    order = PaperRunPreviewOrder(
        paper_order_id=paper_order_id,
        created_at=now_utc,
        symbol=symbol,
        direction=direction,  # type: ignore[arg-type]
        quantity=quantity,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        max_risk_pct=max_risk_pct,
        status="open",
        rejection_reason=None,
    )

    fill = PaperRunPreviewFill(
        paper_fill_id=paper_fill_id,
        paper_order_ref=paper_order_id,
        fill_timestamp=now_utc,
        symbol=symbol,
        direction=direction,  # type: ignore[arg-type]
        fill_price=entry_price,
        quantity=quantity,
    )

    # Simulate a small favourable price move for display (0.01% of entry).
    # No live market data is consulted — purely cosmetic for the preview.
    pip_move = entry_price * 0.0001
    if direction == "BUY":
        current_price = round(entry_price + pip_move, 5)
        unrealized_pnl = round((current_price - entry_price) * quantity, 6)
    else:
        current_price = round(entry_price - pip_move, 5)
        unrealized_pnl = round((entry_price - current_price) * quantity, 6)

    position = PaperRunPreviewPosition(
        paper_position_id=paper_position_id,
        paper_order_ref=paper_order_id,
        opened_at=now_utc,
        closed_at=None,
        symbol=symbol,
        direction=direction,  # type: ignore[arg-type]
        quantity=quantity,
        entry_price=entry_price,
        current_price=current_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        unrealized_pnl=unrealized_pnl,
        max_risk_pct=max_risk_pct,
        status="open",
    )

    paper_run = PaperRunPreviewRun(
        run_id=run_id,
        started_at=now_utc,
        ended_at=None,
        total_signals=1,
        accepted_signals=1,
        rejected_signals=0,
        open_positions_count=1,
        closed_positions_count=0,
        max_risk_pct=max_risk_pct,
        orders=[order],
        fills=[fill],
        positions=[position],
    )

    return PaperRunPreviewResponse(
        allowed=True,
        reason=(
            "All risk checks passed. Paper run simulation approved for display. "
            "Paper-only, dry-run, no broker execution, human review required."
        ),
        paper_run=paper_run,
    )
