from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any


@dataclass
class BrokerOrder:
    symbol: str
    side: str
    volume: float
    sl: float | None = None
    tp: float | None = None
    price: float | None = None
    comment: str = ""


@dataclass
class BrokerPosition:
    symbol: str
    side: str
    volume: float
    price_open: float
    price_current: float
    profit: float = 0.0
    sl: float | None = None
    tp: float | None = None
    ticket: str | int | None = None


@dataclass
class BrokerAccountInfo:
    balance: float
    equity: float
    profit: float = 0.0
    margin: float = 0.0
    free_margin: float = 0.0
    currency: str = "USD"


class BrokerAdapter(Protocol):
    name: str

    def connect(self) -> bool: ...
    def disconnect(self) -> None: ...
    def get_account_info(self) -> BrokerAccountInfo | None: ...
    def get_positions(self) -> list[BrokerPosition]: ...
    def place_order(self, order: BrokerOrder) -> dict[str, Any]: ...
    def get_latest_price(self, symbol: str) -> float | None: ...
