"""IBKR-READ-001 tests for the optional real read-only IBKR client.

The client wrapper must stay import-safe, opt-in, localhost/paper-only,
and free of order/execution surface. All tests use fake sessions and
must never open a TWS/Gateway socket.
"""

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace
from typing import Any

from brokers.ibkr_config import IBKRPaperConfig
from brokers.ibkr_readonly_client import (
    IBKRPaperReadOnlyClient,
    ibkr_paper_config_from_env,
    ibkr_paper_readonly_enabled,
)

FORBIDDEN_METHOD_NAMES: tuple[str, ...] = (
    "place_order",
    "cancel_order",
    "modify_order",
    "execute",
    "submit_order",
    "buy",
    "sell",
    "placeOrder",
    "cancelOrder",
    "reqMktData",
    "reqPositions",
    "broker_execute",
)

FORBIDDEN_OUTPUT_KEYS: tuple[str, ...] = (
    "account_id",
    "account",
    "username",
    "password",
    "token",
    "secret",
    "api_key",
    "credential",
    "credentials",
    "order_id",
    "execution_id",
    "trade_id",
)


class _FakeIB:
    def __init__(self) -> None:
        self.connected = False
        self.connect_calls: list[dict[str, Any]] = []

    def connect(
        self,
        host: str,
        port: int,
        *,
        clientId: int,
        readonly: bool,
        timeout: float,
    ) -> None:
        self.connect_calls.append(
            {
                "host": host,
                "port": port,
                "clientId": clientId,
                "readonly": readonly,
                "timeout": timeout,
            }
        )
        self.connected = True

    def isConnected(self) -> bool:
        return self.connected

    def accountSummary(self) -> list[Any]:
        return [
            SimpleNamespace(
                tag="TotalCashValue",
                value="1234.50",
                currency="USD",
                account="DU_NOT_SURFACED",
            ),
            SimpleNamespace(
                tag="NetLiquidation",
                value="5678.90",
                currency="USD",
                account="DU_NOT_SURFACED",
            ),
            SimpleNamespace(
                tag="BuyingPower",
                value="9876.50",
                currency="USD",
                account="DU_NOT_SURFACED",
            ),
        ]

    def positions(self) -> list[Any]:
        return [
            SimpleNamespace(
                contract=SimpleNamespace(
                    symbol="AAPL",
                    currency="USD",
                    account_id="SHOULD_NOT_SURFACE",
                ),
                position=10,
                avgCost=150.25,
                account="DU_NOT_SURFACED",
                order_id="ORD_NOT_SURFACED",
            )
        ]


def _enabled_config(**overrides: object) -> IBKRPaperConfig:
    values: dict[str, object] = {"enabled": True}
    values.update(overrides)
    return IBKRPaperConfig(**values)  # type: ignore[arg-type]


def test_module_import_does_not_require_ib_insync() -> None:
    sys.modules.pop("brokers.ibkr_readonly_client", None)
    sys.modules.pop("ib_insync", None)

    before = set(sys.modules)
    module = importlib.import_module("brokers.ibkr_readonly_client")
    newly_imported = set(sys.modules) - before

    assert hasattr(module, "IBKRPaperReadOnlyClient")
    assert "ib_insync" not in newly_imported


def test_env_flag_defaults_disabled() -> None:
    assert ibkr_paper_readonly_enabled({}) is False
    assert ibkr_paper_config_from_env({}).enabled is False


def test_env_config_reads_harmless_values_only() -> None:
    cfg = ibkr_paper_config_from_env(
        {
            "IBKR_PAPER_READONLY_ENABLED": "true",
            "IBKR_PAPER_HOST": "localhost",
            "IBKR_PAPER_PORT": "4002",
            "IBKR_PAPER_CLIENT_ID": "202",
            "IBKR_PAPER_TIMEOUT_S": "2.5",
        }
    )
    assert cfg.enabled is True
    assert cfg.host == "localhost"
    assert cfg.port == 4002
    assert cfg.client_id == 202
    assert cfg.timeout_s == 2.5
    assert cfg.paper is True
    assert cfg.read_only is True


def test_missing_dependency_degrades_safely() -> None:
    client = IBKRPaperReadOnlyClient(
        config=_enabled_config(),
        module_loader=lambda name: (_ for _ in ()).throw(ImportError(name)),
    )
    assert client.is_connected() is False
    assert client.account_snapshot() is None
    assert client.positions() == []
    assert client.last_error == "missing_dependency"


def test_disabled_config_makes_no_session_attempt() -> None:
    calls = 0

    def factory() -> _FakeIB:
        nonlocal calls
        calls += 1
        return _FakeIB()

    client = IBKRPaperReadOnlyClient(config=IBKRPaperConfig(), ib_factory=factory)
    assert client.is_connected() is False
    assert calls == 0
    assert client.last_error == "disabled"


def test_non_local_host_is_blocked_without_network_attempt() -> None:
    calls = 0

    def factory() -> _FakeIB:
        nonlocal calls
        calls += 1
        return _FakeIB()

    client = IBKRPaperReadOnlyClient(
        config=_enabled_config(host="192.0.2.10"),
        ib_factory=factory,
    )
    assert client.is_connected() is False
    assert calls == 0
    assert client.last_error == "non_local_host_blocked"


def test_non_paper_port_is_blocked_without_network_attempt() -> None:
    calls = 0

    def factory() -> _FakeIB:
        nonlocal calls
        calls += 1
        return _FakeIB()

    client = IBKRPaperReadOnlyClient(
        config=_enabled_config(port=7496),
        ib_factory=factory,
    )
    assert client.is_connected() is False
    assert calls == 0
    assert client.last_error == "non_paper_port_blocked"


def test_fake_session_connects_readonly_to_local_paper_port() -> None:
    fake = _FakeIB()
    client = IBKRPaperReadOnlyClient(
        config=_enabled_config(port=7497, client_id=303, timeout_s=1.5),
        ib_factory=lambda: fake,
    )

    assert client.is_connected() is True
    assert fake.connect_calls == [
        {
            "host": "127.0.0.1",
            "port": 7497,
            "clientId": 303,
            "readonly": True,
            "timeout": 1.5,
        }
    ]


def test_client_safety_flags_are_locked() -> None:
    client = IBKRPaperReadOnlyClient(config=_enabled_config())
    assert client.paper is True
    assert client.read_only is True
    assert client.execution_enabled is False
    assert client.live_orders_blocked is True


def test_client_exposes_no_order_surface() -> None:
    client = IBKRPaperReadOnlyClient(config=_enabled_config())
    surface = set(dir(client)) | set(dir(IBKRPaperReadOnlyClient))
    leaked = sorted(surface & set(FORBIDDEN_METHOD_NAMES))
    assert not leaked


def test_account_mapping_whitelists_safe_fields_only() -> None:
    client = IBKRPaperReadOnlyClient(
        config=_enabled_config(),
        ib_factory=_FakeIB,
    )
    snapshot = client.account_snapshot()
    assert snapshot == {
        "currency": "USD",
        "cash": 1234.5,
        "equity": 5678.9,
        "buying_power": 9876.5,
    }
    assert not (set(snapshot or {}) & set(FORBIDDEN_OUTPUT_KEYS))


def test_positions_mapping_whitelists_safe_fields_only() -> None:
    client = IBKRPaperReadOnlyClient(
        config=_enabled_config(),
        ib_factory=_FakeIB,
    )
    positions = client.positions()
    assert positions == [
        {
            "symbol": "AAPL",
            "quantity": 10.0,
            "average_price": 150.25,
            "currency": "USD",
        }
    ]
    assert not (set(positions[0]) & set(FORBIDDEN_OUTPUT_KEYS))
