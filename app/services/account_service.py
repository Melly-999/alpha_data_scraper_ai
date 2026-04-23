from __future__ import annotations

from app.schemas.dashboard import AccountOverview
from app.schemas.order import OrderRow
from app.schemas.position import PositionSummary
from app.services.cache import TTLCache
from app.services.mt5_read_adapter import MT5ReadAdapter


class AccountService:
    def __init__(self, *, adapter: MT5ReadAdapter) -> None:
        self._adapter = adapter
        self._fallback = True
        self._account_cache: TTLCache[AccountOverview] = TTLCache(ttl_seconds=2)
        self._open_positions_cache: TTLCache[list[PositionSummary]] = TTLCache(
            ttl_seconds=2
        )
        self._history_cache: TTLCache[list[PositionSummary]] = TTLCache(ttl_seconds=15)
        self._orders_cache: TTLCache[list[OrderRow]] = TTLCache(ttl_seconds=5)

    @property
    def fallback_mode(self) -> bool:
        return self._fallback

    def get_account_overview(self) -> AccountOverview:
        envelope = self._account_cache.get_or_set(self._load_account_overview)
        return envelope.value

    def get_open_positions(self) -> list[PositionSummary]:
        envelope = self._open_positions_cache.get_or_set(self._load_open_positions)
        return envelope.value

    def get_position_history(self) -> list[PositionSummary]:
        envelope = self._history_cache.get_or_set(self._load_position_history)
        return envelope.value

    def get_orders(self) -> list[OrderRow]:
        envelope = self._orders_cache.get_or_set(self._load_orders)
        return envelope.value

    def clear_cache(self) -> None:
        self._account_cache.clear()
        self._open_positions_cache.clear()
        self._history_cache.clear()
        self._orders_cache.clear()

    def _load_account_overview(self) -> AccountOverview:
        snapshot = (
            self._adapter.read_account_overview()
            or self._adapter.fallback_account_overview()
        )
        self._fallback = snapshot.source != "mt5"
        return AccountOverview.model_validate(snapshot.payload)

    def _load_open_positions(self) -> list[PositionSummary]:
        snapshot = (
            self._adapter.read_open_positions()
            or self._adapter.fallback_open_positions()
        )
        self._fallback = snapshot.source != "mt5"
        return [PositionSummary.model_validate(item) for item in snapshot.payload]

    def _load_position_history(self) -> list[PositionSummary]:
        snapshot = (
            self._adapter.read_position_history()
            or self._adapter.fallback_position_history()
        )
        self._fallback = snapshot.source != "mt5"
        rows = [PositionSummary.model_validate(item) for item in snapshot.payload]
        return rows[:25]

    def _load_orders(self) -> list[OrderRow]:
        snapshot = self._adapter.read_orders() or self._adapter.fallback_orders()
        self._fallback = snapshot.source != "mt5"
        rows = [OrderRow.model_validate(item) for item in snapshot.payload]
        return rows[:25]
