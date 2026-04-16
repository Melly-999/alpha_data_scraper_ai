from __future__ import annotations

from types import SimpleNamespace

from risk.risk_manager import RiskConfig, RiskContext, RiskManager
import mt5_trader
from mt5_trader import MT5AutoTrader


class FakeMT5:
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    TRADE_ACTION_DEAL = 1
    ORDER_TIME_GTC = 0
    ORDER_FILLING_IOC = 0
    TRADE_RETCODE_DONE = 10009

    def __init__(self) -> None:
        self.sent_requests: list[dict] = []

    def initialize(self) -> bool:
        return True

    def shutdown(self) -> None:
        return None

    def last_error(self) -> tuple[int, str]:
        return 0, "ok"

    def symbol_select(self, symbol: str, enabled: bool) -> bool:
        return bool(symbol and enabled)

    def symbol_info_tick(self, symbol: str):
        return SimpleNamespace(ask=1.1, bid=1.0998)

    def symbol_info(self, symbol: str):
        return SimpleNamespace(point=0.0001)

    def order_send(self, request: dict):
        self.sent_requests.append(request)
        return SimpleNamespace(retcode=self.TRADE_RETCODE_DONE, order=1, deal=2)


def test_mt5_trader_blocks_when_risk_validation_fails(monkeypatch) -> None:
    fake_mt5 = FakeMT5()
    monkeypatch.setattr(mt5_trader, "mt5_api", fake_mt5)
    risk = RiskManager(
        ctx=RiskContext(balance=10_000.0, open_positions=0, daily_pnl_pct=0.0),
        risk_config=RiskConfig(min_rr=10.0),
    )
    trader = MT5AutoTrader(
        symbol="EURUSD",
        enabled=True,
        dry_run=False,
        sl_points=200,
        tp_points=300,
        risk_manager=risk,
    )

    result = trader.maybe_execute(signal="BUY", confidence=80)

    assert result["status"] == "risk_blocked"
    assert result["validation"]["status"] == "BLOCKED_LOW_RISK_REWARD"
    assert fake_mt5.sent_requests == []


def test_mt5_trader_uses_risk_lot_size_in_dry_run(monkeypatch) -> None:
    fake_mt5 = FakeMT5()
    monkeypatch.setattr(mt5_trader, "mt5_api", fake_mt5)
    risk = RiskManager(
        ctx=RiskContext(balance=10_000.0, open_positions=0, daily_pnl_pct=0.0),
        risk_config=RiskConfig(
            max_risk_per_trade_pct=1.0,
            min_rr=1.2,
            max_position_size_lots=0.5,
            stop_loss_pips=20.0,
            pip_value_per_lot=10.0,
        ),
    )
    trader = MT5AutoTrader(
        symbol="EURUSD",
        enabled=True,
        dry_run=True,
        volume=0.01,
        sl_points=200,
        tp_points=300,
        risk_manager=risk,
    )

    result = trader.maybe_execute(signal="BUY", confidence=80)

    assert result["status"] == "dry_run"
    assert result["request"]["volume"] == 0.5
