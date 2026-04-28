"""Tests for the safe broker adapter dataclass models."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

from brokers.adapter_models import (
    BrokerAccountSnapshot,
    BrokerExecutionReport,
    BrokerHealth,
    ExecutionDecision,
)


def test_broker_health_is_serialisable_dataclass() -> None:
    health = BrokerHealth(
        adapter="ibkr_paper",
        mode="paper",
        connected=False,
        host="127.0.0.1",
        port=7497,
        client_id=1,
        read_only=True,
        supports_live_orders=False,
    )
    assert is_dataclass(health)
    payload = asdict(health)
    assert payload["adapter"] == "ibkr_paper"
    assert payload["mode"] == "paper"
    assert payload["supports_live_orders"] is False
    assert payload["status"] == "ok"
    assert isinstance(payload["timestamp"], str) and payload["timestamp"]


def test_broker_account_snapshot_defaults_safe() -> None:
    snap = BrokerAccountSnapshot(adapter="ibkr_paper", connected=False)
    payload = asdict(snap)
    assert payload["connected"] is False
    assert payload["net_liquidation"] == 0.0
    assert payload["cash"] == 0.0
    assert payload["buying_power"] == 0.0
    assert payload["currency"] == "USD"


def test_broker_execution_report_is_dry_run_only() -> None:
    decision = ExecutionDecision(
        decision_id="d1",
        signal_id="s1",
        symbol="AAPL",
        direction="BUY",
        confidence=72.0,
    )
    report = BrokerExecutionReport(
        adapter="ibkr_paper",
        broker="ibkr_paper",
        dry_run=True,
        accepted=True,
        decision_id=decision.decision_id,
        signal_id=decision.signal_id,
        symbol=decision.symbol,
        direction=decision.direction,
        confidence=decision.confidence,
        reason="dry_run_ok",
    )
    assert report.dry_run is True
    assert asdict(report)["broker"] == "ibkr_paper"
