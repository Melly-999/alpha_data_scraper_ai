from __future__ import annotations

from app.schemas.mt5 import MT5Status
from app.services.fixture_data import prototype_mt5_status


class MT5Service:
    def __init__(self, *, mt5_available: bool) -> None:
        self._mt5_available = mt5_available

    @property
    def fallback_mode(self) -> bool:
        return True

    def get_status(self) -> MT5Status:
        data = prototype_mt5_status()
        data["connected"] = False
        data["fallback"] = not self._mt5_available
        return MT5Status.model_validate(data)
