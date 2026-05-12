from __future__ import annotations

from typing import Iterable

from app.schemas.signal_scanner import (
    SignalAction,
    SignalScannerBatch,
    SignalScannerResult,
)


def _normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def scan_symbols(symbols: Iterable[str]) -> SignalScannerBatch:
    """Build a read-only advisory signal batch.

    This scanner is intentionally inert: no network calls, no broker calls,
    no persistence, no order intent, and no execution routes.
    """

    results: list[SignalScannerResult] = []
    for raw_symbol in symbols:
        if raw_symbol is None:
            continue
        normalized = _normalize_symbol(str(raw_symbol))
        if not normalized:
            continue
        results.append(
            SignalScannerResult(
                symbol=normalized,
                action=SignalAction.WATCH,
                confidence=50.0,
                reason=(
                    "Read-only SIG-001 scanner foundation. Advisory only. "
                    "No execution."
                ),
            )
        )

    return SignalScannerBatch(results=results)
