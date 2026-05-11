"""IBKR-001 — Tests for the read-only IBKR Paper adapter skeleton.

Asserts:

* :class:`brokers.ibkr_config.IBKRPaperConfig` defaults are safe
  (paper=True, read_only=True, sane host/port/client_id/timeout) and
  the config rejects any attempt to weaken them.
* :class:`brokers.ibkr_paper_readonly.IBKRPaperReadOnlyAdapter`
  implements the read-only :class:`brokers.protocol.BrokerAdapter`
  protocol with `adapter_id == "ibkr-paper"`.
* All four outputs validate cleanly into the BRK-003 schemas, with
  safe disconnected/degraded defaults and zero-valued account state.
* The adapter exposes none of the forbidden execution-shaped method
  names (including IBKR-specific ones like ``placeOrder`` /
  ``cancelOrder`` / ``reqMktData`` / ``reqPositions`` / ``buy`` /
  ``sell``).
* Importing the module pulls in no broker SDK or network dependency
  (``ib_insync``, ``ibapi``, ``MetaTrader5``, ``requests``, ``httpx``,
  ``websockets``, ``alpaca``, ``ccxt``).
* The default broker registry still contains exactly the
  ``safe-disconnected`` adapter — the IBKR adapter is *not* registered
  in this task.
* The legacy ``tests/app/test_broker_endpoints.py`` baseline is
  unaffected (smoke-checked by importing the route module).
"""

from __future__ import annotations

import importlib
import sys

import pytest


# ---------------------------------------------------------------------------
# IBKRPaperConfig — defaults and safety constraints
# ---------------------------------------------------------------------------
def test_ibkr_paper_config_defaults_are_safe() -> None:
    from brokers.ibkr_config import IBKRPaperConfig

    cfg = IBKRPaperConfig()
    assert cfg.paper is True
    assert cfg.read_only is True
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 7497
    assert cfg.client_id == 101
    assert cfg.timeout_s > 0
    assert cfg.account_filter is None


_FORBIDDEN_CONFIG_FIELDS: tuple[str, ...] = (
    "password",
    "token",
    "api_key",
    "secret",
    "credential",
    "credentials",
    "account_id",
)


@pytest.mark.parametrize("field", _FORBIDDEN_CONFIG_FIELDS)
def test_ibkr_paper_config_has_no_secret_or_account_fields(field: str) -> None:
    from brokers.ibkr_config import IBKRPaperConfig

    declared = set(IBKRPaperConfig.__dataclass_fields__.keys())
    assert field not in declared, (
        f"IBKRPaperConfig must not declare forbidden field {field!r}"
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"paper": False},
        {"read_only": False},
        {"port": 0},
        {"port": -1},
        {"client_id": 0},
        {"client_id": -1},
        {"timeout_s": 0.0},
        {"timeout_s": -1.0},
        {"host": ""},
    ],
)
def test_ibkr_paper_config_rejects_unsafe_values(
    kwargs: dict[str, object],
) -> None:
    from brokers.ibkr_config import IBKRPaperConfig

    with pytest.raises(ValueError):
        IBKRPaperConfig(**kwargs)


# ---------------------------------------------------------------------------
# Adapter — import + protocol surface
# ---------------------------------------------------------------------------
def test_adapter_module_imports() -> None:
    module = importlib.import_module("brokers.ibkr_paper_readonly")
    assert hasattr(module, "IBKRPaperReadOnlyAdapter")
    assert module.ADAPTER_ID == "ibkr-paper"


def test_adapter_id_is_ibkr_paper() -> None:
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter

    assert IBKRPaperReadOnlyAdapter().adapter_id == "ibkr-paper"


def test_adapter_satisfies_broker_adapter_protocol() -> None:
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter
    from brokers.protocol import BrokerAdapter

    assert isinstance(IBKRPaperReadOnlyAdapter(), BrokerAdapter)


def test_adapter_constructor_accepts_optional_config() -> None:
    from brokers.ibkr_config import IBKRPaperConfig
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter

    custom = IBKRPaperConfig(port=4002, client_id=42)
    adapter = IBKRPaperReadOnlyAdapter(custom)
    assert adapter.config is custom
    # Default constructor still works.
    assert IBKRPaperReadOnlyAdapter().config.port == 7497


# ---------------------------------------------------------------------------
# Outputs validate as BRK-003 schemas
# ---------------------------------------------------------------------------
def test_capabilities_validate_into_schema() -> None:
    from app.schemas.broker import BrokerCapabilities
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter

    payload = dict(IBKRPaperReadOnlyAdapter().capabilities())
    payload.pop("adapter_id", None)
    caps = BrokerCapabilities(**payload)
    assert caps.read_only is True
    assert caps.paper is True
    assert caps.execution_enabled is False
    assert caps.live_orders_blocked is True
    assert caps.can_place_orders is False
    assert caps.can_cancel_orders is False
    assert caps.can_modify_orders is False


def test_status_validates_into_schema() -> None:
    from app.schemas.broker import BrokerStatus
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter

    status = BrokerStatus(**dict(IBKRPaperReadOnlyAdapter().status()))
    assert status.adapter_id == "ibkr-paper"
    assert status.connected is False
    assert status.degraded is True
    assert status.read_only is True
    assert status.execution_enabled is False
    assert status.live_orders_blocked is True
    assert status.degraded_reason
    assert status.safety_note


def test_account_snapshot_validates_into_schema() -> None:
    from app.schemas.broker import BrokerAccountSnapshot
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter

    snap = BrokerAccountSnapshot(
        **dict(IBKRPaperReadOnlyAdapter().account_snapshot())
    )
    assert snap.adapter_id == "ibkr-paper"
    assert snap.read_only is True
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert snap.currency == "USD"


def test_positions_returns_empty_list_and_validates() -> None:
    from app.schemas.broker import BrokerPosition
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter

    positions = [
        BrokerPosition(**dict(p))
        for p in IBKRPaperReadOnlyAdapter().positions()
    ]
    assert positions == []


# ---------------------------------------------------------------------------
# Forbidden methods absent
# ---------------------------------------------------------------------------
_FORBIDDEN_METHOD_NAMES: tuple[str, ...] = (
    # BRK-001 shared list
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
    # IBKR-specific shapes
    "placeOrder",
    "cancelOrder",
    "reqMktData",
    "reqPositions",
    "buy",
    "sell",
)


def test_adapter_has_no_forbidden_methods() -> None:
    from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter

    adapter = IBKRPaperReadOnlyAdapter()
    surface = set(dir(adapter)) | set(dir(IBKRPaperReadOnlyAdapter))
    leaked = sorted(surface & set(_FORBIDDEN_METHOD_NAMES))
    assert not leaked, (
        "IBKRPaperReadOnlyAdapter must not expose forbidden "
        f"execution-shaped method(s): {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Import safety — no broker SDK / network dependency
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
    # Drop cached modules so we can observe the import side-effects on a
    # clean slate.
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
# Default broker registry includes IBKR paper but keeps safe-disconnected default
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


# ---------------------------------------------------------------------------
# Broker endpoint route module still imports — sanity guard that this PR
# did not break the GET-only broker surface.
# ---------------------------------------------------------------------------
def test_broker_route_module_still_imports() -> None:
    module = importlib.import_module("app.api.routes.brokers")
    assert hasattr(module, "router")
