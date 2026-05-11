"""BRK-007 — Tests for :class:`brokers.registry.BrokerRegistry`.

Asserts the safety contract:

* Default registry contains safe-disconnected plus ibkr-paper.
* Default lookup still returns safe-disconnected.
* Default lookup returns that adapter.
* Missing-id lookup raises :class:`KeyError`; ``get_optional`` returns
  ``None``.
* The registry exposes no execution-shaped methods.
* Returned default adapter's outputs validate cleanly into the
  BRK-003 typed schemas (`BrokerCapabilities`, `BrokerStatus`,
  `BrokerAccountSnapshot`, `BrokerPosition`).
* Importing :mod:`brokers.registry` pulls in no broker SDK or
  network module.
"""

from __future__ import annotations

import importlib
import sys

import pytest


# ---------------------------------------------------------------------------
# Test 1 — module imports.
# ---------------------------------------------------------------------------
def test_broker_registry_module_imports() -> None:
    module = importlib.import_module("brokers.registry")
    assert hasattr(module, "BrokerRegistry")
    assert hasattr(module, "create_default_registry")
    assert hasattr(module, "default_broker_registry")
    assert module.DEFAULT_ADAPTER_ID == "safe-disconnected"


# ---------------------------------------------------------------------------
# Test 2 — both factory names exist and return fresh instances.
# ---------------------------------------------------------------------------
def test_default_registry_factories_return_fresh_instances() -> None:
    from brokers.registry import (
        BrokerRegistry,
        create_default_registry,
        default_broker_registry,
    )

    a = create_default_registry()
    b = default_broker_registry()
    assert isinstance(a, BrokerRegistry)
    assert isinstance(b, BrokerRegistry)
    assert a is not b


# ---------------------------------------------------------------------------
# Test 3 — default registry contains safe-disconnected plus ibkr-paper.
# ---------------------------------------------------------------------------
def test_default_registry_contains_safe_disconnected_and_ibkr_paper() -> None:
    from brokers.registry import create_default_registry

    registry = create_default_registry()
    assert set(registry.list_adapter_ids()) == {
        "safe-disconnected",
        "ibkr-paper",
    }
    assert len(registry) == 2


# ---------------------------------------------------------------------------
# Test 4 — default adapter id.
# ---------------------------------------------------------------------------
def test_default_registry_default_is_safe_disconnected() -> None:
    from brokers.registry import create_default_registry

    registry = create_default_registry()
    assert registry.default_adapter_id == "safe-disconnected"
    assert registry.get_default().adapter_id == "safe-disconnected"


# ---------------------------------------------------------------------------
# Test 5 — get returns the SafeDisconnectedBrokerAdapter.
# ---------------------------------------------------------------------------
def test_get_returns_safe_disconnected_adapter() -> None:
    from brokers.registry import create_default_registry
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    registry = create_default_registry()
    adapter = registry.get("safe-disconnected")
    assert isinstance(adapter, SafeDisconnectedBrokerAdapter)


def test_get_returns_ibkr_paper_readonly_adapter() -> None:
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter
    from brokers.registry import create_default_registry

    registry = create_default_registry()
    adapter = registry.get("ibkr-paper")
    assert isinstance(adapter, IBKRPaperReadOnlyAdapter)


# ---------------------------------------------------------------------------
# Test 6 — has() / __contains__.
# ---------------------------------------------------------------------------
def test_has_and_contains_for_known_and_unknown_ids() -> None:
    from brokers.registry import create_default_registry

    registry = create_default_registry()
    assert registry.has("safe-disconnected") is True
    assert registry.has("ibkr-paper") is True
    assert "safe-disconnected" in registry
    assert "ibkr-paper" in registry
    assert registry.has("mt5-live") is False
    assert "mt5-live" not in registry
    # Non-string is never present.
    assert 123 not in registry  # type: ignore[operator]


# ---------------------------------------------------------------------------
# Test 7 — missing adapter lookup behaves safely and predictably.
# ---------------------------------------------------------------------------
def test_missing_adapter_lookup_behaviour() -> None:
    from brokers.registry import create_default_registry

    registry = create_default_registry()

    with pytest.raises(KeyError) as excinfo:
        registry.get("mt5-live")
    assert "mt5-live" in str(excinfo.value)

    assert registry.get_optional("mt5-live") is None


# ---------------------------------------------------------------------------
# Test 8 — list_adapters / list_adapter_ids return read-only safe info.
# ---------------------------------------------------------------------------
def test_list_adapters_returns_safe_adapter_objects() -> None:
    from brokers.registry import create_default_registry

    registry = create_default_registry()
    ids = registry.list_adapter_ids()
    adapters = registry.list_adapters()
    assert set(ids) == {"safe-disconnected", "ibkr-paper"}
    assert len(adapters) == 2
    assert {adapter.adapter_id for adapter in adapters} == {
        "safe-disconnected",
        "ibkr-paper",
    }


# ---------------------------------------------------------------------------
# Test 9 — default adapter capabilities validate as BrokerCapabilities.
# ---------------------------------------------------------------------------
def test_default_adapter_capabilities_validate_into_schema() -> None:
    from app.schemas.broker import BrokerCapabilities
    from brokers.registry import create_default_registry

    adapter = create_default_registry().get_default()
    payload = dict(adapter.capabilities())
    payload.pop("adapter_id", None)
    caps = BrokerCapabilities(**payload)
    assert caps.read_only is True
    assert caps.execution_enabled is False
    assert caps.live_orders_blocked is True


# ---------------------------------------------------------------------------
# Test 10 — default adapter status validates as BrokerStatus.
# ---------------------------------------------------------------------------
def test_default_adapter_status_validates_into_schema() -> None:
    from app.schemas.broker import BrokerStatus
    from brokers.registry import create_default_registry

    adapter = create_default_registry().get_default()
    status = BrokerStatus(**dict(adapter.status()))
    assert status.connected is False
    assert status.degraded is True
    assert status.read_only is True
    assert status.live_orders_blocked is True


# ---------------------------------------------------------------------------
# Test 11 — default adapter account_snapshot validates as BrokerAccountSnapshot.
# ---------------------------------------------------------------------------
def test_default_adapter_account_snapshot_validates_into_schema() -> None:
    from app.schemas.broker import BrokerAccountSnapshot
    from brokers.registry import create_default_registry

    adapter = create_default_registry().get_default()
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert snap.read_only is True


# ---------------------------------------------------------------------------
# Test 12 — default adapter positions validate as list[BrokerPosition].
# ---------------------------------------------------------------------------
def test_default_adapter_positions_validate_into_schema() -> None:
    from app.schemas.broker import BrokerPosition
    from brokers.registry import create_default_registry

    adapter = create_default_registry().get_default()
    positions = [BrokerPosition(**dict(p)) for p in adapter.positions()]
    assert positions == []


def test_ibkr_paper_adapter_validates_as_broker_adapter() -> None:
    from brokers.protocol import BrokerAdapter
    from brokers.registry import create_default_registry

    adapter = create_default_registry().get("ibkr-paper")
    assert isinstance(adapter, BrokerAdapter)


def test_ibkr_paper_capabilities_validate_into_schema() -> None:
    from app.schemas.broker import BrokerCapabilities
    from brokers.registry import create_default_registry

    adapter = create_default_registry().get("ibkr-paper")
    payload = dict(adapter.capabilities())
    payload.pop("adapter_id", None)
    caps = BrokerCapabilities(**payload)
    assert caps.read_only is True
    assert caps.paper is True
    assert caps.execution_enabled is False
    assert caps.live_orders_blocked is True
    assert caps.can_place_orders is False
    assert caps.can_cancel_orders is False
    assert caps.can_modify_orders is False


def test_ibkr_paper_status_validates_as_safe_disconnected_default() -> None:
    from app.schemas.broker import BrokerStatus
    from brokers.registry import create_default_registry

    adapter = create_default_registry().get("ibkr-paper")
    status = BrokerStatus(**dict(adapter.status()))
    assert status.adapter_id == "ibkr-paper"
    assert status.connected is False
    assert status.degraded is True
    assert status.read_only is True
    assert status.execution_enabled is False
    assert status.live_orders_blocked is True


def test_ibkr_paper_account_snapshot_validates_as_safe_zero_default() -> None:
    from app.schemas.broker import BrokerAccountSnapshot
    from brokers.registry import create_default_registry

    adapter = create_default_registry().get("ibkr-paper")
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.adapter_id == "ibkr-paper"
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert snap.read_only is True


def test_ibkr_paper_positions_validate_as_empty_default() -> None:
    from app.schemas.broker import BrokerPosition
    from brokers.registry import create_default_registry

    adapter = create_default_registry().get("ibkr-paper")
    positions = [BrokerPosition(**dict(p)) for p in adapter.positions()]
    assert positions == []


# ---------------------------------------------------------------------------
# Test 13 — registry exposes no forbidden execution-shaped methods.
# ---------------------------------------------------------------------------
def test_registry_has_no_forbidden_methods() -> None:
    from brokers.protocol import FORBIDDEN_METHOD_NAMES
    from brokers.registry import BrokerRegistry, create_default_registry

    registry = create_default_registry()
    surface = set(dir(BrokerRegistry)) | set(dir(registry))
    leaked = sorted(surface & set(FORBIDDEN_METHOD_NAMES))
    assert not leaked, (
        "BrokerRegistry must not expose forbidden execution-shaped "
        f"method(s): {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Test 14 — module import pulls in no broker SDK / network module.
# ---------------------------------------------------------------------------
_FORBIDDEN_IMPORT_PREFIXES: tuple[str, ...] = (
    "MetaTrader5",
    "ib_insync",
    "ibapi",
    "alpaca",
    "alpaca_trade_api",
    "ccxt",
    "requests",
    "httpx",
    "websocket",
    "websockets",
)


def test_registry_import_pulls_no_broker_or_network_modules() -> None:
    sys.modules.pop("brokers.registry", None)

    before = set(sys.modules)
    importlib.import_module("brokers.registry")
    after = set(sys.modules)

    newly_imported = after - before
    leaked = sorted(
        name
        for name in newly_imported
        if any(
            name == prefix or name.startswith(prefix + ".")
            for prefix in _FORBIDDEN_IMPORT_PREFIXES
        )
    )
    assert not leaked, (
        "brokers.registry must be import-safe; unexpected modules "
        f"imported: {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Bonus — register() basic semantics: duplicate id is rejected.
# ---------------------------------------------------------------------------
def test_register_rejects_duplicate_ids() -> None:
    from brokers.registry import create_default_registry
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    registry = create_default_registry()
    with pytest.raises(ValueError):
        registry.register(SafeDisconnectedBrokerAdapter())
