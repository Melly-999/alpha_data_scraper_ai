from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.schemas.common import BlockedReason
from app.services.account_service import AccountService
from app.services.log_service import LogService
from app.services.risk_service import RiskService
from app.services.signal_service import ServiceDependencies, SignalService


def build_services() -> tuple[RiskService, SignalService]:
    log_service = LogService()
    risk_service = RiskService(Path("config.json"), log_service)
    signal_service = SignalService(
        risk_service=risk_service,
        log_service=log_service,
        account_service=AccountService(),
        dependencies=ServiceDependencies(
            claude_available=False,
            news_available=False,
        ),
    )
    return risk_service, signal_service


def test_signal_adapter_maps_blocked_reasons_and_bounds() -> None:
    _, signal_service = build_services()

    signals = signal_service.list_signals()
    by_id = {signal.id: signal for signal in signals}

    assert by_id["sig-003"].blocked_reason == BlockedReason.LOW_CONFIDENCE
    assert by_id["sig-004"].blocked_reason == BlockedReason.COOLDOWN
    assert all(33 <= signal.confidence <= 85 for signal in signals)


def test_duplicate_signal_blocking_and_cooldown() -> None:
    risk_service, _ = build_services()
    now = datetime.now(timezone.utc)

    first = risk_service.evaluate_signal(
        signal_id="sig-live-1",
        symbol="EURUSD",
        direction="BUY",
        confidence=80,
        sl=1.0,
        tp=2.0,
        rr=2.0,
        timestamp=now,
        open_positions=0,
        register=True,
    )
    second = risk_service.evaluate_signal(
        signal_id="sig-live-2",
        symbol="EURUSD",
        direction="BUY",
        confidence=80,
        sl=1.0,
        tp=2.0,
        rr=2.0,
        timestamp=now + timedelta(seconds=30),
        open_positions=0,
        register=True,
    )

    assert first[0] is True
    assert second[0] is False
    assert second[1] == BlockedReason.COOLDOWN
    assert second[2] is not None


def test_emergency_stop_enforcement_in_risk_service() -> None:
    risk_service, _ = build_services()
    risk_service.trigger_emergency_stop()

    allowed, blocked_reason, _, _ = risk_service.evaluate_signal(
        signal_id="sig-stop",
        symbol="EURUSD",
        direction="BUY",
        confidence=80,
        sl=1.0,
        tp=2.0,
        rr=2.0,
        timestamp=datetime.now(timezone.utc),
        open_positions=0,
        register=False,
    )

    assert allowed is False
    assert blocked_reason == BlockedReason.EMERGENCY_STOP


def test_conservative_defaults_remain_disabled() -> None:
    risk_service, _ = build_services()
    config = risk_service.get_config()

    assert config.auto_trade is False
    assert config.dry_run is True
    assert config.max_risk_per_trade <= 1.0
    assert config.min_confidence >= 70
