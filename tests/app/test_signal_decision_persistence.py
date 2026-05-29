"""Tests for signal_decision_persistence.py — SUPA-011.

Covers: success path, degraded path, _insert_fn injection, metadata safety,
payload key safety, safety invariants, no-raise behavior, write_audit_event
usage, and schema contract.

No network calls. No Supabase client. No execution semantics.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.schemas.audit_event import AuditEventRecord
from app.schemas.signal_decision import SignalDecisionRecord
from app.services.signal_decision_persistence import (
    _DECISIONS_TABLE,
    _SAFE_PAYLOAD_KEYS,
    _build_decision_payload,
    write_signal_decision,
)

# ---------------------------------------------------------------------------
# Forbidden key sets — mirrored from AuditEventCreate validators
# ---------------------------------------------------------------------------

_EXECUTION_KEYS: frozenset[str] = frozenset(
    {
        "place_order",
        "execute_trade",
        "broker_execute",
        "cancel_order",
        "modify_order",
        "enable_autotrade",
        "disable_dry_run",
        "connect_live",
    }
)

_CREDENTIAL_KEYS: frozenset[str] = frozenset(
    {
        "account_id",
        "order_id",
        "execution_id",
        "trade_id",
        "secret",
        "token",
        "api_key",
        "password",
        "credential",
        "service_role",
        "broker_id",
        "user_id",
        "client_id",
    }
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_record(
    *,
    record_id: str = "test-sdp-001",
    symbol: str = "AAPL",
    direction: str = "BUY",
    confidence: float = 0.75,
    source: str = "scanner",
    strategy: str = "mtf_confluence",
    risk_status: str = "pass",
    decision: str = "watch_only",
    blocked_reason: str | None = None,
    audit_event_id: str | None = None,
) -> SignalDecisionRecord:
    return SignalDecisionRecord(
        id=record_id,
        timestamp=datetime.now(timezone.utc),
        symbol=symbol,
        direction=direction,  # type: ignore[arg-type]
        confidence=confidence,
        source=source,
        strategy=strategy,
        risk_status=risk_status,  # type: ignore[arg-type]
        decision=decision,  # type: ignore[arg-type]
        blocked_reason=blocked_reason,
        audit_event_id=audit_event_id,
        dry_run=True,
        auto_trade=False,
        read_only=True,
        stop_loss_required=True,
        take_profit_required=True,
        max_risk_per_trade=0.01,
    )


# ---------------------------------------------------------------------------
# 1. Table name constant
# ---------------------------------------------------------------------------


class TestDecisionsTableConstant:
    def test_table_name_is_signal_decisions(self) -> None:
        assert _DECISIONS_TABLE == "signal_decisions"

    def test_table_name_has_no_schema_prefix(self) -> None:
        assert "." not in _DECISIONS_TABLE


# ---------------------------------------------------------------------------
# 2. Safe payload key set
# ---------------------------------------------------------------------------


class TestSafePayloadKeys:
    def test_safe_payload_keys_is_frozenset(self) -> None:
        assert isinstance(_SAFE_PAYLOAD_KEYS, frozenset)

    def test_no_execution_keys_in_safe_payload_keys(self) -> None:
        assert not (_SAFE_PAYLOAD_KEYS & _EXECUTION_KEYS)

    def test_no_credential_keys_in_safe_payload_keys(self) -> None:
        assert not (_SAFE_PAYLOAD_KEYS & _CREDENTIAL_KEYS)

    def test_safety_columns_present(self) -> None:
        assert "dry_run" in _SAFE_PAYLOAD_KEYS
        assert "auto_trade" in _SAFE_PAYLOAD_KEYS
        assert "read_only" in _SAFE_PAYLOAD_KEYS
        assert "order_placed" in _SAFE_PAYLOAD_KEYS

    def test_signal_fields_present(self) -> None:
        assert "symbol" in _SAFE_PAYLOAD_KEYS
        assert "direction" in _SAFE_PAYLOAD_KEYS
        assert "confidence" in _SAFE_PAYLOAD_KEYS
        assert "risk_status" in _SAFE_PAYLOAD_KEYS
        assert "decision" in _SAFE_PAYLOAD_KEYS


# ---------------------------------------------------------------------------
# 3. Payload builder
# ---------------------------------------------------------------------------


class TestBuildDecisionPayload:
    def test_payload_keys_are_exactly_safe_set(self) -> None:
        record = _make_record()
        payload = _build_decision_payload(record)
        assert set(payload.keys()) == _SAFE_PAYLOAD_KEYS

    def test_payload_symbol_matches_record(self) -> None:
        record = _make_record(symbol="NVDA")
        assert _build_decision_payload(record)["symbol"] == "NVDA"

    def test_payload_direction_matches_record(self) -> None:
        record = _make_record(direction="SELL")
        assert _build_decision_payload(record)["direction"] == "SELL"

    def test_payload_confidence_matches_record(self) -> None:
        record = _make_record(confidence=0.82)
        assert _build_decision_payload(record)["confidence"] == pytest.approx(0.82)

    def test_payload_strategy_matches_record(self) -> None:
        record = _make_record(strategy="rsi_reversal")
        assert _build_decision_payload(record)["strategy"] == "rsi_reversal"

    def test_payload_risk_status_matches_record(self) -> None:
        record = _make_record(risk_status="blocked")
        assert _build_decision_payload(record)["risk_status"] == "blocked"

    def test_payload_decision_matches_record(self) -> None:
        record = _make_record(decision="blocked")
        assert _build_decision_payload(record)["decision"] == "blocked"

    def test_payload_blocked_reason_when_none(self) -> None:
        record = _make_record(blocked_reason=None)
        assert _build_decision_payload(record)["blocked_reason"] is None

    def test_payload_blocked_reason_when_set(self) -> None:
        record = _make_record(blocked_reason="Confidence below threshold.")
        assert (
            _build_decision_payload(record)["blocked_reason"]
            == "Confidence below threshold."
        )

    def test_payload_audit_event_id_when_none(self) -> None:
        record = _make_record(audit_event_id=None)
        assert _build_decision_payload(record)["audit_event_id"] is None

    def test_payload_audit_event_id_when_set(self) -> None:
        record = _make_record(audit_event_id="evt-safety-001")
        assert _build_decision_payload(record)["audit_event_id"] == "evt-safety-001"

    def test_payload_dry_run_forced_true(self) -> None:
        record = _make_record()
        assert _build_decision_payload(record)["dry_run"] is True

    def test_payload_auto_trade_forced_false(self) -> None:
        record = _make_record()
        assert _build_decision_payload(record)["auto_trade"] is False

    def test_payload_read_only_forced_true(self) -> None:
        record = _make_record()
        assert _build_decision_payload(record)["read_only"] is True

    def test_payload_order_placed_forced_false(self) -> None:
        record = _make_record()
        assert _build_decision_payload(record)["order_placed"] is False

    def test_no_execution_keys_in_payload(self) -> None:
        payload = _build_decision_payload(_make_record())
        assert not (set(payload.keys()) & _EXECUTION_KEYS)

    def test_no_credential_keys_in_payload(self) -> None:
        payload = _build_decision_payload(_make_record())
        assert not (set(payload.keys()) & _CREDENTIAL_KEYS)


# ---------------------------------------------------------------------------
# 4. Degraded path — no client, no _insert_fn
# ---------------------------------------------------------------------------


class TestDegradedPath:
    def test_returns_audit_event_record_when_no_client(self) -> None:
        record = _make_record()
        result = write_signal_decision(record)
        assert isinstance(result, AuditEventRecord)

    def test_persisted_false_when_no_client(self) -> None:
        record = _make_record()
        result = write_signal_decision(record)
        assert result.persisted is False

    def test_degraded_true_when_no_client(self) -> None:
        record = _make_record()
        result = write_signal_decision(record)
        assert result.degraded is True

    def test_degraded_reason_present_when_no_client(self) -> None:
        record = _make_record()
        result = write_signal_decision(record)
        assert result.degraded_reason is not None
        assert len(result.degraded_reason) > 0

    def test_event_type_correct_when_degraded(self) -> None:
        record = _make_record()
        result = write_signal_decision(record)
        assert result.event_type == "signal_decision_persisted"

    def test_source_scanner_when_degraded(self) -> None:
        record = _make_record()
        result = write_signal_decision(record)
        assert result.source == "scanner"

    def test_read_only_true_when_degraded(self) -> None:
        record = _make_record()
        result = write_signal_decision(record)
        assert result.read_only is True

    def test_dry_run_true_when_degraded(self) -> None:
        record = _make_record()
        result = write_signal_decision(record)
        assert result.dry_run is True


# ---------------------------------------------------------------------------
# 5. Success path — _insert_fn injection
# ---------------------------------------------------------------------------


class TestSuccessPath:
    def test_returns_audit_event_record_on_success(self) -> None:
        record = _make_record()
        result = write_signal_decision(record, _insert_fn=lambda t, p: None)
        assert isinstance(result, AuditEventRecord)

    def test_persisted_true_on_success(self) -> None:
        record = _make_record()
        result = write_signal_decision(record, _insert_fn=lambda t, p: None)
        assert result.persisted is True

    def test_degraded_false_on_success(self) -> None:
        record = _make_record()
        result = write_signal_decision(record, _insert_fn=lambda t, p: None)
        assert result.degraded is False

    def test_event_type_correct_on_success(self) -> None:
        record = _make_record()
        result = write_signal_decision(record, _insert_fn=lambda t, p: None)
        assert result.event_type == "signal_decision_persisted"

    def test_source_scanner_on_success(self) -> None:
        record = _make_record()
        result = write_signal_decision(record, _insert_fn=lambda t, p: None)
        assert result.source == "scanner"

    def test_read_only_true_on_success(self) -> None:
        record = _make_record()
        result = write_signal_decision(record, _insert_fn=lambda t, p: None)
        assert result.read_only is True

    def test_dry_run_true_on_success(self) -> None:
        record = _make_record()
        result = write_signal_decision(record, _insert_fn=lambda t, p: None)
        assert result.dry_run is True

    def test_insert_fn_called_with_correct_table(self) -> None:
        captured: list[str] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(table)

        write_signal_decision(_make_record(), _insert_fn=_capture)
        assert captured == [_DECISIONS_TABLE]

    def test_insert_fn_receives_safe_payload_keys(self) -> None:
        captured: list[dict[str, Any]] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(payload)

        write_signal_decision(_make_record(), _insert_fn=_capture)
        assert set(captured[0].keys()) == _SAFE_PAYLOAD_KEYS

    def test_insert_fn_receives_correct_symbol(self) -> None:
        captured: list[dict[str, Any]] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(payload)

        write_signal_decision(_make_record(symbol="MSFT"), _insert_fn=_capture)
        assert captured[0]["symbol"] == "MSFT"

    def test_insert_fn_receives_correct_direction(self) -> None:
        captured: list[dict[str, Any]] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(payload)

        write_signal_decision(_make_record(direction="SELL"), _insert_fn=_capture)
        assert captured[0]["direction"] == "SELL"

    def test_insert_fn_payload_dry_run_forced_true(self) -> None:
        captured: list[dict[str, Any]] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(payload)

        write_signal_decision(_make_record(), _insert_fn=_capture)
        assert captured[0]["dry_run"] is True

    def test_insert_fn_payload_auto_trade_forced_false(self) -> None:
        captured: list[dict[str, Any]] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(payload)

        write_signal_decision(_make_record(), _insert_fn=_capture)
        assert captured[0]["auto_trade"] is False

    def test_insert_fn_payload_read_only_forced_true(self) -> None:
        captured: list[dict[str, Any]] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(payload)

        write_signal_decision(_make_record(), _insert_fn=_capture)
        assert captured[0]["read_only"] is True

    def test_insert_fn_payload_order_placed_forced_false(self) -> None:
        captured: list[dict[str, Any]] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(payload)

        write_signal_decision(_make_record(), _insert_fn=_capture)
        assert captured[0]["order_placed"] is False

    def test_insert_fn_payload_no_execution_keys(self) -> None:
        captured: list[dict[str, Any]] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(payload)

        write_signal_decision(_make_record(), _insert_fn=_capture)
        assert not (set(captured[0].keys()) & _EXECUTION_KEYS)

    def test_insert_fn_payload_no_credential_keys(self) -> None:
        captured: list[dict[str, Any]] = []

        def _capture(table: str, payload: dict[str, Any]) -> None:
            captured.append(payload)

        write_signal_decision(_make_record(), _insert_fn=_capture)
        assert not (set(captured[0].keys()) & _CREDENTIAL_KEYS)


# ---------------------------------------------------------------------------
# 6. _insert_fn raises — degraded path
# ---------------------------------------------------------------------------


class TestInsertFnRaises:
    def test_returns_record_when_insert_fn_raises(self) -> None:
        def _raise(table: str, payload: dict[str, Any]) -> None:
            raise RuntimeError("DB error")

        result = write_signal_decision(_make_record(), _insert_fn=_raise)
        assert isinstance(result, AuditEventRecord)

    def test_degraded_true_when_insert_fn_raises(self) -> None:
        def _raise(table: str, payload: dict[str, Any]) -> None:
            raise RuntimeError("DB error")

        result = write_signal_decision(_make_record(), _insert_fn=_raise)
        assert result.degraded is True

    def test_persisted_false_when_insert_fn_raises(self) -> None:
        def _raise(table: str, payload: dict[str, Any]) -> None:
            raise RuntimeError("DB error")

        result = write_signal_decision(_make_record(), _insert_fn=_raise)
        assert result.persisted is False

    def test_never_raises_when_insert_fn_raises(self) -> None:
        def _raise(table: str, payload: dict[str, Any]) -> None:
            raise RuntimeError("unexpected failure")

        # Must not propagate the exception.
        result = write_signal_decision(_make_record(), _insert_fn=_raise)
        assert result is not None


# ---------------------------------------------------------------------------
# 7. No-raise contract
# ---------------------------------------------------------------------------


class TestNoRaiseBehavior:
    def test_never_raises_no_client(self) -> None:
        result = write_signal_decision(_make_record(), client=None, _insert_fn=None)
        assert result is not None

    def test_never_raises_with_bad_client(self) -> None:
        bad_client = MagicMock()
        bad_client.table.side_effect = RuntimeError("bad client")
        result = write_signal_decision(_make_record(), client=bad_client)
        assert result is not None

    def test_never_raises_with_exception_in_insert_fn(self) -> None:
        def _raise(*args: Any) -> None:
            raise ValueError("injected error")

        result = write_signal_decision(_make_record(), _insert_fn=_raise)
        assert result is not None


# ---------------------------------------------------------------------------
# 8. write_audit_event is called on success
# ---------------------------------------------------------------------------


class TestWriteAuditEventUsage:
    def test_write_audit_event_called_on_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[Any] = []

        def _mock_write_audit(
            event: Any, *, client: Any = None, _insert_fn: Any = None
        ) -> AuditEventRecord:
            calls.append(event)
            return AuditEventRecord(
                event_type=event.event_type,
                severity="info",
                source="scanner",
                message="mock",
                metadata={},
                read_only=True,
                dry_run=True,
                persisted=False,
                degraded=True,
                degraded_reason="mock",
            )

        monkeypatch.setattr(
            "app.services.signal_decision_persistence.write_audit_event",
            _mock_write_audit,
        )
        write_signal_decision(_make_record(), _insert_fn=lambda t, p: None)
        assert len(calls) == 1

    def test_audit_event_has_correct_event_type(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[Any] = []

        def _mock_write_audit(
            event: Any, *, client: Any = None, _insert_fn: Any = None
        ) -> AuditEventRecord:
            calls.append(event)
            return AuditEventRecord(
                event_type=event.event_type,
                severity="info",
                source="scanner",
                message="mock",
                metadata={},
                read_only=True,
                dry_run=True,
                persisted=False,
                degraded=True,
                degraded_reason="mock",
            )

        monkeypatch.setattr(
            "app.services.signal_decision_persistence.write_audit_event",
            _mock_write_audit,
        )
        write_signal_decision(_make_record(), _insert_fn=lambda t, p: None)
        assert calls[0].event_type == "signal_decision_persisted"

    def test_audit_event_metadata_has_no_execution_keys(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[Any] = []

        def _mock_write_audit(
            event: Any, *, client: Any = None, _insert_fn: Any = None
        ) -> AuditEventRecord:
            calls.append(event)
            return AuditEventRecord(
                event_type=event.event_type,
                severity="info",
                source="scanner",
                message="mock",
                metadata={},
                read_only=True,
                dry_run=True,
                persisted=False,
                degraded=True,
                degraded_reason="mock",
            )

        monkeypatch.setattr(
            "app.services.signal_decision_persistence.write_audit_event",
            _mock_write_audit,
        )
        write_signal_decision(_make_record(), _insert_fn=lambda t, p: None)
        assert not (set(calls[0].metadata.keys()) & _EXECUTION_KEYS)

    def test_write_audit_event_not_called_on_degraded_no_client(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """write_audit_event should not be called when there is no client."""
        calls: list[Any] = []

        def _mock_write_audit(event: Any, **kwargs: Any) -> AuditEventRecord:  # type: ignore[return]
            calls.append(event)

        monkeypatch.setattr(
            "app.services.signal_decision_persistence.write_audit_event",
            _mock_write_audit,
        )
        write_signal_decision(_make_record(), client=None, _insert_fn=None)
        assert calls == []


# ---------------------------------------------------------------------------
# 9. Various record configurations
# ---------------------------------------------------------------------------


class TestVariousRecordConfigurations:
    @pytest.mark.parametrize(
        "decision",
        ["dry_run_allowed", "blocked", "watch_only", "no_action"],
    )
    def test_all_decision_types_accepted(self, decision: str) -> None:
        result = write_signal_decision(
            _make_record(decision=decision),
            _insert_fn=lambda t, p: None,
        )
        assert isinstance(result, AuditEventRecord)
        assert result.persisted is True

    @pytest.mark.parametrize("risk_status", ["pass", "warn", "blocked", "unknown"])
    def test_all_risk_statuses_accepted(self, risk_status: str) -> None:
        result = write_signal_decision(
            _make_record(risk_status=risk_status),
            _insert_fn=lambda t, p: None,
        )
        assert isinstance(result, AuditEventRecord)
        assert result.persisted is True

    @pytest.mark.parametrize("direction", ["BUY", "SELL", "HOLD", "UNKNOWN"])
    def test_all_directions_accepted(self, direction: str) -> None:
        result = write_signal_decision(
            _make_record(direction=direction),
            _insert_fn=lambda t, p: None,
        )
        assert isinstance(result, AuditEventRecord)
        assert result.persisted is True

    def test_with_blocked_reason(self) -> None:
        result = write_signal_decision(
            _make_record(blocked_reason="Max risk exceeded."),
            _insert_fn=lambda t, p: None,
        )
        assert result.persisted is True

    def test_with_audit_event_id(self) -> None:
        result = write_signal_decision(
            _make_record(audit_event_id="evt-safety-001"),
            _insert_fn=lambda t, p: None,
        )
        assert result.persisted is True

    def test_confidence_boundary_low(self) -> None:
        result = write_signal_decision(
            _make_record(confidence=0.0),
            _insert_fn=lambda t, p: None,
        )
        assert result.persisted is True

    def test_confidence_boundary_high(self) -> None:
        result = write_signal_decision(
            _make_record(confidence=1.0),
            _insert_fn=lambda t, p: None,
        )
        assert result.persisted is True
