from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.schemas.common import BlockedReason
from app.services.account_service import AccountService
from app.services.analytics_service import AnalyticsService
from app.services.cache import TTLCache
from app.services.log_service import LogService
from app.services.mt5_read_adapter import AdapterSnapshot, MT5ReadAdapter
from app.services.mt5_service import MT5Service
from app.services.risk_service import RiskService
from app.services.signal_service import ServiceDependencies, SignalService


def build_services() -> tuple[RiskService, SignalService]:
    log_service = LogService()
    risk_service = RiskService(Path("config.json"), log_service)
    adapter = MT5ReadAdapter()
    signal_service = SignalService(
        risk_service=risk_service,
        log_service=log_service,
        account_service=AccountService(adapter=adapter),
        dependencies=ServiceDependencies(
            mt5_available=False,
            claude_available=False,
            news_available=False,
        ),
        tracked_symbols=["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
    )
    return risk_service, signal_service


def test_signal_adapter_maps_blocked_reasons_and_bounds() -> None:
    _, signal_service = build_services()

    signals = signal_service.list_signals()
    by_id = {signal.id: signal for signal in signals}

    assert by_id["sig-003"].blocked_reason == BlockedReason.LOW_CONFIDENCE
    assert by_id["sig-004"].blocked is True
    assert by_id["sig-004"].blocked_reason is not None
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


def test_account_service_switches_to_read_only_adapter() -> None:
    class FakeAdapter(MT5ReadAdapter):
        def read_account_overview(self) -> AdapterSnapshot | None:
            return AdapterSnapshot(
                payload={
                    "balance": 1000.0,
                    "equity": 1010.0,
                    "margin": 12.0,
                    "free_margin": 998.0,
                    "margin_level": 400.0,
                    "drawdown": 1.0,
                    "daily_pnl": 10.0,
                    "daily_pnl_pct": 1.0,
                    "open_positions": 1,
                    "today_trades": 2,
                },
                source="mt5",
                connected=True,
                latency_ms=4,
            )

    service = AccountService(adapter=FakeAdapter())
    overview = service.get_account_overview()

    assert service.fallback_mode is False
    assert overview.balance == 1000.0
    assert overview.open_positions == 1


def test_ttl_cache_reuses_loaded_value_until_cleared() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=60)
    call_count = {"value": 0}

    def loader() -> int:
        call_count["value"] += 1
        return call_count["value"]

    first = cache.get_or_set(loader)
    second = cache.get_or_set(loader)
    cache.clear()
    third = cache.get_or_set(loader)

    assert first.value == 1
    assert second.value == 1
    assert second.cache_age_seconds >= 0
    assert third.value == 2


def test_signal_reasoning_includes_provenance_fields() -> None:
    _, signal_service = build_services()

    reasoning = signal_service.get_reasoning("sig-001")

    assert reasoning.provenance.signal_source
    assert reasoning.provenance.market_data_source
    assert reasoning.confidence_explainer is not None


def test_analytics_service_returns_read_only_metrics() -> None:
    service = AnalyticsService(default_symbol="EURUSD")

    summary = service.get_summary()

    assert summary.total_trades >= 0
    assert summary.source
    assert summary.highlights


def test_mt5_status_contract_matches_read_snapshot_source() -> None:
    class FakeAdapter(MT5ReadAdapter):
        def read_status(self, symbols: list[str]) -> AdapterSnapshot | None:
            return AdapterSnapshot(
                payload={
                    "connected": True,
                    "server": "Demo-Server",
                    "account_id": "123",
                    "account_name": "Read Only",
                    "broker": "Broker",
                    "currency": "USD",
                    "leverage": "1:100",
                    "last_heartbeat": datetime.now(timezone.utc).isoformat(),
                    "latency_ms": 5,
                    "symbols_loaded": len(symbols),
                    "orders_sync": True,
                    "positions_sync": True,
                    "build_version": "5.0.0",
                    "fallback": False,
                    "read_only": True,
                    "data_source": "mt5",
                    "terminal_path": "C:/MT5",
                    "cache_age_seconds": 0,
                    "refreshed_at": datetime.now(timezone.utc).isoformat(),
                    "connection_logs": [],
                },
                source="mt5",
                connected=True,
                latency_ms=5,
            )

    status = MT5Service(
        adapter=FakeAdapter(),
        tracked_symbols=["EURUSD", "GBPUSD"],
    ).get_status()

    assert status.fallback is False
    assert status.data_source == "mt5"
    assert status.read_only is True
