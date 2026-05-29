from __future__ import annotations

"""SIG-UNIVERSE-001 — Read-only scanner/watchlist universe presets.

This module defines deterministic, offline symbol universe collections for
MellyTrade's scanner and watchlist panels.

Design constraints:
- No network calls.
- No broker imports.
- No secrets or account IDs.
- No execution or order language in public function names.
- No mutation side effects.
- No persistence.
- All public outputs are immutable tuples.
- Labels are symbol identifiers only — no trading instructions.
"""

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# SymbolUniverseItem
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SymbolUniverseItem:
    """A single entry in a scanner/watchlist universe.

    All fields are read-only.  This type carries no execution semantics,
    order intent, or trading instructions.
    """

    symbol: str
    name: str
    asset_class: str
    venue_hint: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    enabled: bool = True


# ---------------------------------------------------------------------------
# Universe definitions
# ---------------------------------------------------------------------------

_AI_MEGA_CAPS: tuple[SymbolUniverseItem, ...] = (
    SymbolUniverseItem(
        symbol="NVDA",
        name="NVIDIA Corporation",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "semiconductors", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="GOOGL",
        name="Alphabet Inc. (Class A)",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "tech", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="AMZN",
        name="Amazon.com Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "cloud", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="MSFT",
        name="Microsoft Corporation",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "cloud", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="AAPL",
        name="Apple Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("tech", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="META",
        name="Meta Platforms Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "social", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="TSLA",
        name="Tesla Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ev", "ai", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="AMD",
        name="Advanced Micro Devices Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "semiconductors", "large_cap"),
    ),
    SymbolUniverseItem(
        symbol="AVGO",
        name="Broadcom Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "semiconductors", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="ORCL",
        name="Oracle Corporation",
        asset_class="equity",
        venue_hint="NYSE",
        tags=("ai", "cloud", "large_cap"),
    ),
    SymbolUniverseItem(
        symbol="NFLX",
        name="Netflix Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("streaming", "ai", "large_cap"),
    ),
    SymbolUniverseItem(
        symbol="INTC",
        name="Intel Corporation",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("semiconductors", "large_cap"),
    ),
    SymbolUniverseItem(
        symbol="PLTR",
        name="Palantir Technologies Inc.",
        asset_class="equity",
        venue_hint="NYSE",
        tags=("ai", "data", "mid_cap"),
    ),
    SymbolUniverseItem(
        symbol="SMCI",
        name="Super Micro Computer Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "servers", "mid_cap"),
    ),
    SymbolUniverseItem(
        symbol="ARM",
        name="Arm Holdings plc",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "semiconductors", "large_cap"),
    ),
)

_XTB_CFD_WATCHLIST: tuple[SymbolUniverseItem, ...] = (
    SymbolUniverseItem(
        symbol="US100",
        name="NASDAQ 100 Index CFD",
        asset_class="index_cfd",
        venue_hint="XTB",
        tags=("index", "us", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="US500",
        name="S&P 500 Index CFD",
        asset_class="index_cfd",
        venue_hint="XTB",
        tags=("index", "us", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="US30",
        name="Dow Jones Industrial Average CFD",
        asset_class="index_cfd",
        venue_hint="XTB",
        tags=("index", "us", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="DE40",
        name="DAX 40 Index CFD",
        asset_class="index_cfd",
        venue_hint="XTB",
        tags=("index", "europe", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="EU50",
        name="Euro Stoxx 50 Index CFD",
        asset_class="index_cfd",
        venue_hint="XTB",
        tags=("index", "europe", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="UK100",
        name="FTSE 100 Index CFD",
        asset_class="index_cfd",
        venue_hint="XTB",
        tags=("index", "uk", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="XAUUSD",
        name="Gold vs US Dollar",
        asset_class="commodity",
        venue_hint="XTB",
        tags=("commodity", "precious_metals", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="OIL.WTI",
        name="WTI Crude Oil CFD",
        asset_class="commodity",
        venue_hint="XTB",
        tags=("commodity", "energy", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="NATGAS",
        name="Natural Gas CFD",
        asset_class="commodity",
        venue_hint="XTB",
        tags=("commodity", "energy", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="EURUSD",
        name="Euro vs US Dollar",
        asset_class="fx",
        venue_hint="XTB",
        tags=("fx", "major"),
    ),
    SymbolUniverseItem(
        symbol="GBPUSD",
        name="British Pound vs US Dollar",
        asset_class="fx",
        venue_hint="XTB",
        tags=("fx", "major"),
    ),
    SymbolUniverseItem(
        symbol="USDJPY",
        name="US Dollar vs Japanese Yen",
        asset_class="fx",
        venue_hint="XTB",
        tags=("fx", "major"),
    ),
    SymbolUniverseItem(
        symbol="BTCUSD",
        name="Bitcoin vs US Dollar",
        asset_class="crypto",
        venue_hint="XTB",
        tags=("crypto", "cfd"),
    ),
    SymbolUniverseItem(
        symbol="ETHUSD",
        name="Ethereum vs US Dollar",
        asset_class="crypto",
        venue_hint="XTB",
        tags=("crypto", "cfd"),
    ),
)

_CORE_MACRO: tuple[SymbolUniverseItem, ...] = (
    SymbolUniverseItem(
        symbol="EURUSD",
        name="Euro vs US Dollar",
        asset_class="fx",
        tags=("fx", "major"),
    ),
    SymbolUniverseItem(
        symbol="GBPUSD",
        name="British Pound vs US Dollar",
        asset_class="fx",
        tags=("fx", "major"),
    ),
    SymbolUniverseItem(
        symbol="USDJPY",
        name="US Dollar vs Japanese Yen",
        asset_class="fx",
        tags=("fx", "major"),
    ),
    SymbolUniverseItem(
        symbol="XAUUSD",
        name="Gold vs US Dollar",
        asset_class="commodity",
        tags=("commodity", "precious_metals"),
    ),
    SymbolUniverseItem(
        symbol="OIL.WTI",
        name="WTI Crude Oil",
        asset_class="commodity",
        tags=("commodity", "energy"),
    ),
    SymbolUniverseItem(
        symbol="BTCUSD",
        name="Bitcoin vs US Dollar",
        asset_class="crypto",
        tags=("crypto",),
    ),
    SymbolUniverseItem(
        symbol="ETHUSD",
        name="Ethereum vs US Dollar",
        asset_class="crypto",
        tags=("crypto",),
    ),
    SymbolUniverseItem(
        symbol="US500",
        name="S&P 500 Index",
        asset_class="index",
        tags=("index", "us"),
    ),
    SymbolUniverseItem(
        symbol="DE40",
        name="DAX 40 Index",
        asset_class="index",
        tags=("index", "europe"),
    ),
)

_POLISH_EU_WATCHLIST: tuple[SymbolUniverseItem, ...] = (
    SymbolUniverseItem(
        symbol="PKN",
        name="PKN Orlen SA",
        asset_class="equity",
        venue_hint="GPW",
        tags=("polish", "energy", "large_cap"),
    ),
    SymbolUniverseItem(
        symbol="CDR",
        name="CD Projekt SA",
        asset_class="equity",
        venue_hint="GPW",
        tags=("polish", "gaming", "mid_cap"),
    ),
    SymbolUniverseItem(
        symbol="DAX",
        name="DAX 40 Index",
        asset_class="index",
        venue_hint="XETRA",
        tags=("europe", "index", "germany"),
    ),
    SymbolUniverseItem(
        symbol="EURPLN",
        name="Euro vs Polish Zloty",
        asset_class="fx",
        tags=("fx", "pln", "europe"),
    ),
    SymbolUniverseItem(
        symbol="USDPLN",
        name="US Dollar vs Polish Zloty",
        asset_class="fx",
        tags=("fx", "pln", "us"),
    ),
)

# Default demo universe — a curated subset drawn from the above universes.
# No duplicates.  Kept small for a focused demo experience.
_DEFAULT_DEMO: tuple[SymbolUniverseItem, ...] = (
    SymbolUniverseItem(
        symbol="NVDA",
        name="NVIDIA Corporation",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "semiconductors", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="AAPL",
        name="Apple Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("tech", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="MSFT",
        name="Microsoft Corporation",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ai", "cloud", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="TSLA",
        name="Tesla Inc.",
        asset_class="equity",
        venue_hint="NASDAQ",
        tags=("ev", "ai", "mega_cap"),
    ),
    SymbolUniverseItem(
        symbol="EURUSD",
        name="Euro vs US Dollar",
        asset_class="fx",
        tags=("fx", "major"),
    ),
    SymbolUniverseItem(
        symbol="XAUUSD",
        name="Gold vs US Dollar",
        asset_class="commodity",
        tags=("commodity", "precious_metals"),
    ),
    SymbolUniverseItem(
        symbol="GBPUSD",
        name="British Pound vs US Dollar",
        asset_class="fx",
        tags=("fx", "major"),
    ),
    SymbolUniverseItem(
        symbol="USDJPY",
        name="US Dollar vs Japanese Yen",
        asset_class="fx",
        tags=("fx", "major"),
    ),
)

# Registry — the authoritative mapping of name → universe tuple.
_UNIVERSES: dict[str, tuple[SymbolUniverseItem, ...]] = {
    "ai_mega_caps": _AI_MEGA_CAPS,
    "xtb_cfd_watchlist": _XTB_CFD_WATCHLIST,
    "core_macro": _CORE_MACRO,
    "polish_eu_watchlist": _POLISH_EU_WATCHLIST,
    "default_demo": _DEFAULT_DEMO,
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalize_universe_name(name: str) -> str:
    """Normalise a universe name to its canonical lowercase-underscore form.

    Strips whitespace and lowercases the input.  Does not validate whether
    the name exists in the registry.
    """
    return name.strip().lower()


def list_universes() -> dict[str, tuple[SymbolUniverseItem, ...]]:
    """Return a copy of the full universe registry.

    The returned dict is a shallow copy; the inner tuples are immutable.
    """
    return dict(_UNIVERSES)


def get_universe(name: str) -> tuple[SymbolUniverseItem, ...]:
    """Return the universe for *name*.

    Parameters
    ----------
    name:
        Universe name.  Case-insensitive; whitespace-stripped.

    Returns
    -------
    tuple[SymbolUniverseItem, ...]
        The matching universe.  Falls back to ``default_demo`` if *name* is
        not found in the registry (safe degradation — never raises for unknown
        names).
    """
    canonical = normalize_universe_name(name)
    return _UNIVERSES.get(canonical, _DEFAULT_DEMO)


def list_symbols_for_universe(name: str) -> tuple[str, ...]:
    """Return deduplicated display symbols for *name* (case-insensitive).

    Unknown universe names fall back to ``default_demo``.  Empty symbols are
    excluded.  Original display casing is preserved.  Order matches the
    universe definition order; first occurrence wins on duplicates.
    """
    items = get_universe(name)
    seen: set[str] = set()
    symbols: list[str] = []
    for item in items:
        if not item.symbol:
            continue
        key = item.symbol.upper()
        if key in seen:
            continue
        seen.add(key)
        symbols.append(item.symbol)
    return tuple(symbols)


def list_default_symbols() -> tuple[str, ...]:
    """Return deduplicated display symbols for the ``default_demo`` universe."""
    return list_symbols_for_universe("default_demo")
