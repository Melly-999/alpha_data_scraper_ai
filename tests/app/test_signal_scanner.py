from __future__ import annotations

import inspect
import json
import subprocess
import sys

import pytest
from pydantic import ValidationError

from app.schemas.signal_scanner import (
    SignalAction,
    SignalScannerBatch,
    SignalScannerResult,
)
from app.services.signal_scanner import scan_symbols


FORBIDDEN_FIELDS = [
    "order_id",
    "account_id",
    "execution_id",
    "trade_id",
    "place_order",
    "broker_execute",
    "secret",
    "token",
    "api_key",
]


def test_signal_scanner_result_safe_defaults() -> None:
    result = SignalScannerResult(
        symbol=" eurusd ",
        action=SignalAction.WATCH,
        confidence=50,
        reason=" scanner foundation ",
    )

    assert result.symbol == "eurusd"
    assert result.action == SignalAction.WATCH
    assert result.confidence == 50
    assert result.reason == "scanner foundation"
    assert result.risk_allowed is False
    assert result.execution_mode == "dry_run_only"
    assert result.requires_human_review is True
    assert result.source == "scanner"
    assert result.timestamp is not None


@pytest.mark.parametrize("symbol", ["", "   "])
def test_signal_scanner_result_rejects_blank_symbol(symbol: str) -> None:
    with pytest.raises(ValidationError):
        SignalScannerResult(
            symbol=symbol,
            action=SignalAction.WATCH,
            confidence=50,
            reason="advisory only",
        )


@pytest.mark.parametrize("reason", ["", "   "])
def test_signal_scanner_result_rejects_blank_reason(reason: str) -> None:
    with pytest.raises(ValidationError):
        SignalScannerResult(
            symbol="EURUSD",
            action=SignalAction.WATCH,
            confidence=50,
            reason=reason,
        )


@pytest.mark.parametrize("confidence", [-1, 101])
def test_signal_scanner_result_rejects_out_of_range_confidence(
    confidence: float,
) -> None:
    with pytest.raises(ValidationError):
        SignalScannerResult(
            symbol="EURUSD",
            action=SignalAction.WATCH,
            confidence=confidence,
            reason="advisory only",
        )


def test_signal_scanner_result_rejects_risk_allowed_true() -> None:
    with pytest.raises(ValidationError):
        SignalScannerResult(
            symbol="EURUSD",
            action=SignalAction.WATCH,
            confidence=50,
            reason="advisory only",
            risk_allowed=True,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("execution_mode", ["live", "dry_run", "execute_now"])
def test_signal_scanner_result_rejects_non_dry_run_execution_mode(
    execution_mode: str,
) -> None:
    with pytest.raises(ValidationError):
        SignalScannerResult(
            symbol="EURUSD",
            action=SignalAction.WATCH,
            confidence=50,
            reason="advisory only",
            execution_mode=execution_mode,  # type: ignore[arg-type]
        )


def test_signal_scanner_result_rejects_requires_human_review_false() -> None:
    with pytest.raises(ValidationError):
        SignalScannerResult(
            symbol="EURUSD",
            action=SignalAction.WATCH,
            confidence=50,
            reason="advisory only",
            requires_human_review=False,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("field_name", FORBIDDEN_FIELDS)
def test_signal_scanner_result_rejects_forbidden_extra_fields(
    field_name: str,
) -> None:
    payload = {
        "symbol": "EURUSD",
        "action": "WATCH",
        "confidence": 50,
        "reason": "advisory only",
        field_name: "unsafe",
    }
    with pytest.raises(ValidationError):
        SignalScannerResult.model_validate(payload)


def test_scan_symbols_returns_read_only_dry_run_only_batch() -> None:
    batch = scan_symbols([" eurusd ", "GBPUSD", "  "])

    assert isinstance(batch, SignalScannerBatch)
    assert batch.read_only is True
    assert batch.execution_mode == "dry_run_only"
    assert len(batch.results) == 2
    assert [result.symbol for result in batch.results] == ["EURUSD", "GBPUSD"]
    for result in batch.results:
        assert result.risk_allowed is False
        assert result.execution_mode == "dry_run_only"
        assert result.requires_human_review is True
        assert result.source == "scanner"


def test_scan_symbols_empty_input_returns_empty_batch() -> None:
    batch = scan_symbols([])
    assert batch.read_only is True
    assert batch.execution_mode == "dry_run_only"
    assert batch.results == []


def test_scan_symbols_has_no_broker_order_execution_public_methods() -> None:
    import app.services.signal_scanner as scanner_module

    public_functions = [
        name
        for name, obj in inspect.getmembers(scanner_module, inspect.isfunction)
        if not name.startswith("_")
    ]
    assert public_functions == ["scan_symbols"]

    forbidden_segments = [
        "order",
        "execute",
        "broker",
        "trade",
        "live",
        "autotrade",
        "connect",
    ]
    assert not any(
        segment in name.lower()
        for name in public_functions
        for segment in forbidden_segments
        if name != "scan_symbols"
    )


def test_signal_scanner_module_does_not_import_broker_or_network_libraries() -> None:
    script = """
import json
import sys
import app.services.signal_scanner  # noqa: F401

forbidden = [
    "ib_insync",
    "ibapi",
    "MetaTrader5",
    "requests",
    "httpx",
    "websockets",
    "alpaca",
    "ccxt",
]

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
    assert present == []


def test_scanner_output_has_no_forbidden_keys() -> None:
    batch = scan_symbols(["EURUSD"])
    payload = batch.model_dump()

    def _keys(value: object) -> set[str]:
        collected: set[str] = set()
        if isinstance(value, dict):
            for key, nested in value.items():
                collected.add(key)
                collected.update(_keys(nested))
        elif isinstance(value, list):
            for item in value:
                collected.update(_keys(item))
        return collected

    keys = _keys(payload)
    for forbidden in FORBIDDEN_FIELDS:
        assert forbidden not in keys
    assert payload["read_only"] is True
    assert payload["execution_mode"] == "dry_run_only"
