from __future__ import annotations

from app.schemas.market import MarketItem

_FALLBACK_ITEMS: tuple[MarketItem, ...] = (
    MarketItem(
        symbol="EURUSD", price=1.0784, change_pct=0.18, signal="HOLD", confidence=61
    ),
    MarketItem(
        symbol="GBPUSD", price=1.2532, change_pct=-0.11, signal="WATCH", confidence=55
    ),
    MarketItem(
        symbol="USDJPY", price=156.42, change_pct=0.24, signal="HOLD", confidence=58
    ),
    MarketItem(
        symbol="XAUUSD", price=2318.8, change_pct=-0.32, signal="WATCH", confidence=63
    ),
)


class MarketOverviewService:
    def get_overview(self) -> list[MarketItem]:
        return list(_FALLBACK_ITEMS)
