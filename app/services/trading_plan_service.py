"""Read-only Daily Trading Plan preview service.

This service produces a *display-only* planning context for the Terminal V1
dashboard. It is **not** a trade signal, **not** an order, and **not** a
recommendation to execute. It performs zero IO:

* No MT5 calls.
* No broker calls.
* No live market data fetches.
* No order placement.
* No position sizing for execution (the schema deliberately omits
  quantity / lot / sl / tp fields so the response cannot be misread as an
  order ticket).

The plan items are static and deterministic so tests can assert on shape
without flakiness. The ``generated_at`` timestamp is the only field that
changes per call.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.schemas.terminal import TradingPlanItem, TradingPlanResponse


# Module-level static plan. Editable as a content-only change by an analyst;
# no code change required. Keep entries terse and observation-shaped — never
# imperative ("BUY X") and never with execution parameters.
_DEFAULT_PLAN_ITEMS: tuple[TradingPlanItem, ...] = (
    TradingPlanItem(
        instrument="EURUSD",
        bias="neutral",
        setup_quality="medium",
        risk_tier="low",
        no_trade_condition=(
            "No trade if price is within 10 pips of the prior daily high/low "
            "or during the first 15 minutes after London open."
        ),
        setup_area="1.0820 – 1.0865 daily range",
        notes=(
            "Range-bound between London pivots. Wait for a clean rejection "
            "before forming a directional view."
        ),
    ),
    TradingPlanItem(
        instrument="GBPUSD",
        bias="bearish",
        setup_quality="medium",
        risk_tier="medium",
        no_trade_condition=(
            "Skip if UK CPI prints within +/- 60 minutes of the watch window "
            "or if the H1 ATR doubles above its 20-period average."
        ),
        setup_area="1.2710 supply zone retest",
        notes=(
            "Lower-high structure on H4. Plan looks for confirmation only; "
            "no anticipatory action."
        ),
    ),
    TradingPlanItem(
        instrument="XAUUSD",
        bias="wait",
        setup_quality="low",
        risk_tier="high",
        no_trade_condition=(
            "No engagement during NY session unless realised volatility "
            "compresses below the 20-day median."
        ),
        setup_area="2330 – 2360 chop band",
        notes=(
            "Macro headline risk is elevated. Default posture is to stand "
            "aside and observe."
        ),
    ),
    TradingPlanItem(
        instrument="US500",
        bias="bullish",
        setup_quality="high",
        risk_tier="low",
        no_trade_condition=(
            "Skip if VIX gaps above 20 at the cash open or if the rolling "
            "5-day breadth turns negative intraday."
        ),
        setup_area="Prior swing-low retest near 5180",
        notes=(
            "Higher-low structure on D1; the plan tracks pullbacks only — "
            "no breakout chasing."
        ),
    ),
)


class TradingPlanService:
    """Generate the static read-only Daily Trading Plan preview."""

    def get_plan(self) -> TradingPlanResponse:
        return TradingPlanResponse(
            items=list(_DEFAULT_PLAN_ITEMS),
            generated_at=datetime.now(timezone.utc),
        )
