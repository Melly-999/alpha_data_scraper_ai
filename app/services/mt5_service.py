from __future__ import annotations

from app.schemas.mt5 import MT5Status
from app.services.cache import TTLCache
from app.services.mt5_read_adapter import MT5ReadAdapter


class MT5Service:
    def __init__(self, *, adapter: MT5ReadAdapter, tracked_symbols: list[str]) -> None:
        self._adapter = adapter
        self._tracked_symbols = tracked_symbols
        self._cache: TTLCache[MT5Status] = TTLCache(ttl_seconds=3)

    def get_status(self) -> MT5Status:
        envelope = self._cache.get_or_set(self._load_status)
        return envelope.value.model_copy(
            update={"cache_age_seconds": envelope.cache_age_seconds}
        )

    def clear_cache(self) -> None:
        self._cache.clear()

    def _load_status(self) -> MT5Status:
        snapshot = (
            self._adapter.read_status(self._tracked_symbols)
            or self._adapter.fallback_status()
        )
        return MT5Status.model_validate(snapshot.payload)
