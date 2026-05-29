from __future__ import annotations

"""Tests for app.services.signal_universe (SIG-UNIVERSE-001).

Validates:
- all expected universe names exist
- key symbols present in each universe
- default_demo contains reasonable symbols
- symbols are deduplicated case-insensitively
- no empty symbols
- all items enabled by default
- all public outputs are tuples
- unknown universe name degrades safely (returns default_demo)
- no forbidden fields/terms in the module or its outputs
- module does not import network or broker libraries
"""

import inspect
import json
import subprocess
import sys

import pytest

from app.services.signal_universe import (
    SymbolUniverseItem,
    get_universe,
    list_default_symbols,
    list_symbols_for_universe,
    list_universes,
    normalize_universe_name,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXPECTED_UNIVERSE_NAMES = {
    "ai_mega_caps",
    "xtb_cfd_watchlist",
    "core_macro",
    "polish_eu_watchlist",
    "default_demo",
}

FORBIDDEN_FIELD_NAMES = [
    "order_id",
    "account_id",
    "execution_id",
    "place_order",
    "broker_execute",
    "api_key",
    "secret",
    "token",
    "password",
]

FORBIDDEN_BROKER_LIBS = [
    "requests",
    "httpx",
    "ib_insync",
    "ibapi",
    "MetaTrader5",
    "yfinance",
    "alpaca",
    "ccxt",
    "websockets",
]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_all_expected_universes_exist() -> None:
    universes = list_universes()
    assert EXPECTED_UNIVERSE_NAMES.issubset(set(universes.keys()))


def test_list_universes_returns_dict() -> None:
    result = list_universes()
    assert isinstance(result, dict)


def test_list_universes_values_are_tuples() -> None:
    for name, items in list_universes().items():
        assert isinstance(items, tuple), f"Universe '{name}' is not a tuple"


def test_list_universes_items_are_symbol_universe_items() -> None:
    for name, items in list_universes().items():
        for item in items:
            assert isinstance(
                item, SymbolUniverseItem
            ), f"Item in '{name}' is not a SymbolUniverseItem"


# ---------------------------------------------------------------------------
# ai_mega_caps
# ---------------------------------------------------------------------------


def test_ai_mega_caps_contains_required_symbols() -> None:
    symbols = list_symbols_for_universe("ai_mega_caps")
    for expected in ("NVDA", "GOOGL", "AMZN", "MSFT", "AAPL", "META", "TSLA"):
        assert expected in symbols, f"Expected {expected!r} in ai_mega_caps"


def test_ai_mega_caps_contains_extended_symbols() -> None:
    symbols = list_symbols_for_universe("ai_mega_caps")
    for expected in ("AMD", "AVGO", "ORCL", "NFLX", "INTC", "PLTR", "SMCI", "ARM"):
        assert expected in symbols, f"Expected {expected!r} in ai_mega_caps"


def test_ai_mega_caps_asset_class_equity() -> None:
    items = get_universe("ai_mega_caps")
    for item in items:
        assert (
            item.asset_class == "equity"
        ), f"Unexpected asset_class {item.asset_class!r} for {item.symbol}"


# ---------------------------------------------------------------------------
# xtb_cfd_watchlist
# ---------------------------------------------------------------------------


def test_xtb_cfd_watchlist_contains_required_symbols() -> None:
    symbols = list_symbols_for_universe("xtb_cfd_watchlist")
    for expected in (
        "US100",
        "US500",
        "XAUUSD",
        "OIL.WTI",
        "NATGAS",
        "EURUSD",
        "GBPUSD",
        "USDJPY",
        "BTCUSD",
        "ETHUSD",
    ):
        assert expected in symbols, f"Expected {expected!r} in xtb_cfd_watchlist"


def test_xtb_cfd_watchlist_contains_indices() -> None:
    symbols = list_symbols_for_universe("xtb_cfd_watchlist")
    for expected in ("US30", "DE40", "EU50", "UK100"):
        assert expected in symbols, f"Expected {expected!r} in xtb_cfd_watchlist"


# ---------------------------------------------------------------------------
# core_macro
# ---------------------------------------------------------------------------


def test_core_macro_contains_fx_symbols() -> None:
    symbols = list_symbols_for_universe("core_macro")
    for expected in ("EURUSD", "GBPUSD", "USDJPY"):
        assert expected in symbols, f"Expected {expected!r} in core_macro"


def test_core_macro_contains_commodities() -> None:
    symbols = list_symbols_for_universe("core_macro")
    for expected in ("XAUUSD", "OIL.WTI"):
        assert expected in symbols, f"Expected {expected!r} in core_macro"


def test_core_macro_contains_crypto() -> None:
    symbols = list_symbols_for_universe("core_macro")
    for expected in ("BTCUSD", "ETHUSD"):
        assert expected in symbols, f"Expected {expected!r} in core_macro"


# ---------------------------------------------------------------------------
# polish_eu_watchlist
# ---------------------------------------------------------------------------


def test_polish_eu_watchlist_contains_required_symbols() -> None:
    symbols = list_symbols_for_universe("polish_eu_watchlist")
    for expected in ("PKN", "CDR", "DAX", "EURPLN", "USDPLN"):
        assert expected in symbols, f"Expected {expected!r} in polish_eu_watchlist"


# ---------------------------------------------------------------------------
# default_demo
# ---------------------------------------------------------------------------


def test_default_demo_has_reasonable_symbols() -> None:
    symbols = list_default_symbols()
    assert len(symbols) >= 4, "default_demo should have at least 4 symbols"


def test_default_demo_returns_tuple() -> None:
    result = list_default_symbols()
    assert isinstance(result, tuple)


def test_default_demo_contains_key_symbols() -> None:
    symbols = list_default_symbols()
    # At minimum expect NVDA and EURUSD to anchor the demo experience
    assert "NVDA" in symbols
    assert "EURUSD" in symbols


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "universe_name",
    [
        "ai_mega_caps",
        "xtb_cfd_watchlist",
        "core_macro",
        "polish_eu_watchlist",
        "default_demo",
    ],
)
def test_symbols_are_deduplicated(universe_name: str) -> None:
    symbols = list_symbols_for_universe(universe_name)
    upper_symbols = [s.upper() for s in symbols]
    assert len(upper_symbols) == len(
        set(upper_symbols)
    ), f"Duplicate symbols found in universe '{universe_name}'"


# ---------------------------------------------------------------------------
# No empty symbols
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "universe_name",
    [
        "ai_mega_caps",
        "xtb_cfd_watchlist",
        "core_macro",
        "polish_eu_watchlist",
        "default_demo",
    ],
)
def test_no_empty_symbols(universe_name: str) -> None:
    symbols = list_symbols_for_universe(universe_name)
    for s in symbols:
        assert (
            s and s.strip()
        ), f"Empty or blank symbol found in universe '{universe_name}'"


# ---------------------------------------------------------------------------
# All items enabled by default
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "universe_name",
    [
        "ai_mega_caps",
        "xtb_cfd_watchlist",
        "core_macro",
        "polish_eu_watchlist",
        "default_demo",
    ],
)
def test_all_items_enabled_by_default(universe_name: str) -> None:
    items = get_universe(universe_name)
    for item in items:
        assert (
            item.enabled is True
        ), f"Item {item.symbol!r} in '{universe_name}' has enabled=False"


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------


def test_get_universe_returns_tuple() -> None:
    result = get_universe("ai_mega_caps")
    assert isinstance(result, tuple)


def test_list_symbols_for_universe_returns_tuple() -> None:
    result = list_symbols_for_universe("core_macro")
    assert isinstance(result, tuple)


def test_symbol_items_are_frozen() -> None:
    """SymbolUniverseItem must be frozen (immutable)."""
    item = get_universe("default_demo")[0]
    with pytest.raises((AttributeError, TypeError)):
        item.symbol = "MUTATED"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Unknown universe name — safe degradation
# ---------------------------------------------------------------------------


def test_unknown_universe_name_returns_default_demo() -> None:
    result = get_universe("this_universe_does_not_exist")
    default = get_universe("default_demo")
    assert result == default, "Unknown universe name should fall back to default_demo"


def test_list_symbols_unknown_universe_returns_default_demo_symbols() -> None:
    result = list_symbols_for_universe("completely_unknown_universe_xyz")
    default = list_default_symbols()
    assert result == default


def test_unknown_universe_result_is_tuple() -> None:
    result = get_universe("unknown_xyz_abc")
    assert isinstance(result, tuple)


# ---------------------------------------------------------------------------
# normalize_universe_name
# ---------------------------------------------------------------------------


def test_normalize_universe_name_strips_and_lowercases() -> None:
    assert normalize_universe_name("  AI_Mega_Caps  ") == "ai_mega_caps"


def test_normalize_universe_name_empty_string() -> None:
    assert normalize_universe_name("") == ""


def test_normalize_universe_name_already_canonical() -> None:
    assert normalize_universe_name("default_demo") == "default_demo"


# ---------------------------------------------------------------------------
# No forbidden fields in SymbolUniverseItem
# ---------------------------------------------------------------------------


def test_symbol_universe_item_has_no_forbidden_fields() -> None:
    item_fields = {f.name for f in SymbolUniverseItem.__dataclass_fields__.values()}
    for forbidden in FORBIDDEN_FIELD_NAMES:
        assert (
            forbidden not in item_fields
        ), f"Forbidden field {forbidden!r} found in SymbolUniverseItem"


def test_symbol_universe_item_source_has_no_forbidden_terms() -> None:
    import app.services.signal_universe as universe_module

    source = inspect.getsource(universe_module)
    # Terms that must not appear as active code (outside of prohibition docs/comments).
    # We check the public API names specifically.
    public_names = [
        name
        for name, obj in inspect.getmembers(universe_module)
        if not name.startswith("_") and callable(obj)
    ]
    forbidden_function_segments = [
        "place_order",
        "broker_execute",
        "live_trade",
        "autotrade",
        "connect_live",
    ]
    for name in public_names:
        for segment in forbidden_function_segments:
            assert (
                segment not in name.lower()
            ), f"Forbidden segment {segment!r} found in public name {name!r}"


# ---------------------------------------------------------------------------
# No network or broker library imports
# ---------------------------------------------------------------------------


def test_signal_universe_module_does_not_import_forbidden_libraries() -> None:
    script = f"""
import json
import sys
import app.services.signal_universe  # noqa: F401

forbidden = {json.dumps(FORBIDDEN_BROKER_LIBS)}
present = [name for name in forbidden if name in sys.modules]
print(json.dumps(present))
"""
    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )
    present = json.loads(completed.stdout.strip())
    assert present == [], f"signal_universe imported forbidden libraries: {present}"


# ---------------------------------------------------------------------------
# Public API shape
# ---------------------------------------------------------------------------


def test_public_functions_are_limited_to_expected_set() -> None:
    import app.services.signal_universe as universe_module

    public_functions = {
        name
        for name, obj in inspect.getmembers(universe_module, inspect.isfunction)
        if not name.startswith("_") and obj.__module__ == universe_module.__name__
    }
    expected = {
        "get_universe",
        "list_universes",
        "list_default_symbols",
        "list_symbols_for_universe",
        "normalize_universe_name",
    }
    assert public_functions == expected, (
        f"Public functions mismatch.\n"
        f"  Expected: {sorted(expected)}\n"
        f"  Got:      {sorted(public_functions)}"
    )


def test_symbol_universe_item_is_exported() -> None:
    from app.services.signal_universe import SymbolUniverseItem as _Item

    assert _Item is SymbolUniverseItem
