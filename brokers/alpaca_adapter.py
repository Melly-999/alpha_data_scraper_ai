from __future__ import annotations

from typing import Any

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from brokers.base import BrokerAdapter, BrokerOrder


class AlpacaBrokerAdapter(BrokerAdapter):
    name = "alpaca"

    def __init__(self, config: dict[str, Any]):
        key = config.get("alpaca_key")
        secret = config.get("alpaca_secret")
        paper = config.get("alpaca_paper", True)

        self.client = TradingClient(key, secret, paper=paper)

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        return None

    def place_order(self, order: BrokerOrder) -> dict[str, Any]:
        request = MarketOrderRequest(
            symbol=order.symbol,
            qty=order.volume,
            side=OrderSide.BUY if order.side == "BUY" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )

        submitted = self.client.submit_order(order_data=request)

        return {
            "status": "submitted",
            "id": str(submitted.id),
        }
