"""Registry tests for optional IBKR real read-only client wiring."""

from __future__ import annotations

from typing import Any, Mapping

from brokers.ibkr_config import IBKRPaperConfig


class _FakeRegistryClient:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    connected: bool = True

    def __init__(self, config: IBKRPaperConfig) -> None:
        self.config = config

    def account_snapshot(self) -> Mapping[str, Any]:
        return {
            "currency": "USD",
            "cash": 10.0,
            "equity": 20.0,
            "buying_power": 30.0,
            "account_id": "SHOULD_NOT_SURFACE",
        }

    def positions(self) -> list[Mapping[str, Any]]:
        return [
            {
                "symbol": "AAPL",
                "quantity": 1,
                "average_price": 100.0,
                "account_id": "SHOULD_NOT_SURFACE",
                "order_id": "SHOULD_NOT_SURFACE",
            }
        ]


def _clear_ibkr_env(monkeypatch) -> None:
    for name in (
        "IBKR_PAPER_READONLY_ENABLED",
        "IBKR_PAPER_HOST",
        "IBKR_PAPER_PORT",
        "IBKR_PAPER_CLIENT_ID",
        "IBKR_PAPER_TIMEOUT_S",
    ):
        monkeypatch.delenv(name, raising=False)


def test_env_disabled_registry_behavior_unchanged(monkeypatch) -> None:
    _clear_ibkr_env(monkeypatch)

    from brokers.registry import create_default_registry
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    registry = create_default_registry()
    adapter = registry.get("ibkr-paper")

    assert set(registry.list_adapter_ids()) == {"safe-disconnected", "ibkr-paper"}
    assert registry.default_adapter_id == "safe-disconnected"
    assert isinstance(registry.get_default(), SafeDisconnectedBrokerAdapter)
    assert adapter.has_client is False
    assert adapter.status()["connected"] is False


def test_env_enabled_wires_mocked_readonly_client(monkeypatch) -> None:
    _clear_ibkr_env(monkeypatch)
    monkeypatch.setenv("IBKR_PAPER_READONLY_ENABLED", "true")
    monkeypatch.setenv("IBKR_PAPER_PORT", "4002")
    monkeypatch.setenv("IBKR_PAPER_CLIENT_ID", "404")

    import brokers.registry as registry_module

    monkeypatch.setattr(
        registry_module,
        "IBKRPaperReadOnlyClient",
        _FakeRegistryClient,
    )

    registry = registry_module.create_default_registry()
    adapter = registry.get("ibkr-paper")
    status = adapter.status()
    account = adapter.account_snapshot()
    positions = adapter.positions()

    assert registry.default_adapter_id == "safe-disconnected"
    assert adapter.has_client is True
    assert adapter.config.enabled is True
    assert adapter.config.port == 4002
    assert adapter.config.client_id == 404
    assert status["connected"] is True
    assert status["read_only"] is True
    assert status["execution_enabled"] is False
    assert status["live_orders_blocked"] is True
    assert account["cash"] == 10.0
    assert "account_id" not in account
    assert len(positions) == 1
    assert "account_id" not in positions[0]
    assert "order_id" not in positions[0]


def test_env_enabled_failing_factory_falls_back_safely(monkeypatch) -> None:
    _clear_ibkr_env(monkeypatch)
    monkeypatch.setenv("IBKR_PAPER_READONLY_ENABLED", "true")

    import brokers.registry as registry_module

    def failing_factory(*args: object, **kwargs: object) -> object:
        raise RuntimeError("simulated factory failure")

    monkeypatch.setattr(
        registry_module,
        "IBKRPaperReadOnlyClient",
        failing_factory,
    )

    registry = registry_module.create_default_registry()
    adapter = registry.get("ibkr-paper")

    assert registry.default_adapter_id == "safe-disconnected"
    assert adapter.has_client is False
    assert adapter.status()["connected"] is False
    assert adapter.account_snapshot()["cash"] == 0.0
    assert adapter.positions() == []


def test_adapter_surface_remains_clean_when_registry_client_enabled(
    monkeypatch,
) -> None:
    _clear_ibkr_env(monkeypatch)
    monkeypatch.setenv("IBKR_PAPER_READONLY_ENABLED", "true")

    import brokers.registry as registry_module

    monkeypatch.setattr(
        registry_module,
        "IBKRPaperReadOnlyClient",
        _FakeRegistryClient,
    )
    adapter = registry_module.create_default_registry().get("ibkr-paper")

    forbidden = {
        "place_order",
        "cancel_order",
        "modify_order",
        "execute",
        "submit_order",
        "buy",
        "sell",
        "placeOrder",
        "cancelOrder",
        "broker_execute",
        "connect",
        "disconnect",
    }
    leaked = sorted((set(dir(adapter)) | set(dir(type(adapter)))) & forbidden)
    assert not leaked
