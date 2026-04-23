from __future__ import annotations

from app.schemas.dashboard import AccountOverview
from app.schemas.order import OrderRow
from app.schemas.position import PositionSummary
from app.services.fixture_data import (
    prototype_account,
    prototype_orders,
    prototype_positions_history,
    prototype_positions_open,
)


class AccountService:
    def __init__(self) -> None:
        self._fallback = True

    @property
    def fallback_mode(self) -> bool:
        return self._fallback

    def get_account_overview(self) -> AccountOverview:
        return AccountOverview.model_validate(prototype_account())

    def get_open_positions(self) -> list[PositionSummary]:
        return [
            PositionSummary.model_validate(item) for item in prototype_positions_open()
        ]

    def get_position_history(self) -> list[PositionSummary]:
        return [
            PositionSummary.model_validate(item)
            for item in prototype_positions_history()
        ]

    def get_orders(self) -> list[OrderRow]:
        return [OrderRow.model_validate(item) for item in prototype_orders()]
