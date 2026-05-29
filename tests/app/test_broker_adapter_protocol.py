"""BRK-001 — Tests for the read-only ``BrokerAdapter`` protocol.

Asserts the following safety contract:

* The protocol exposes the expected read-only surface only.
* The protocol does NOT expose any forbidden execution / order /
  autotrade / risk-policy mutation method.
* Importing :mod:`brokers.protocol` does not pull in any live broker
  SDK (``MetaTrader5``, ``ib_insync``, ``alpaca`` ...) or network /
  credential dependency.
* The protocol is :func:`typing.runtime_checkable` and a minimal
  read-only fake adapter satisfies :func:`isinstance`.
* The fake adapter exposes only read-only attributes / methods.
"""

from __future__ import annotations

import importlib
import sys
from typing import Any, Mapping


# ---------------------------------------------------------------------------
# Test 1 — expected read-only surface.
# ---------------------------------------------------------------------------
def test_broker_adapter_exposes_expected_read_only_methods() -> None:
    from brokers.protocol import (
        EXPECTED_READ_ONLY_METHOD_NAMES,
        BrokerAdapter,
    )

    surface = set(dir(BrokerAdapter))
    for name in EXPECTED_READ_ONLY_METHOD_NAMES:
        assert name in surface, f"BrokerAdapter is missing read-only member: {name!r}"


# ---------------------------------------------------------------------------
# Test 2 — forbidden execution / order / risk mutation surface is absent.
# ---------------------------------------------------------------------------
def test_broker_adapter_has_no_forbidden_methods() -> None:
    from brokers.protocol import FORBIDDEN_METHOD_NAMES, BrokerAdapter

    surface = set(dir(BrokerAdapter))
    leaked = sorted(surface & set(FORBIDDEN_METHOD_NAMES))
    assert not leaked, (
        "BrokerAdapter must be read-only; forbidden execution-shaped "
        f"method(s) found on the protocol: {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Test 3 — importing the protocol pulls in no live broker SDK / network dep.
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


def test_broker_protocol_import_pulls_no_broker_or_network_modules() -> None:
    # Drop a clean slate for the protocol module so the import side-effects
    # we care about are observable in this test alone.
    sys.modules.pop("brokers.protocol", None)

    before = set(sys.modules)
    module = importlib.import_module("brokers.protocol")
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
        "brokers.protocol must be import-safe and free of broker / network "
        f"dependencies; unexpected modules imported: {leaked!r}"
    )

    # And the module itself imported successfully.
    assert hasattr(module, "BrokerAdapter")


# ---------------------------------------------------------------------------
# Test 4 — protocol is local / read-only and needs no runtime connection.
# ---------------------------------------------------------------------------
def test_broker_protocol_does_not_require_runtime_connection() -> None:
    """Defining a fake adapter and checking the protocol must not require
    opening a broker connection, contacting the network, or loading
    credentials.
    """
    from brokers.protocol import BrokerAdapter

    # Building a minimal fake adapter does not connect anywhere.
    class _OfflineFake:
        adapter_id = "offline_fake"

        def capabilities(self) -> Mapping[str, Any]:
            return {"read_only": True}

        def status(self) -> Mapping[str, Any]:
            return {"connected": False, "read_only": True}

        def account_snapshot(self) -> Mapping[str, Any]:
            return {}

        def positions(self) -> list[Mapping[str, Any]]:
            return []

    fake = _OfflineFake()
    assert isinstance(fake, BrokerAdapter)


# ---------------------------------------------------------------------------
# Test 5 — runtime_checkable + minimal fake satisfies the protocol.
# ---------------------------------------------------------------------------
def test_minimal_fake_read_only_adapter_satisfies_protocol() -> None:
    from brokers.protocol import BrokerAdapter

    class FakeReadOnlyAdapter:
        adapter_id = "fake_ro"

        def capabilities(self) -> Mapping[str, Any]:
            return {"read_only": True, "supports_positions": True}

        def status(self) -> Mapping[str, Any]:
            return {"connected": True, "read_only": True}

        def account_snapshot(self) -> Mapping[str, Any]:
            return {"balance": 0.0, "equity": 0.0, "currency": "USD"}

        def positions(self) -> list[Mapping[str, Any]]:
            return []

    adapter = FakeReadOnlyAdapter()
    assert isinstance(adapter, BrokerAdapter)
    # The five read-only methods are callable / accessible.
    assert adapter.adapter_id == "fake_ro"
    assert adapter.capabilities()["read_only"] is True
    assert adapter.status()["read_only"] is True
    assert adapter.account_snapshot()["currency"] == "USD"
    assert adapter.positions() == []


# ---------------------------------------------------------------------------
# Test 6 — fake adapter only implements read-only members.
# ---------------------------------------------------------------------------
def test_fake_read_only_adapter_only_has_read_only_members() -> None:
    from brokers.protocol import EXPECTED_READ_ONLY_METHOD_NAMES

    class FakeReadOnlyAdapter:
        adapter_id = "fake_ro"

        def capabilities(self) -> Mapping[str, Any]:
            return {}

        def status(self) -> Mapping[str, Any]:
            return {}

        def account_snapshot(self) -> Mapping[str, Any]:
            return {}

        def positions(self) -> list[Mapping[str, Any]]:
            return []

    public_attrs = {
        name for name in dir(FakeReadOnlyAdapter) if not name.startswith("_")
    }
    expected = set(EXPECTED_READ_ONLY_METHOD_NAMES)
    extra = public_attrs - expected
    assert not extra, (
        "Fake read-only adapter exposes unexpected public attributes "
        f"beyond the read-only protocol: {sorted(extra)!r}"
    )


# ---------------------------------------------------------------------------
# Test 7 — fake adapter has none of the forbidden execution-shaped names.
# ---------------------------------------------------------------------------
def test_fake_read_only_adapter_has_no_forbidden_methods() -> None:
    from brokers.protocol import FORBIDDEN_METHOD_NAMES

    class FakeReadOnlyAdapter:
        adapter_id = "fake_ro"

        def capabilities(self) -> Mapping[str, Any]:
            return {}

        def status(self) -> Mapping[str, Any]:
            return {}

        def account_snapshot(self) -> Mapping[str, Any]:
            return {}

        def positions(self) -> list[Mapping[str, Any]]:
            return []

    surface = set(dir(FakeReadOnlyAdapter))
    leaked = sorted(surface & set(FORBIDDEN_METHOD_NAMES))
    assert not leaked, (
        "Fake read-only adapter must not expose forbidden execution-shaped "
        f"method(s): {leaked!r}"
    )
