"""IBKR-005 — Tests for the read-only IBKR Paper account snapshot path.

The adapter must:

* Default to safe zeros when no client is injected.
* Surface real `cash` / `equity` / `buying_power` / `currency` only when
  the injected client carries every required safety flag.
* Force-zero whenever the injected client reports an unsafe flag or
  returns a malformed payload (non-numeric, NaN, inf, missing
  accessor, raising accessor, non-mapping return).
* Silently drop every sensitive / execution-shaped field on the source
  payload (``account_id``, ``account``, ``username``, ``password``,
  ``token``, ``secret``, ``api_key``, ``credential``, ``credentials``,
  ``order_id``, ``execution_id``) and surface only the BRK-003-aligned
  keys.
* Keep ``read_only=True`` on every output.
* Keep ``positions()`` unchanged (``[]``) — IBKR-006 will handle that.
* Stay import-safe (no broker SDK / network module pulled in).
* Leave the default broker registry untouched.
"""

from __future__ import annotations

import importlib
import math
import sys
from dataclasses import dataclass, field
from typing import Any, Mapping

import pytest

from app.schemas.broker import BrokerAccountSnapshot
from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter


# ---------------------------------------------------------------------------
# Tiny duck-typed fake clients. None of them open a connection or
# perform network I/O.
# ---------------------------------------------------------------------------
@dataclass
class _SafePaperAccountClient:
    """Safe paper client that exposes an account_snapshot() accessor."""

    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    connected: bool = True
    snapshot: Mapping[str, Any] = field(
        default_factory=lambda: {
            "currency": "USD",
            "cash": 1234.5,
            "equity": 5678.9,
            "buying_power": 9876.5,
        }
    )

    def account_snapshot(self) -> Mapping[str, Any]:
        return self.snapshot


@dataclass
class _SafePaperAccountClientViaGetter:
    """Like above but uses get_account_snapshot()."""

    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    snapshot: Mapping[str, Any] = field(
        default_factory=lambda: {
            "currency": "EUR",
            "cash": 100.0,
            "equity": 200.0,
            "buying_power": 300.0,
        }
    )

    def get_account_snapshot(self) -> Mapping[str, Any]:
        return self.snapshot


@dataclass
class _RaisingAccountClient:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True

    def account_snapshot(self) -> Mapping[str, Any]:
        raise RuntimeError("simulated broker accessor failure")


# ---------------------------------------------------------------------------
# Test 1 — default adapter returns safe zeros.
# ---------------------------------------------------------------------------
def test_default_account_snapshot_returns_safe_zeros() -> None:
    snap = BrokerAccountSnapshot(
        **dict(IBKRPaperReadOnlyAdapter().account_snapshot())
    )
    assert snap.adapter_id == "ibkr-paper"
    assert snap.currency == "USD"
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert snap.read_only is True


# ---------------------------------------------------------------------------
# Test 2 — safe paper client surfaces real values.
# ---------------------------------------------------------------------------
def test_safe_client_surfaces_account_values() -> None:
    adapter = IBKRPaperReadOnlyAdapter(
        readonly_client=_SafePaperAccountClient()
    )
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.currency == "USD"
    assert snap.cash == 1234.5
    assert snap.equity == 5678.9
    assert snap.buying_power == 9876.5
    assert snap.read_only is True


def test_safe_client_via_get_accessor_surfaces_account_values() -> None:
    adapter = IBKRPaperReadOnlyAdapter(
        readonly_client=_SafePaperAccountClientViaGetter()
    )
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.currency == "EUR"
    assert snap.cash == 100.0
    assert snap.equity == 200.0
    assert snap.buying_power == 300.0


# ---------------------------------------------------------------------------
# Test 3 — missing numeric fields default to 0.0.
# ---------------------------------------------------------------------------
def test_missing_numeric_fields_default_to_zero() -> None:
    client = _SafePaperAccountClient(
        snapshot={"currency": "USD", "cash": 250.0}
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.cash == 250.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0


# ---------------------------------------------------------------------------
# Test 4 — missing currency defaults to USD.
# ---------------------------------------------------------------------------
def test_missing_currency_defaults_to_usd() -> None:
    client = _SafePaperAccountClient(
        snapshot={"cash": 1.0, "equity": 2.0, "buying_power": 3.0}
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.currency == "USD"


# ---------------------------------------------------------------------------
# Tests 5–8 — unsafe fake clients return safe zero snapshot.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "unsafe_kwargs",
    [
        {"paper": False},
        {"read_only": False},
        {"execution_enabled": True},
        {"live_orders_blocked": False},
    ],
    ids=[
        "paper-false",
        "read-only-false",
        "execution-enabled",
        "live-orders-not-blocked",
    ],
)
def test_unsafe_client_returns_safe_zero_snapshot(
    unsafe_kwargs: dict[str, object],
) -> None:
    client = _SafePaperAccountClient(**unsafe_kwargs)  # type: ignore[arg-type]
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert snap.currency == "USD"
    assert snap.read_only is True
    # The note must clearly explain the unsafe-client rejection.
    assert "unsafe" in snap.safety_note.lower() or "violat" in snap.safety_note.lower()


# ---------------------------------------------------------------------------
# Test 9 — malformed numeric values degrade safely to zero snapshot.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "bad_snapshot",
    [
        {"cash": "not-a-number", "equity": 0.0, "buying_power": 0.0},
        {"cash": 0.0, "equity": object(), "buying_power": 0.0},
        {"cash": 0.0, "equity": 0.0, "buying_power": [1, 2]},
        {"cash": float("nan"), "equity": 0.0, "buying_power": 0.0},
        {"cash": float("inf"), "equity": 0.0, "buying_power": 0.0},
    ],
    ids=["cash-str", "equity-obj", "bp-list", "cash-nan", "cash-inf"],
)
def test_malformed_payload_degrades_safely(
    bad_snapshot: dict[str, object],
) -> None:
    client = _SafePaperAccountClient(
        snapshot={"currency": "USD", **bad_snapshot}
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert "malformed" in snap.safety_note.lower()
    # Sanity: BRK-003 itself only sees finite floats.
    for value in (snap.cash, snap.equity, snap.buying_power):
        assert math.isfinite(value)


def test_accessor_raising_degrades_safely() -> None:
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=_RaisingAccountClient())
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.cash == snap.equity == snap.buying_power == 0.0


def test_non_mapping_accessor_return_degrades_safely() -> None:
    @dataclass
    class _BadShape:
        paper: bool = True
        read_only: bool = True
        execution_enabled: bool = False
        live_orders_blocked: bool = True

        def account_snapshot(self) -> Any:
            return ["unexpected", "list"]

    adapter = IBKRPaperReadOnlyAdapter(readonly_client=_BadShape())
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.cash == snap.equity == snap.buying_power == 0.0


# ---------------------------------------------------------------------------
# Test 10 — sensitive fields on the source payload are dropped.
# ---------------------------------------------------------------------------
_SENSITIVE_FIELDS: tuple[str, ...] = (
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
)


def test_sensitive_source_fields_are_dropped() -> None:
    leaky = {
        "currency": "USD",
        "cash": 1.0,
        "equity": 2.0,
        "buying_power": 3.0,
        # Every sensitive / execution-shaped key the spec forbids.
        "account_id": "ACCT123",
        "account": "ACCT123",
        "username": "alice",
        "password": "leakme",
        "token": "tk-leakme",
        "secret": "shhh",
        "api_key": "ak-leakme",
        "credential": "cred",
        "credentials": "creds",
        "order_id": "ord-1",
        "execution_id": "exec-1",
    }
    client = _SafePaperAccountClient(snapshot=leaky)
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    snap = adapter.account_snapshot()

    # BRK-003 validation accepts the snapshot.
    BrokerAccountSnapshot(**dict(snap))

    # The output mapping contains exactly the BRK-003 keys — nothing
    # else leaks through.
    expected_keys = {
        "adapter_id",
        "currency",
        "cash",
        "equity",
        "buying_power",
        "read_only",
        "safety_note",
    }
    assert set(snap.keys()) == expected_keys

    leaked = sorted(set(snap.keys()) & set(_SENSITIVE_FIELDS))
    assert not leaked, f"sensitive fields leaked into snapshot: {leaked!r}"


# ---------------------------------------------------------------------------
# Test 11 — account_snapshot always exposes read_only=True.
# ---------------------------------------------------------------------------
def test_account_snapshot_always_read_only() -> None:
    assert IBKRPaperReadOnlyAdapter().account_snapshot()["read_only"] is True
    safe_client = _SafePaperAccountClient()
    assert (
        IBKRPaperReadOnlyAdapter(readonly_client=safe_client).account_snapshot()[
            "read_only"
        ]
        is True
    )


# ---------------------------------------------------------------------------
# Test 12 — positions() remains [].
# ---------------------------------------------------------------------------
def test_positions_still_empty_with_safe_client() -> None:
    adapter = IBKRPaperReadOnlyAdapter(
        readonly_client=_SafePaperAccountClient()
    )
    assert adapter.positions() == []


# ---------------------------------------------------------------------------
# Test 13 — adapter still exposes no forbidden execution-shaped methods.
# ---------------------------------------------------------------------------
_FORBIDDEN_METHOD_NAMES: tuple[str, ...] = (
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


def test_adapter_has_no_forbidden_methods() -> None:
    adapter = IBKRPaperReadOnlyAdapter(
        readonly_client=_SafePaperAccountClient()
    )
    surface = set(dir(adapter)) | set(dir(IBKRPaperReadOnlyAdapter))
    leaked = sorted(surface & set(_FORBIDDEN_METHOD_NAMES))
    assert not leaked, (
        "IBKRPaperReadOnlyAdapter must not expose forbidden "
        f"method(s): {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Test 14 — module import still pulls no broker SDK / network module.
# ---------------------------------------------------------------------------
_FORBIDDEN_IMPORT_PREFIXES: tuple[str, ...] = (
    "ib_insync",
    "ibapi",
    "MetaTrader5",
    "alpaca",
    "alpaca_trade_api",
    "ccxt",
    "requests",
    "httpx",
    "websocket",
    "websockets",
)


def test_module_import_pulls_no_broker_or_network_modules() -> None:
    for name in (
        "brokers.ibkr_paper_readonly",
        "brokers.ibkr_config",
    ):
        sys.modules.pop(name, None)

    before = set(sys.modules)
    importlib.import_module("brokers.ibkr_paper_readonly")
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
        "brokers.ibkr_paper_readonly must be import-safe; unexpected "
        f"modules imported: {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Test 15 — default registry unchanged.
# ---------------------------------------------------------------------------
def test_default_registry_still_only_safe_disconnected() -> None:
    from brokers.registry import create_default_registry

    registry = create_default_registry()
    assert registry.list_adapter_ids() == ["safe-disconnected"]
    assert registry.get_optional("ibkr-paper") is None
