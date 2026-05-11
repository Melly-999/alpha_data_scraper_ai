"""IBKR-011/012 no-order-surface regression tests.

These tests pin the read-only IBKR Paper adapter contract across the
states introduced by IBKR-001, IBKR-002, IBKR-005, and IBKR-006. The
adapter must remain import-safe, registry-isolated, read-only, and free
of execution-shaped methods even when injected fake clients report
unsafe flags or leaky/malformed read payloads.
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

import pytest


FORBIDDEN_METHOD_NAMES: tuple[str, ...] = (
    "place_order",
    "cancel_order",
    "modify_order",
    "execute",
    "submit_order",
    "close_position",
    "open_position",
    "broker_execute",
    "enable_autotrade",
    "disable_dry_run",
    "change_config_runtime",
    "modify_risk_policy",
    "placeOrder",
    "cancelOrder",
    "reqMktData",
    "reqPositions",
    "buy",
    "sell",
    "connect",
    "disconnect",
)

FORBIDDEN_OUTPUT_KEYS: tuple[str, ...] = (
    "account_id",
    "account",
    "order_id",
    "execution_id",
    "trade_id",
    "password",
    "token",
    "secret",
    "api_key",
    "credential",
    "credentials",
    "username",
)

FORBIDDEN_IMPORT_PREFIXES: tuple[str, ...] = (
    "ib_insync",
    "ibapi",
    "MetaTrader5",
    "requests",
    "httpx",
    "websocket",
    "websockets",
    "alpaca",
    "alpaca_trade_api",
    "ccxt",
)

FORBIDDEN_OPENAPI_SINGLE_SEGMENTS: tuple[str, ...] = (
    "execute",
    "execute-trade",
    "execute_trade",
    "live-trade",
    "live_trade",
    "place-order",
    "place_order",
    "submit-order",
    "submit_order",
    "broker-execute",
    "broker_execute",
    "disable-dry-run",
    "enable-autotrade",
)

FORBIDDEN_OPENAPI_COMPOUND_PATTERNS: tuple[str, ...] = (
    "order/place",
    "order/submit",
    "trade/execute",
    "trading/execute",
    "autotrade/enable",
    "dry-run/disable",
)


@dataclass
class _SafePaperClient:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    connected: bool = True


@dataclass
class _UnsafePaperClient:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    connected: bool = True


@dataclass
class _AccountSnapshotClient:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    connected: bool = True
    snapshot: Mapping[str, Any] = field(
        default_factory=lambda: {
            "currency": "USD",
            "cash": 1000.0,
            "equity": 1100.0,
            "buying_power": 5000.0,
            "account_id": "should-not-surface",
            "account": "should-not-surface",
            "username": "should-not-surface",
            "password": "should-not-surface",
            "token": "should-not-surface",
            "secret": "should-not-surface",
            "api_key": "should-not-surface",
            "credential": "should-not-surface",
            "credentials": "should-not-surface",
            "order_id": "should-not-surface",
            "execution_id": "should-not-surface",
        }
    )

    def account_snapshot(self) -> Mapping[str, Any]:
        return self.snapshot


@dataclass
class _PositionsClient:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    connected: bool = True
    items: Iterable[Any] = field(
        default_factory=lambda: [
            {
                "symbol": "AAPL",
                "quantity": 10,
                "average_price": 150.0,
                "market_price": 155.0,
                "unrealized_pnl": 50.0,
                "currency": "USD",
                "account_id": "should-not-surface",
                "account": "should-not-surface",
                "order_id": "should-not-surface",
                "execution_id": "should-not-surface",
                "trade_id": "should-not-surface",
                "password": "should-not-surface",
                "token": "should-not-surface",
                "secret": "should-not-surface",
                "api_key": "should-not-surface",
                "credential": "should-not-surface",
                "credentials": "should-not-surface",
            },
            {
                "symbol": "MSFT",
                "quantity": 5,
                "currency": "USD",
                "account_id": "should-not-surface",
            },
        ]
    )

    def positions(self) -> Iterable[Any]:
        return self.items


@dataclass
class _MalformedAllClient:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    connected: bool = True

    def account_snapshot(self) -> Any:
        return {"currency": "USD", "cash": "not-a-number"}

    def positions(self) -> Any:
        return "not-a-position-list"


def _every_adapter_state() -> list[tuple[str, Any]]:
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter

    return [
        ("default-disconnected", IBKRPaperReadOnlyAdapter()),
        (
            "safe-connected",
            IBKRPaperReadOnlyAdapter(readonly_client=_SafePaperClient()),
        ),
        (
            "unsafe-paper-false",
            IBKRPaperReadOnlyAdapter(
                readonly_client=_UnsafePaperClient(paper=False)
            ),
        ),
        (
            "unsafe-read-only-false",
            IBKRPaperReadOnlyAdapter(
                readonly_client=_UnsafePaperClient(read_only=False)
            ),
        ),
        (
            "unsafe-execution-enabled",
            IBKRPaperReadOnlyAdapter(
                readonly_client=_UnsafePaperClient(execution_enabled=True)
            ),
        ),
        (
            "unsafe-live-orders-not-blocked",
            IBKRPaperReadOnlyAdapter(
                readonly_client=_UnsafePaperClient(live_orders_blocked=False)
            ),
        ),
        (
            "account-snapshot-client",
            IBKRPaperReadOnlyAdapter(readonly_client=_AccountSnapshotClient()),
        ),
        (
            "positions-client",
            IBKRPaperReadOnlyAdapter(readonly_client=_PositionsClient()),
        ),
        (
            "malformed-mixed-data",
            IBKRPaperReadOnlyAdapter(readonly_client=_MalformedAllClient()),
        ),
    ]


STATE_PARAMS = pytest.mark.parametrize(
    "state_name, adapter",
    _every_adapter_state(),
    ids=lambda value: value if isinstance(value, str) else "adapter",
)


def _forbidden_methods_on(obj: object) -> list[str]:
    return sorted(set(dir(obj)) & set(FORBIDDEN_METHOD_NAMES))


def test_class_has_no_forbidden_methods() -> None:
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter

    leaked = _forbidden_methods_on(IBKRPaperReadOnlyAdapter)
    assert not leaked, f"class exposes forbidden methods: {leaked!r}"


@STATE_PARAMS
def test_instance_has_no_forbidden_methods_in_every_state(
    state_name: str, adapter: Any
) -> None:
    leaked = _forbidden_methods_on(adapter)
    assert not leaked, (
        f"adapter in state {state_name!r} exposes forbidden methods: "
        f"{leaked!r}"
    )


@STATE_PARAMS
def test_capabilities_always_lock_safety_flags(
    state_name: str, adapter: Any
) -> None:
    caps = adapter.capabilities()
    assert caps["read_only"] is True, state_name
    assert caps["paper"] is True, state_name
    assert caps["execution_enabled"] is False, state_name
    assert caps["live_orders_blocked"] is True, state_name
    assert caps["can_place_orders"] is False, state_name
    assert caps["can_cancel_orders"] is False, state_name
    assert caps["can_modify_orders"] is False, state_name


@STATE_PARAMS
def test_status_always_forces_safety_flags(
    state_name: str, adapter: Any
) -> None:
    status = adapter.status()
    assert status["read_only"] is True, state_name
    assert status["execution_enabled"] is False, state_name
    assert status["live_orders_blocked"] is True, state_name


@STATE_PARAMS
def test_account_snapshot_never_leaks_sensitive_or_execution_keys(
    state_name: str, adapter: Any
) -> None:
    snapshot = adapter.account_snapshot()
    assert snapshot["read_only"] is True, state_name

    leaked = sorted(set(snapshot.keys()) & set(FORBIDDEN_OUTPUT_KEYS))
    assert not leaked, (
        f"account_snapshot in state {state_name!r} leaked keys: {leaked!r}"
    )


@STATE_PARAMS
def test_positions_never_leak_sensitive_or_execution_keys(
    state_name: str, adapter: Any
) -> None:
    positions = adapter.positions()
    assert isinstance(positions, list), state_name

    for index, position in enumerate(positions):
        assert isinstance(position, Mapping), (state_name, index)
        assert position["read_only"] is True, (state_name, index)
        leaked = sorted(set(position.keys()) & set(FORBIDDEN_OUTPUT_KEYS))
        assert not leaked, (
            f"position {index} in state {state_name!r} leaked keys: "
            f"{leaked!r}"
        )


def test_module_import_pulls_no_broker_sdk_or_network_modules() -> None:
    for module_name in (
        "brokers.ibkr_paper_readonly",
        "brokers.ibkr_config",
    ):
        sys.modules.pop(module_name, None)

    before = set(sys.modules)
    importlib.import_module("brokers.ibkr_paper_readonly")
    newly_imported = set(sys.modules) - before

    leaked = sorted(
        module_name
        for module_name in newly_imported
        if any(
            module_name == prefix or module_name.startswith(prefix + ".")
            for prefix in FORBIDDEN_IMPORT_PREFIXES
        )
    )
    assert not leaked, (
        "IBKR read-only adapter import pulled forbidden modules: "
        f"{leaked!r}"
    )


def test_openapi_forbidden_path_scan_still_passes(client) -> None:
    schema = client.app.openapi()
    paths = list((schema.get("paths") or {}).keys())

    offenders: list[tuple[str, str]] = []
    for path in paths:
        parts = path.split("/")
        for segment in FORBIDDEN_OPENAPI_SINGLE_SEGMENTS:
            if segment in parts:
                offenders.append((path, segment))
        for pattern in FORBIDDEN_OPENAPI_COMPOUND_PATTERNS:
            if pattern in path:
                offenders.append((path, pattern))

    assert not offenders, (
        "OpenAPI schema contains order/execution-shaped paths: "
        f"{offenders!r}"
    )


def test_default_registry_still_only_safe_disconnected() -> None:
    from brokers.registry import create_default_registry

    registry = create_default_registry()
    assert registry.list_adapter_ids() == ["safe-disconnected"]
    assert registry.get_optional("ibkr-paper") is None
