"""BRK-002 — Tests for :class:`SafeDisconnectedBrokerAdapter`.

Asserts the safety contract:

* The adapter implements the read-only :class:`brokers.protocol.BrokerAdapter`.
* It returns safe defaults declaring itself disconnected and read-only.
* It exposes none of the forbidden execution / order / risk-mutation
  method names.
* Its module imports no broker SDK or network dependency.
"""

from __future__ import annotations

import importlib
import sys


# ---------------------------------------------------------------------------
# Test 1 — module imports successfully.
# ---------------------------------------------------------------------------
def test_safe_disconnected_module_imports() -> None:
    module = importlib.import_module("brokers.safe_disconnected")
    assert hasattr(module, "SafeDisconnectedBrokerAdapter")
    assert hasattr(module, "ADAPTER_ID")
    assert module.ADAPTER_ID == "safe-disconnected"


# ---------------------------------------------------------------------------
# Test 2 — instance satisfies the runtime_checkable BrokerAdapter protocol.
# ---------------------------------------------------------------------------
def test_safe_disconnected_satisfies_broker_adapter_protocol() -> None:
    from brokers.protocol import BrokerAdapter
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    adapter = SafeDisconnectedBrokerAdapter()
    assert isinstance(adapter, BrokerAdapter)


# ---------------------------------------------------------------------------
# Test 3 — adapter_id.
# ---------------------------------------------------------------------------
def test_adapter_id_is_safe_disconnected() -> None:
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    adapter = SafeDisconnectedBrokerAdapter()
    assert adapter.adapter_id == "safe-disconnected"


# ---------------------------------------------------------------------------
# Test 4 — capabilities() reports safe, read-only, non-executable.
# ---------------------------------------------------------------------------
def test_capabilities_report_read_only_non_executable() -> None:
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    caps = SafeDisconnectedBrokerAdapter().capabilities()

    assert caps["read_only"] is True
    assert caps["execution_enabled"] is False
    assert caps["live_orders_blocked"] is True
    assert caps["can_place_orders"] is False
    assert caps["can_cancel_orders"] is False
    assert caps["can_modify_orders"] is False
    assert caps["supports_account_snapshot"] is True
    assert caps["supports_positions"] is True
    assert caps["paper"] is False
    assert "safety_note" in caps and isinstance(caps["safety_note"], str)
    assert caps["safety_note"].strip()


# ---------------------------------------------------------------------------
# Test 5 — status() reports disconnected/degraded/read-only.
# ---------------------------------------------------------------------------
def test_status_reports_disconnected_and_safe() -> None:
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    status = SafeDisconnectedBrokerAdapter().status()

    assert status["connected"] is False
    assert status["degraded"] is True
    assert status["read_only"] is True
    assert status["execution_enabled"] is False
    assert status["live_orders_blocked"] is True
    assert "degraded_reason" in status and status["degraded_reason"]
    assert "safety_note" in status and isinstance(status["safety_note"], str)


# ---------------------------------------------------------------------------
# Test 6 — account_snapshot() returns safe zero values.
# ---------------------------------------------------------------------------
def test_account_snapshot_returns_safe_zero_values() -> None:
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    snap = SafeDisconnectedBrokerAdapter().account_snapshot()

    assert snap["read_only"] is True
    assert snap["cash"] == 0.0
    assert snap["equity"] == 0.0
    assert snap["buying_power"] == 0.0
    assert snap["currency"] in ("USD", "N/A")
    assert "safety_note" in snap and isinstance(snap["safety_note"], str)


# ---------------------------------------------------------------------------
# Test 7 — positions() returns an empty list.
# ---------------------------------------------------------------------------
def test_positions_returns_empty_list() -> None:
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    positions = SafeDisconnectedBrokerAdapter().positions()
    assert positions == []
    assert isinstance(positions, list)


# ---------------------------------------------------------------------------
# Test 8 — no forbidden execution-shaped method names exist on the adapter.
# ---------------------------------------------------------------------------
def test_safe_disconnected_has_no_forbidden_methods() -> None:
    from brokers.protocol import FORBIDDEN_METHOD_NAMES
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    adapter = SafeDisconnectedBrokerAdapter()
    surface = set(dir(adapter)) | set(dir(SafeDisconnectedBrokerAdapter))
    leaked = sorted(surface & set(FORBIDDEN_METHOD_NAMES))
    assert not leaked, (
        "SafeDisconnectedBrokerAdapter must not expose forbidden "
        f"execution-shaped method(s): {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Test 9 — module import does not pull in broker SDK / network deps.
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


def test_safe_disconnected_import_pulls_no_broker_or_network_modules() -> None:
    sys.modules.pop("brokers.safe_disconnected", None)

    before = set(sys.modules)
    importlib.import_module("brokers.safe_disconnected")
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
        "brokers.safe_disconnected must be import-safe; unexpected modules "
        f"imported: {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Test 10 — only public attributes are the expected read-only surface.
# ---------------------------------------------------------------------------
def test_safe_disconnected_public_surface_is_read_only_only() -> None:
    from brokers.protocol import EXPECTED_READ_ONLY_METHOD_NAMES
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    public = {
        name for name in dir(SafeDisconnectedBrokerAdapter) if not name.startswith("_")
    }
    expected = set(EXPECTED_READ_ONLY_METHOD_NAMES)
    extra = public - expected
    assert not extra, (
        "SafeDisconnectedBrokerAdapter must only expose the read-only "
        f"protocol surface; extra public attributes: {sorted(extra)!r}"
    )
