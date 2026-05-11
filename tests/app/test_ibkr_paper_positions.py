"""IBKR-006 — Tests for the read-only IBKR Paper positions path.

The adapter must:

* Default to ``[]`` when no client is injected.
* Surface real positions only when the injected client carries every
  required safety flag (``paper=True``, ``read_only=True``,
  ``execution_enabled=False``, ``live_orders_blocked=True``).
* Return ``[]`` whenever the injected client reports an unsafe flag,
  raises from its accessor, returns a non-list payload, or otherwise
  cannot be parsed.
* Silently drop every sensitive / execution-shaped field on a source
  position item (``account_id``, ``account``, ``order_id``,
  ``execution_id``, ``trade_id``, ``password``, ``token``, ``secret``,
  ``api_key``, ``credential``, ``credentials``) and surface only the
  BRK-003-aligned keys.
* Drop any malformed item (non-mapping, missing/empty symbol,
  non-numeric quantity, NaN / inf, malformed optional field).
* Keep ``read_only=True`` and stamp ``adapter_id="ibkr-paper"`` on
  every position.
* Stay import-safe (no broker SDK or network module pulled in).
* Leave the default broker registry untouched.
"""

from __future__ import annotations

import importlib
import math
import sys
from dataclasses import dataclass, field
from typing import Any, Iterable

import pytest

from app.schemas.broker import BrokerPosition
from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter


# ---------------------------------------------------------------------------
# Tiny duck-typed fake clients. None of them open a connection or
# perform network I/O.
# ---------------------------------------------------------------------------
@dataclass
class _SafePaperPositionsClient:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    items: Iterable[Any] = field(default_factory=list)

    def positions(self) -> Iterable[Any]:
        return self.items


@dataclass
class _SafePaperPositionsClientViaGetter:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    items: Iterable[Any] = field(default_factory=list)

    def get_positions(self) -> Iterable[Any]:
        return self.items


@dataclass
class _RaisingPositionsClient:
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True

    def positions(self) -> Iterable[Any]:
        raise RuntimeError("simulated accessor failure")


# ---------------------------------------------------------------------------
# Test 1 — default positions() returns [].
# ---------------------------------------------------------------------------
def test_default_positions_returns_empty_list() -> None:
    assert IBKRPaperReadOnlyAdapter().positions() == []


# ---------------------------------------------------------------------------
# Test 2 — safe fake paper client → BrokerPosition list.
# ---------------------------------------------------------------------------
def test_safe_client_surfaces_positions() -> None:
    client = _SafePaperPositionsClient(
        items=[
            {
                "symbol": "AAPL",
                "quantity": 10,
                "average_price": 150.5,
                "market_price": 155.0,
                "unrealized_pnl": 45.0,
                "currency": "USD",
            },
            {
                "symbol": "MSFT",
                "quantity": -5,
                "average_price": 320.0,
                "market_price": 315.0,
                "unrealized_pnl": 25.0,
                "currency": "USD",
            },
        ]
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    raw = adapter.positions()
    assert len(raw) == 2
    positions = [BrokerPosition(**dict(p)) for p in raw]
    assert positions[0].symbol == "AAPL"
    assert positions[0].quantity == 10.0
    assert positions[0].average_price == 150.5
    assert positions[0].market_price == 155.0
    assert positions[0].unrealized_pnl == 45.0
    assert positions[0].currency == "USD"
    assert positions[0].adapter_id == "ibkr-paper"
    assert positions[0].read_only is True

    assert positions[1].symbol == "MSFT"
    assert positions[1].quantity == -5.0
    assert positions[1].read_only is True


def test_safe_client_via_get_accessor_surfaces_positions() -> None:
    client = _SafePaperPositionsClientViaGetter(
        items=[{"symbol": "TSLA", "quantity": 1}]
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    raw = adapter.positions()
    assert len(raw) == 1
    pos = BrokerPosition(**dict(raw[0]))
    assert pos.symbol == "TSLA"
    assert pos.quantity == 1.0


# ---------------------------------------------------------------------------
# Test 3 — optional numeric fields can be missing.
# ---------------------------------------------------------------------------
def test_optional_numeric_fields_can_be_missing() -> None:
    client = _SafePaperPositionsClient(
        items=[{"symbol": "AAPL", "quantity": 10}]
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    raw = adapter.positions()
    pos = BrokerPosition(**dict(raw[0]))
    assert pos.symbol == "AAPL"
    assert pos.quantity == 10.0
    # Optional numeric fields default to None (BRK-003 allows None).
    assert pos.average_price is None
    assert pos.market_price is None
    assert pos.unrealized_pnl is None
    assert pos.currency is None


# ---------------------------------------------------------------------------
# Test 4 — unsafe fake client returns [].
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
def test_unsafe_client_returns_empty(unsafe_kwargs: dict[str, object]) -> None:
    client = _SafePaperPositionsClient(
        items=[{"symbol": "AAPL", "quantity": 10}],
        **unsafe_kwargs,  # type: ignore[arg-type]
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    assert adapter.positions() == []


# ---------------------------------------------------------------------------
# Test 5 — malformed payload returns [].
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "bad_payload",
    [
        None,
        {},  # mapping is not a list
        "not-a-list",
        42,
        object(),
    ],
    ids=["none", "dict", "str", "int", "object"],
)
def test_non_list_payload_returns_empty(bad_payload: object) -> None:
    client = _SafePaperPositionsClient(items=bad_payload)  # type: ignore[arg-type]
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    assert adapter.positions() == []


def test_accessor_raising_returns_empty() -> None:
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=_RaisingPositionsClient())
    assert adapter.positions() == []


# ---------------------------------------------------------------------------
# Test 6 — sensitive/execution fields are dropped.
# ---------------------------------------------------------------------------
_SENSITIVE_FIELDS: tuple[str, ...] = (
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
)


def test_sensitive_fields_are_dropped_from_positions() -> None:
    leaky_item = {
        "symbol": "AAPL",
        "quantity": 10,
        "average_price": 150.0,
        # Every sensitive / execution-shaped key the spec forbids.
        "account_id": "ACCT123",
        "account": "ACCT123",
        "order_id": "ord-1",
        "execution_id": "exec-1",
        "trade_id": "trd-1",
        "password": "leakme",
        "token": "tk-leakme",
        "secret": "shhh",
        "api_key": "ak-leakme",
        "credential": "cred",
        "credentials": "creds",
    }
    client = _SafePaperPositionsClient(items=[leaky_item])
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    raw = adapter.positions()
    assert len(raw) == 1
    # Validate that BRK-003 accepts the surfaced shape.
    BrokerPosition(**dict(raw[0]))
    leaked = sorted(set(raw[0].keys()) & set(_SENSITIVE_FIELDS))
    assert not leaked, f"sensitive fields leaked into position: {leaked!r}"
    # And the surfaced keys are the BRK-003 subset only.
    expected_keys = {
        "adapter_id",
        "symbol",
        "quantity",
        "average_price",
        "read_only",
        "safety_note",
    }
    assert set(raw[0].keys()) == expected_keys


# ---------------------------------------------------------------------------
# Test 7 — missing/empty symbol → item dropped.
# ---------------------------------------------------------------------------
def test_missing_or_empty_symbol_drops_item() -> None:
    client = _SafePaperPositionsClient(
        items=[
            {"quantity": 1},  # missing symbol
            {"symbol": "", "quantity": 2},  # empty symbol
            {"symbol": None, "quantity": 3},  # None symbol
            {"symbol": "AAPL", "quantity": 4},  # valid
        ]
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    raw = adapter.positions()
    assert len(raw) == 1
    assert raw[0]["symbol"] == "AAPL"


def test_non_mapping_item_dropped() -> None:
    client = _SafePaperPositionsClient(
        items=[
            "not-a-mapping",
            42,
            None,
            ["AAPL", 1],
            {"symbol": "AAPL", "quantity": 7},
        ]
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    raw = adapter.positions()
    assert len(raw) == 1
    assert raw[0]["symbol"] == "AAPL"
    assert raw[0]["quantity"] == 7.0


# ---------------------------------------------------------------------------
# Test 8 — non-numeric / NaN / inf values degrade safely.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "bad_field",
    [
        {"quantity": "ten"},
        {"quantity": object()},
        {"quantity": float("nan")},
        {"quantity": float("inf")},
        {"quantity": 1, "average_price": "high"},
        {"quantity": 1, "market_price": float("nan")},
        {"quantity": 1, "unrealized_pnl": float("-inf")},
    ],
    ids=[
        "qty-str",
        "qty-obj",
        "qty-nan",
        "qty-inf",
        "avg-price-str",
        "market-nan",
        "pnl-neg-inf",
    ],
)
def test_malformed_numeric_values_drop_item(bad_field: dict[str, object]) -> None:
    base = {"symbol": "AAPL", "quantity": 1}
    base.update(bad_field)  # type: ignore[arg-type]
    client = _SafePaperPositionsClient(items=[base])
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    raw = adapter.positions()
    assert raw == []


# ---------------------------------------------------------------------------
# Test 9 — output never contains order_id / account_id / execution_id.
# ---------------------------------------------------------------------------
def test_positions_output_never_contains_id_keys() -> None:
    client = _SafePaperPositionsClient(
        items=[
            {
                "symbol": "AAPL",
                "quantity": 10,
                "order_id": "x",
                "account_id": "y",
                "execution_id": "z",
            }
        ]
    )
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    raw = adapter.positions()
    assert len(raw) == 1
    for forbidden in ("order_id", "account_id", "execution_id", "trade_id"):
        assert forbidden not in raw[0]
    # Surfaced values are finite floats only.
    assert math.isfinite(raw[0]["quantity"])


# ---------------------------------------------------------------------------
# Test 10 — adapter still exposes no forbidden execution-shaped methods.
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
        readonly_client=_SafePaperPositionsClient()
    )
    surface = set(dir(adapter)) | set(dir(IBKRPaperReadOnlyAdapter))
    leaked = sorted(surface & set(_FORBIDDEN_METHOD_NAMES))
    assert not leaked, (
        "IBKRPaperReadOnlyAdapter must not expose forbidden "
        f"method(s): {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Test 11 — module import still pulls no broker SDK / network module.
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
# Test 12 — account_snapshot baseline still holds (sanity).
# ---------------------------------------------------------------------------
def test_account_snapshot_baseline_still_holds() -> None:
    from app.schemas.broker import BrokerAccountSnapshot

    snap = BrokerAccountSnapshot(
        **dict(IBKRPaperReadOnlyAdapter().account_snapshot())
    )
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert snap.read_only is True


# ---------------------------------------------------------------------------
# Test 13 — default registry includes IBKR paper but keeps safe default.
# ---------------------------------------------------------------------------
def test_default_registry_includes_ibkr_without_changing_default() -> None:
    from brokers.registry import create_default_registry
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    registry = create_default_registry()
    assert set(registry.list_adapter_ids()) == {
        "safe-disconnected",
        "ibkr-paper",
    }
    assert registry.default_adapter_id == "safe-disconnected"
    assert isinstance(registry.get_default(), SafeDisconnectedBrokerAdapter)
    assert registry.get_optional("ibkr-paper") is not None
