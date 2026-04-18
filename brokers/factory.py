from __future__ import annotations

from typing import Any

from brokers.base import BrokerAdapter
from brokers.mt5_adapter import MT5BrokerAdapter
from brokers.xtb_adapter import XTBBrokerAdapter
from brokers.ibkr_adapter import IBKRBrokerAdapter
from brokers.alpaca_adapter import AlpacaBrokerAdapter
from brokers.binance_adapter import BinanceBrokerAdapter


def create_broker(name: str, config: dict[str, Any]) -> BrokerAdapter:
    key = (name or "mt5").lower()
    if key == "mt5":
        return MT5BrokerAdapter(config)
    if key == "xtb":
        return XTBBrokerAdapter(config)
    if key == "ibkr":
        return IBKRBrokerAdapter(config)
    if key == "alpaca":
        return AlpacaBrokerAdapter(config)  # type: ignore[abstract]
    if key == "binance":
        return BinanceBrokerAdapter(config)
    raise ValueError(f"Unsupported broker: {name}")
