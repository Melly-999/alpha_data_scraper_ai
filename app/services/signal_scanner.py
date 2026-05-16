from __future__ import annotations

from typing import Iterable

from app.schemas.signal_scanner import (
    SignalAction,
    SignalScannerBatch,
    SignalScannerResult,
)

# Deterministic demo rows keyed by normalised symbol.
# All entries are advisory-only; risk_allowed=False and execution_mode=dry_run_only
# are enforced by the SignalScannerResult schema — not overridable here.
# Unknown symbols fall back to WATCH / 50% / generic reason.
_DEMO_ROWS: dict[str, tuple[SignalAction, float, str]] = {
    "AAPL": (
        SignalAction.WATCH,
        62.0,
        "Trend intact above EMA50 — monitoring for breakout above resistance. "
        "Below 70% execution floor. Advisory watch only.",
    ),
    "NVDA": (
        SignalAction.LONG_SETUP,
        74.0,
        "Bullish momentum confirmed on H1 with RSI 58 and MACD cross. "
        "Higher-timeframe alignment present. Dry-run-only — human review required.",
    ),
    "MSFT": (
        SignalAction.HOLD,
        55.0,
        "Mixed timeframe signals — H4 bearish, D1 neutral. "
        "No identifiable edge. Below execution floor; no action.",
    ),
    "TSLA": (
        SignalAction.NO_TRADE,
        48.0,
        "Choppy price action with elevated ATR; timeframes conflicted. "
        "Risk gate would block — no trade.",
    ),
    "EURUSD": (
        SignalAction.WATCH,
        61.0,
        "Ranging session; waiting for momentum confirmation. "
        "Below 70% confidence floor. Watch-list only.",
    ),
    "XAUUSD": (
        SignalAction.SHORT_SETUP,
        71.0,
        "Gold stalling at resistance with bearish MACD divergence; macro tone cautious. "
        "Dry-run-eligible — requires human review before any consideration.",
    ),
    "GBPUSD": (
        SignalAction.HOLD,
        52.0,
        "No directional edge detected; mixed fundamentals. "
        "Confidence below threshold — holding.",
    ),
    "USDJPY": (
        SignalAction.WATCH,
        65.0,
        "Yen weakness persisting but signal in post-evaluation cooldown. "
        "Advisory watch only.",
    ),
}

_FALLBACK_ROW: tuple[SignalAction, float, str] = (
    SignalAction.WATCH,
    50.0,
    "Read-only SIG-001 scanner foundation. Advisory only. No execution.",
)


def _normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def scan_symbols(symbols: Iterable[str]) -> SignalScannerBatch:
    """Build a read-only advisory signal batch.

    This scanner is intentionally inert: no network calls, no broker calls,
    no persistence, no order intent, and no execution routes.
    Known symbols use deterministic demo rows; unknown symbols fall back to
    WATCH / 50% / generic reason.
    """
    results: list[SignalScannerResult] = []
    for raw_symbol in symbols:
        if raw_symbol is None:
            continue
        normalized = _normalize_symbol(str(raw_symbol))
        if not normalized:
            continue
        action, confidence, reason = _DEMO_ROWS.get(normalized, _FALLBACK_ROW)
        results.append(
            SignalScannerResult(
                symbol=normalized,
                action=action,
                confidence=confidence,
                reason=reason,
            )
        )

    return SignalScannerBatch(results=results)
