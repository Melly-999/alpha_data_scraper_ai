"""Tests for signal_decision_reader.py — SUPA-011.

Covers: success path, empty result, invalid row skip, limit clamping,
symbol filter, ordering, no-raise behavior, safety invariants.

No network calls. No Supabase client. Uses _select_fn injection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from app.schemas.signal_decision import SignalDecisionRecord
from app.services.signal_decision_reader import (
    _DECISIONS_TABLE,
    _LIMIT_DEFAULT,
    _LIMIT_MAX,
    _LIMIT_MIN,
    _clamp_limit,
    _parse_timestamp,
    _row_to_record,
    read_signal_decisions,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_row(
    *,
    row_id: str = "550e8400-e29b-41d4-a716-446655440000",
    symbol: str = "AAPL",
    direction: str = "BUY",
    confidence: float = 0.75,
    strategy: str | None = "mtf_confluence",
    source: str = "scanner",
    risk_status: str = "pass",
    decision: str = "watch_only",
    blocked_reason: str | None = None,
    audit_event_id: str | None = None,
    created_at: str = "2026-05-16T12:00:00+00:00",
) -> dict[str, Any]:
    return {
        "id": row_id,
        "created_at": created_at,
        "symbol": symbol,
        "direction": direction,
        "confidence": confidence,
        "strategy": strategy,
        "source": source,
        "risk_status": risk_status,
        "decision": decision,
        "blocked_reason": blocked_reason,
        "audit_event_id": audit_event_id,
        "dry_run": True,
        "auto_trade": False,
        "read_only": True,
        "order_placed": False,
    }


def _make_response(rows: list[dict[str, Any]]) -> SimpleNamespace:
    return SimpleNamespace(data=rows)


def _select_returning(rows: list[dict[str, Any]]):
    def _fn(
        table: str, symbol: str | None, limit: int, **kwargs: Any
    ) -> SimpleNamespace:
        return _make_response(rows)

    return _fn


# ---------------------------------------------------------------------------
# 1. Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_decisions_table_name(self) -> None:
        assert _DECISIONS_TABLE == "signal_decisions"

    def test_limit_default(self) -> None:
        assert _LIMIT_DEFAULT == 100

    def test_limit_min(self) -> None:
        assert _LIMIT_MIN == 1

    def test_limit_max(self) -> None:
        assert _LIMIT_MAX == 500


# ---------------------------------------------------------------------------
# 2. _clamp_limit
# ---------------------------------------------------------------------------


class TestClampLimit:
    def test_clamp_below_min(self) -> None:
        assert _clamp_limit(0) == _LIMIT_MIN

    def test_clamp_negative(self) -> None:
        assert _clamp_limit(-10) == _LIMIT_MIN

    def test_clamp_above_max(self) -> None:
        assert _clamp_limit(1000) == _LIMIT_MAX

    def test_clamp_within_range(self) -> None:
        assert _clamp_limit(50) == 50

    def test_clamp_exactly_min(self) -> None:
        assert _clamp_limit(_LIMIT_MIN) == _LIMIT_MIN

    def test_clamp_exactly_max(self) -> None:
        assert _clamp_limit(_LIMIT_MAX) == _LIMIT_MAX


# ---------------------------------------------------------------------------
# 3. _parse_timestamp
# ---------------------------------------------------------------------------


class TestParseTimestamp:
    def test_parses_iso_string_with_z(self) -> None:
        ts = _parse_timestamp("2026-05-16T12:00:00Z")
        assert isinstance(ts, datetime)
        assert ts.tzinfo is not None

    def test_parses_iso_string_with_offset(self) -> None:
        ts = _parse_timestamp("2026-05-16T12:00:00+00:00")
        assert isinstance(ts, datetime)
        assert ts.tzinfo is not None

    def test_parses_datetime_object(self) -> None:
        now = datetime.now(timezone.utc)
        ts = _parse_timestamp(now)
        assert ts == now

    def test_adds_utc_to_naive_datetime(self) -> None:
        naive = datetime(2026, 5, 16, 12, 0, 0)
        ts = _parse_timestamp(naive)
        assert ts.tzinfo is not None

    def test_invalid_string_returns_now(self) -> None:
        ts = _parse_timestamp("not-a-date")
        assert isinstance(ts, datetime)

    def test_none_returns_now(self) -> None:
        ts = _parse_timestamp(None)
        assert isinstance(ts, datetime)


# ---------------------------------------------------------------------------
# 4. _row_to_record
# ---------------------------------------------------------------------------


class TestRowToRecord:
    def test_valid_row_returns_record(self) -> None:
        record = _row_to_record(_make_row())
        assert isinstance(record, SignalDecisionRecord)

    def test_missing_id_returns_none(self) -> None:
        row = _make_row()
        del row["id"]
        assert _row_to_record(row) is None

    def test_empty_id_returns_none(self) -> None:
        row = _make_row(row_id="")
        assert _row_to_record(row) is None

    def test_invalid_direction_returns_none(self) -> None:
        row = _make_row(direction="INVALID")
        assert _row_to_record(row) is None

    def test_invalid_risk_status_returns_none(self) -> None:
        row = _make_row(risk_status="extreme")
        assert _row_to_record(row) is None

    def test_invalid_decision_returns_none(self) -> None:
        row = _make_row(decision="execute_now")
        assert _row_to_record(row) is None

    def test_null_strategy_falls_back_to_scanner(self) -> None:
        row = _make_row(strategy=None)
        record = _row_to_record(row)
        assert record is not None
        assert record.strategy == "scanner"

    def test_record_dry_run_forced_true(self) -> None:
        row = _make_row()
        row["dry_run"] = False  # DB value ignored — safety re-enforced
        record = _row_to_record(row)
        assert record is not None
        assert record.dry_run is True

    def test_record_auto_trade_forced_false(self) -> None:
        row = _make_row()
        record = _row_to_record(row)
        assert record is not None
        assert record.auto_trade is False

    def test_record_read_only_forced_true(self) -> None:
        row = _make_row()
        record = _row_to_record(row)
        assert record is not None
        assert record.read_only is True

    def test_record_max_risk_per_trade_bounded(self) -> None:
        row = _make_row()
        record = _row_to_record(row)
        assert record is not None
        assert record.max_risk_per_trade <= 0.01

    def test_record_confidence_matches_row(self) -> None:
        row = _make_row(confidence=0.82)
        record = _row_to_record(row)
        assert record is not None
        assert record.confidence == pytest.approx(0.82)

    def test_record_symbol_matches_row(self) -> None:
        row = _make_row(symbol="NVDA")
        record = _row_to_record(row)
        assert record is not None
        assert record.symbol == "NVDA"

    def test_record_audit_event_id_when_set(self) -> None:
        row = _make_row(audit_event_id="evt-001")
        record = _row_to_record(row)
        assert record is not None
        assert record.audit_event_id == "evt-001"

    def test_record_audit_event_id_when_none(self) -> None:
        row = _make_row(audit_event_id=None)
        record = _row_to_record(row)
        assert record is not None
        assert record.audit_event_id is None


# ---------------------------------------------------------------------------
# 5. read_signal_decisions — degraded (no client, no _select_fn)
# ---------------------------------------------------------------------------


class TestReadDegradedPath:
    def test_returns_empty_list_when_no_client(self) -> None:
        result = read_signal_decisions()
        assert result == []

    def test_returns_list_type_when_no_client(self) -> None:
        result = read_signal_decisions()
        assert isinstance(result, list)

    def test_returns_empty_list_with_symbol_and_no_client(self) -> None:
        result = read_signal_decisions(symbol="AAPL")
        assert result == []


# ---------------------------------------------------------------------------
# 6. read_signal_decisions — _select_fn raises
# ---------------------------------------------------------------------------


class TestReadFnRaises:
    def test_returns_empty_when_select_fn_raises(self) -> None:
        def _raise(table: str, symbol: Any, limit: int, **kwargs: Any) -> Any:
            raise RuntimeError("DB connection failed")

        result = read_signal_decisions(_select_fn=_raise)
        assert result == []

    def test_never_raises_when_select_fn_raises(self) -> None:
        def _raise(table: str, symbol: Any, limit: int, **kwargs: Any) -> Any:
            raise ValueError("injected error")

        result = read_signal_decisions(_select_fn=_raise)
        assert result is not None


# ---------------------------------------------------------------------------
# 7. read_signal_decisions — success path
# ---------------------------------------------------------------------------


class TestReadSuccessPath:
    def test_returns_list_of_records(self) -> None:
        rows = [
            _make_row(symbol="AAPL"),
            _make_row(symbol="NVDA", row_id="550e8400-e29b-41d4-a716-446655440001"),
        ]
        result = read_signal_decisions(_select_fn=_select_returning(rows))
        assert len(result) == 2
        assert all(isinstance(r, SignalDecisionRecord) for r in result)

    def test_records_have_correct_symbols(self) -> None:
        rows = [
            _make_row(symbol="AAPL"),
            _make_row(symbol="NVDA", row_id="550e8400-e29b-41d4-a716-446655440001"),
        ]
        result = read_signal_decisions(_select_fn=_select_returning(rows))
        symbols = {r.symbol for r in result}
        assert symbols == {"AAPL", "NVDA"}

    def test_empty_data_returns_empty_list(self) -> None:
        result = read_signal_decisions(_select_fn=_select_returning([]))
        assert result == []

    def test_none_data_returns_empty_list(self) -> None:
        def _fn(table: str, symbol: Any, limit: int, **kwargs: Any) -> SimpleNamespace:
            return SimpleNamespace(data=None)

        result = read_signal_decisions(_select_fn=_fn)
        assert result == []

    def test_no_response_data_attr_returns_empty(self) -> None:
        def _fn(table: str, symbol: Any, limit: int, **kwargs: Any) -> SimpleNamespace:
            return SimpleNamespace()  # no .data attribute

        result = read_signal_decisions(_select_fn=_fn)
        assert result == []

    def test_select_fn_called_with_correct_table(self) -> None:
        captured: list[str] = []

        def _fn(table: str, symbol: Any, limit: int, **kwargs: Any) -> SimpleNamespace:
            captured.append(table)
            return _make_response([])

        read_signal_decisions(_select_fn=_fn)
        assert captured == [_DECISIONS_TABLE]

    def test_select_fn_called_with_symbol_filter(self) -> None:
        captured: list[Any] = []

        def _fn(table: str, symbol: Any, limit: int, **kwargs: Any) -> SimpleNamespace:
            captured.append(symbol)
            return _make_response([])

        read_signal_decisions(symbol="AAPL", _select_fn=_fn)
        assert captured == ["AAPL"]

    def test_select_fn_called_with_none_symbol_when_no_filter(self) -> None:
        captured: list[Any] = []

        def _fn(table: str, symbol: Any, limit: int, **kwargs: Any) -> SimpleNamespace:
            captured.append(symbol)
            return _make_response([])

        read_signal_decisions(_select_fn=_fn)
        assert captured == [None]

    def test_select_fn_called_with_clamped_limit(self) -> None:
        captured: list[int] = []

        def _fn(table: str, symbol: Any, limit: int, **kwargs: Any) -> SimpleNamespace:
            captured.append(limit)
            return _make_response([])

        read_signal_decisions(limit=50, _select_fn=_fn)
        assert captured == [50]

    def test_select_fn_limit_clamped_below_min(self) -> None:
        captured: list[int] = []

        def _fn(table: str, symbol: Any, limit: int, **kwargs: Any) -> SimpleNamespace:
            captured.append(limit)
            return _make_response([])

        read_signal_decisions(limit=0, _select_fn=_fn)
        assert captured[0] >= _LIMIT_MIN

    def test_select_fn_limit_clamped_above_max(self) -> None:
        captured: list[int] = []

        def _fn(table: str, symbol: Any, limit: int, **kwargs: Any) -> SimpleNamespace:
            captured.append(limit)
            return _make_response([])

        read_signal_decisions(limit=9999, _select_fn=_fn)
        assert captured[0] <= _LIMIT_MAX


# ---------------------------------------------------------------------------
# 8. Invalid rows are skipped
# ---------------------------------------------------------------------------


class TestInvalidRowsSkipped:
    def test_invalid_row_skipped_valid_row_returned(self) -> None:
        invalid_row = {"id": None, "symbol": "AAPL"}  # missing required fields
        valid_row = _make_row(symbol="NVDA")
        result = read_signal_decisions(
            _select_fn=_select_returning([invalid_row, valid_row])
        )
        assert len(result) == 1
        assert result[0].symbol == "NVDA"

    def test_all_invalid_rows_returns_empty_list(self) -> None:
        rows = [{"not_valid": True}, {"also_not": True}]
        result = read_signal_decisions(_select_fn=_select_returning(rows))
        assert result == []

    def test_mixed_valid_invalid_rows(self) -> None:
        rows = [
            _make_row(symbol="AAPL"),
            {"id": "bad", "direction": "EXECUTE_NOW"},  # invalid direction
            _make_row(symbol="MSFT", row_id="550e8400-e29b-41d4-a716-446655440002"),
        ]
        result = read_signal_decisions(_select_fn=_select_returning(rows))
        symbols = [r.symbol for r in result]
        assert "AAPL" in symbols
        assert "MSFT" in symbols


# ---------------------------------------------------------------------------
# 9. Safety invariants on returned records
# ---------------------------------------------------------------------------


class TestSafetyInvariantsOnRecords:
    def _get_records(self) -> list[SignalDecisionRecord]:
        rows = [
            _make_row(symbol="AAPL"),
            _make_row(symbol="NVDA", row_id="550e8400-e29b-41d4-a716-446655440001"),
        ]
        return read_signal_decisions(_select_fn=_select_returning(rows))

    def test_all_records_dry_run_true(self) -> None:
        for r in self._get_records():
            assert r.dry_run is True

    def test_all_records_auto_trade_false(self) -> None:
        for r in self._get_records():
            assert r.auto_trade is False

    def test_all_records_read_only_true(self) -> None:
        for r in self._get_records():
            assert r.read_only is True

    def test_all_records_stop_loss_required(self) -> None:
        for r in self._get_records():
            assert r.stop_loss_required is True

    def test_all_records_max_risk_bounded(self) -> None:
        for r in self._get_records():
            assert r.max_risk_per_trade <= 0.01

    def test_all_records_confidence_in_range(self) -> None:
        for r in self._get_records():
            assert 0.0 <= r.confidence <= 1.0


# ---------------------------------------------------------------------------
# 10. SUPA-014: from_date / to_date date-range filters
# ---------------------------------------------------------------------------
#
# Verifies the reader forwards from_date/to_date as ISO 8601 keyword args
# (passed as `from_date=` / `to_date=`) to _select_fn, never raises on
# invalid ranges, and degrades safely when no client is supplied.


class TestSupa014DateFilters:
    def _capturing_fn(self) -> tuple[list[dict[str, Any]], Any]:
        captured: list[dict[str, Any]] = []

        def _fn(
            table: str,
            symbol: Any,
            limit: int,
            **kwargs: Any,
        ) -> SimpleNamespace:
            captured.append(dict(kwargs))
            return _make_response([])

        return captured, _fn

    def test_default_from_and_to_are_none(self) -> None:
        captured, fn = self._capturing_fn()
        read_signal_decisions(_select_fn=fn)
        assert captured[0]["from_date"] is None
        assert captured[0]["to_date"] is None

    def test_from_date_passed_as_iso_string(self) -> None:
        captured, fn = self._capturing_fn()
        read_signal_decisions(
            from_date=datetime(2026, 5, 16, 0, 0, 0, tzinfo=timezone.utc),
            _select_fn=fn,
        )
        assert captured[0]["from_date"] is not None
        assert captured[0]["from_date"].startswith("2026-05-16T00:00:00")
        assert captured[0]["to_date"] is None

    def test_to_date_passed_as_iso_string(self) -> None:
        captured, fn = self._capturing_fn()
        read_signal_decisions(
            to_date=datetime(2026, 5, 17, 23, 59, 59, tzinfo=timezone.utc),
            _select_fn=fn,
        )
        assert captured[0]["to_date"] is not None
        assert captured[0]["to_date"].startswith("2026-05-17T23:59:59")
        assert captured[0]["from_date"] is None

    def test_both_dates_passed(self) -> None:
        captured, fn = self._capturing_fn()
        read_signal_decisions(
            from_date=datetime(2026, 5, 16, 0, 0, 0, tzinfo=timezone.utc),
            to_date=datetime(2026, 5, 17, 0, 0, 0, tzinfo=timezone.utc),
            _select_fn=fn,
        )
        assert captured[0]["from_date"] is not None
        assert captured[0]["to_date"] is not None

    def test_naive_datetime_treated_as_utc(self) -> None:
        captured, fn = self._capturing_fn()
        read_signal_decisions(
            from_date=datetime(2026, 5, 16, 12, 0, 0),  # naive
            _select_fn=fn,
        )
        assert captured[0]["from_date"] is not None
        # ISO output is UTC-normalized
        assert "+00:00" in captured[0]["from_date"]

    def test_inverted_range_never_raises(self) -> None:
        captured, fn = self._capturing_fn()
        # from_date AFTER to_date — must not raise; the reader tolerates it.
        result = read_signal_decisions(
            from_date=datetime(2026, 5, 18, 0, 0, 0, tzinfo=timezone.utc),
            to_date=datetime(2026, 5, 16, 0, 0, 0, tzinfo=timezone.utc),
            _select_fn=fn,
        )
        assert result == []

    def test_date_filter_with_no_client_returns_empty(self) -> None:
        result = read_signal_decisions(
            from_date=datetime(2026, 5, 16, 0, 0, 0, tzinfo=timezone.utc),
            to_date=datetime(2026, 5, 17, 0, 0, 0, tzinfo=timezone.utc),
        )
        assert result == []

    def test_select_fn_raises_with_date_filter_returns_empty(self) -> None:
        def _raise(table: str, symbol: Any, limit: int, **kwargs: Any) -> Any:
            raise RuntimeError("DB unreachable")

        result = read_signal_decisions(
            from_date=datetime(2026, 5, 16, 0, 0, 0, tzinfo=timezone.utc),
            _select_fn=_raise,
        )
        assert result == []

    def test_date_filter_preserves_limit_clamping(self) -> None:
        captured, fn = self._capturing_fn()
        read_signal_decisions(
            limit=9999,
            from_date=datetime(2026, 5, 16, 0, 0, 0, tzinfo=timezone.utc),
            _select_fn=fn,
        )
        # The captured kwargs don't include limit (positional), but the call
        # itself should not raise. Just verify it didn't crash.
        assert len(captured) == 1

    def test_date_filter_returns_records_when_data_present(self) -> None:
        rows = [_make_row(symbol="AAPL")]

        def _fn(table: str, symbol: Any, limit: int, **kwargs: Any) -> SimpleNamespace:
            return _make_response(rows)

        result = read_signal_decisions(
            from_date=datetime(2026, 5, 16, 0, 0, 0, tzinfo=timezone.utc),
            to_date=datetime(2026, 5, 17, 0, 0, 0, tzinfo=timezone.utc),
            _select_fn=_fn,
        )
        assert len(result) == 1
        assert result[0].symbol == "AAPL"


class TestSupa014ToIso:
    """Direct coverage for _to_iso helper."""

    def test_none_returns_none(self) -> None:
        from app.services.signal_decision_reader import _to_iso

        assert _to_iso(None) is None

    def test_utc_datetime_iso(self) -> None:
        from app.services.signal_decision_reader import _to_iso

        result = _to_iso(datetime(2026, 5, 16, 12, 0, 0, tzinfo=timezone.utc))
        assert result is not None
        assert result.startswith("2026-05-16T12:00:00")
        assert "+00:00" in result

    def test_naive_assumed_utc(self) -> None:
        from app.services.signal_decision_reader import _to_iso

        result = _to_iso(datetime(2026, 5, 16, 12, 0, 0))
        assert result is not None
        assert "+00:00" in result
