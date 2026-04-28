"""Tests for the safety-first IBKR paper adapter.

These tests must pass without ``ib_insync`` installed and without a
real TWS / IB Gateway running. CI uses ``requirements-ci.txt`` which
intentionally excludes ``ib_insync``.
"""

from __future__ import annotations

import pytest

from brokers.adapter_models import ExecutionDecision
from brokers.ibkr_paper import (
    IBKRPaperAdapter,
    IBKRPaperConfig,
    LIVE_PORTS,
    PAPER_PORTS,
)
from brokers.paper_factory import (
    get_paper_broker_adapter,
    normalise_name,
)


@pytest.fixture(autouse=True)
def _clear_ibkr_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in (
        "IBKR_ENABLED",
        "IBKR_MODE",
        "IBKR_HOST",
        "IBKR_PORT",
        "IBKR_CLIENT_ID",
        "IBKR_ACCOUNT",
        "IBKR_READ_ONLY",
        "IBKR_ALLOW_PAPER_ORDERS",
        "IBKR_ALLOW_LIVE_ORDERS",
        "IBKR_MAX_ORDER_VALUE",
        "IBKR_MAX_POSITION_VALUE",
        "BROKER_ADAPTER",
    ):
        monkeypatch.delenv(var, raising=False)


def _decision() -> ExecutionDecision:
    return ExecutionDecision(
        decision_id="d-1",
        signal_id="s-1",
        symbol="AAPL",
        direction="BUY",
        confidence=72.0,
        reason="unit-test",
        metadata={"source": "pytest"},
    )


# ---------------------------------------------------------------------------
# Defaults & lifecycle
# ---------------------------------------------------------------------------


def test_adapter_initialises_with_safe_defaults() -> None:
    adapter = IBKRPaperAdapter()
    assert adapter.config.enabled is False
    assert adapter.config.mode == "paper"
    assert adapter.config.host == "127.0.0.1"
    assert adapter.config.port == 7497
    assert adapter.config.read_only is True
    assert adapter.supports_live_orders() is False
    assert 7497 in PAPER_PORTS and 4002 in PAPER_PORTS
    assert 7496 in LIVE_PORTS and 4001 in LIVE_PORTS


def test_health_is_disabled_when_adapter_disabled() -> None:
    adapter = IBKRPaperAdapter()
    health = adapter.connect()
    assert health.connected is False
    assert health.mode == "disabled"
    assert health.status == "disabled"
    assert health.supports_live_orders is False


def test_disconnect_is_safe_without_connection() -> None:
    adapter = IBKRPaperAdapter()
    # Must not raise even though connect() was never called successfully.
    adapter.disconnect()


# ---------------------------------------------------------------------------
# Optional dependency / TWS unavailable
# ---------------------------------------------------------------------------


def test_missing_dependency_returns_disconnected_health(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("brokers.ibkr_paper._HAS_IB_INSYNC", False)
    adapter = IBKRPaperAdapter(
        config=IBKRPaperConfig(enabled=True, mode="paper", port=7497)
    )
    health = adapter.connect()
    assert health.connected is False
    assert health.status == "missing_dependency"
    assert (health.last_error or "").startswith("missing_dependency")


def test_app_safe_to_import_without_ib_insync() -> None:
    # The fact that we can import these modules at all is the smoke test;
    # CI does not install ``ib_insync``.
    import brokers.ibkr_paper as mod
    import brokers.paper_factory as factory

    assert hasattr(mod, "IBKRPaperAdapter")
    assert callable(factory.get_paper_broker_adapter)


# ---------------------------------------------------------------------------
# Live mode / live ports must fail closed
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("port", sorted(LIVE_PORTS))
def test_live_port_is_blocked_by_default(
    monkeypatch: pytest.MonkeyPatch, port: int
) -> None:
    monkeypatch.setattr("brokers.ibkr_paper._HAS_IB_INSYNC", True)
    adapter = IBKRPaperAdapter(
        config=IBKRPaperConfig(enabled=True, mode="paper", port=port)
    )
    health = adapter.connect()
    assert health.connected is False
    assert health.status == "live_blocked"
    assert "live_port_blocked" in (health.last_error or "")


def test_live_mode_is_blocked_even_if_paper_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("brokers.ibkr_paper._HAS_IB_INSYNC", True)
    adapter = IBKRPaperAdapter(
        config=IBKRPaperConfig(enabled=True, mode="live", port=7497)
    )
    health = adapter.connect()
    assert health.connected is False
    assert health.status == "live_blocked"
    assert "live_mode_blocked" in (health.last_error or "")


def test_allow_live_orders_still_blocked_in_v1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("brokers.ibkr_paper._HAS_IB_INSYNC", True)
    adapter = IBKRPaperAdapter(
        config=IBKRPaperConfig(
            enabled=True, mode="paper", port=7497, allow_live_orders=True
        )
    )
    health = adapter.connect()
    assert health.connected is False
    assert "live_orders_disabled_in_v1" in (health.last_error or "")
    assert adapter.supports_live_orders() is False


# ---------------------------------------------------------------------------
# Account snapshot
# ---------------------------------------------------------------------------


def test_account_snapshot_safe_when_disconnected() -> None:
    adapter = IBKRPaperAdapter(
        config=IBKRPaperConfig(enabled=True, account="DU1234567")
    )
    snapshot = adapter.account_snapshot()
    assert snapshot.connected is False
    assert snapshot.account == "DU1234567"
    assert snapshot.net_liquidation == 0.0
    assert snapshot.last_error  # should explain why


# ---------------------------------------------------------------------------
# Dry-run reports
# ---------------------------------------------------------------------------


def test_dry_run_report_when_disabled_is_blocked() -> None:
    adapter = IBKRPaperAdapter()  # enabled=False
    report = adapter.submit_dry_run_report(_decision())
    assert report.dry_run is True
    assert report.accepted is False
    assert report.broker == "ibkr_paper"
    assert report.reason == "adapter_disabled"


def test_dry_run_report_when_paper_is_accepted() -> None:
    adapter = IBKRPaperAdapter(
        config=IBKRPaperConfig(enabled=True, mode="paper", port=7497)
    )
    report = adapter.submit_dry_run_report(_decision())
    assert report.accepted is True
    assert report.symbol == "AAPL"
    assert report.direction == "BUY"
    assert report.confidence == 72.0
    assert report.payload["mode"] == "paper"
    assert report.payload["decision_metadata"] == {"source": "pytest"}


def test_dry_run_report_blocks_live_port() -> None:
    adapter = IBKRPaperAdapter(
        config=IBKRPaperConfig(enabled=True, mode="paper", port=7496)
    )
    report = adapter.submit_dry_run_report(_decision())
    assert report.accepted is False
    assert "live_port_blocked" in (report.reason or "")


def test_paper_bracket_order_always_refused() -> None:
    adapter = IBKRPaperAdapter(
        config=IBKRPaperConfig(
            enabled=True,
            mode="paper",
            port=7497,
            allow_paper_orders=False,
        )
    )
    report = adapter.place_paper_bracket_order(_decision())
    assert report.accepted is False
    assert report.dry_run is True
    assert "paper_orders_disabled" in (report.reason or "")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def test_factory_returns_ibkr_paper_for_known_names() -> None:
    a1 = get_paper_broker_adapter("ibkr-paper")
    a2 = get_paper_broker_adapter("ibkr_paper")
    assert isinstance(a1, IBKRPaperAdapter)
    assert isinstance(a2, IBKRPaperAdapter)


def test_factory_falls_back_to_safe_disabled_adapter() -> None:
    adapter = get_paper_broker_adapter("totally-unknown")
    health = adapter.health()
    assert health.connected is False
    assert health.mode == "disabled"
    assert health.supports_live_orders is False


def test_factory_uses_env_when_no_name_passed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BROKER_ADAPTER", "ibkr-paper")
    adapter = get_paper_broker_adapter()
    assert isinstance(adapter, IBKRPaperAdapter)


def test_normalise_name_handles_separators() -> None:
    assert normalise_name("IBKR_PAPER") == "ibkr-paper"
    assert normalise_name(" ibkr-paper ") == "ibkr-paper"
    assert normalise_name(None) == ""


def test_config_defaults_keep_live_blocked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cfg = IBKRPaperConfig.from_env()
    assert cfg.enabled is False
    assert cfg.mode == "paper"
    assert cfg.port == 7497
    assert cfg.allow_live_orders is False
    assert cfg.allow_paper_orders is False
