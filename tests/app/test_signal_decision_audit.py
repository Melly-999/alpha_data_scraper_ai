"""Tests for SUPA-010: signal decision audit event emitter.

No real network calls — all Supabase interactions are replaced by injectable
_insert_fn or a None client to trigger the degraded path.

Test categories:
  1.  Return shape — single AuditEventRecord
  2.  Event type — signal_decision_evaluated
  3.  Source — "scanner"
  4.  Severity — "info"
  5.  Safety invariants — read_only=True, dry_run=True on every path
  6.  Success path — persisted=True, degraded=False with fake _insert_fn
  7.  Degraded path — persisted=False, degraded=True when no client/no _insert_fn
  8.  Insert failure — does not raise; degrades gracefully
  9.  Injectable _insert_fn — called exactly once, targets audit_events
  10. Metadata safety — only safe keys; explicit absence of forbidden fields
  11. Payload safety — read_only, dry_run, source, event_type in every payload
  12. Endpoint resilience — GET /signals/decisions returns 200 if audit write fails
  13. Non-blocking — audit failure never blocks the decisions response
  14. Symbol filter threading — symbol_filter reflected in metadata safely
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from app.schemas.audit_event import AuditEventRecord
from app.services.signal_decision_audit import emit_signal_decision_event

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Forbidden metadata keys — must never appear (matches audit_event.py).
_FORBIDDEN_KEYS = frozenset(
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
    }
)

# Execution-shaped metadata keys — must never appear.
_EXECUTION_KEYS = frozenset(
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

# Signal-data keys that must never appear in metadata.
_SIGNAL_DATA_KEYS = frozenset(
    {
        "confidence",
        "direction",
        "price",
        "bid",
        "ask",
        "open",
        "close",
        "high",
        "low",
        "pnl",
        "position",
        "balance",
    }
)


def _make_fake_insert_fn() -> tuple[Any, list[tuple[str, dict[str, Any]]]]:
    """Return (fn, calls) — fn records every (table, payload) call in calls."""
    calls: list[tuple[str, dict[str, Any]]] = []

    def _fn(table: str, payload: dict[str, Any]) -> Any:
        calls.append((table, dict(payload)))
        response = MagicMock()
        response.data = [{"id": "sdaudit-test-id-001"}]
        return response

    return _fn, calls


def _make_failing_insert_fn() -> Any:
    """Return an _insert_fn that always raises RuntimeError."""

    def _fn(table: str, payload: dict[str, Any]) -> Any:
        raise RuntimeError("simulated Supabase signal decision insert failure")

    return _fn


# ---------------------------------------------------------------------------
# 1. Return shape
# ---------------------------------------------------------------------------


class TestReturnShape:
    def test_returns_audit_event_record(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert isinstance(result, AuditEventRecord)

    def test_returns_single_record_not_list(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert not isinstance(result, list)

    def test_returns_record_with_insert_fn(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(10, "AAPL", _insert_fn=fn)
        assert isinstance(result, AuditEventRecord)

    def test_returns_record_with_zero_decisions(self) -> None:
        result = emit_signal_decision_event(0, None)
        assert isinstance(result, AuditEventRecord)

    def test_returns_record_with_symbol_filter(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(3, "EURUSD", _insert_fn=fn)
        assert isinstance(result, AuditEventRecord)


# ---------------------------------------------------------------------------
# 2. Event type — signal_decision_evaluated
# ---------------------------------------------------------------------------


class TestEventType:
    def test_event_type_on_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(5, None, _insert_fn=fn)
        assert result.event_type == "signal_decision_evaluated"

    def test_event_type_on_degraded_path(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert result.event_type == "signal_decision_evaluated"

    def test_event_type_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.event_type == "signal_decision_evaluated"

    def test_event_type_with_symbol_filter(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(2, "NVDA", _insert_fn=fn)
        assert result.event_type == "signal_decision_evaluated"


# ---------------------------------------------------------------------------
# 3. Source — "scanner"
# ---------------------------------------------------------------------------


class TestSource:
    def test_source_scanner_on_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(5, None, _insert_fn=fn)
        assert result.source == "scanner"

    def test_source_scanner_on_degraded_path(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert result.source == "scanner"

    def test_source_scanner_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.source == "scanner"


# ---------------------------------------------------------------------------
# 4. Severity — "info"
# ---------------------------------------------------------------------------


class TestSeverity:
    def test_severity_info_on_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(5, None, _insert_fn=fn)
        assert result.severity == "info"

    def test_severity_info_on_degraded_path(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert result.severity == "info"

    def test_severity_info_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.severity == "info"


# ---------------------------------------------------------------------------
# 5. Safety invariants — read_only=True, dry_run=True on every path
# ---------------------------------------------------------------------------


class TestSafetyInvariants:
    def test_read_only_true_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(5, None, _insert_fn=fn)
        assert result.read_only is True

    def test_dry_run_true_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(5, None, _insert_fn=fn)
        assert result.dry_run is True

    def test_read_only_true_degraded_path(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert result.read_only is True

    def test_dry_run_true_degraded_path(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert result.dry_run is True

    def test_read_only_true_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.read_only is True

    def test_dry_run_true_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.dry_run is True


# ---------------------------------------------------------------------------
# 6. Success path
# ---------------------------------------------------------------------------


class TestSuccessPath:
    def test_persisted_true_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(5, None, _insert_fn=fn)
        assert result.persisted is True

    def test_degraded_false_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(5, None, _insert_fn=fn)
        assert result.degraded is False

    def test_id_assigned_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(5, None, _insert_fn=fn)
        assert result.id is not None

    def test_degraded_reason_none_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_signal_decision_event(5, None, _insert_fn=fn)
        assert result.degraded_reason is None


# ---------------------------------------------------------------------------
# 7. Degraded path
# ---------------------------------------------------------------------------


class TestDegradedPath:
    def test_degraded_true_when_no_client_no_fn(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert result.degraded is True

    def test_persisted_false_when_degraded(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert result.persisted is False

    def test_degraded_reason_set_when_degraded(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert result.degraded_reason is not None
        assert len(result.degraded_reason) > 0

    def test_returns_correct_event_type_when_degraded(self) -> None:
        result = emit_signal_decision_event(5, None)
        assert result.event_type == "signal_decision_evaluated"

    def test_no_exception_raised_when_no_client(self) -> None:
        # Must not raise — verify by calling and asserting return type.
        result = emit_signal_decision_event(100, "AAPL")
        assert isinstance(result, AuditEventRecord)


# ---------------------------------------------------------------------------
# 8. Insert failure — does not raise; degrades gracefully
# ---------------------------------------------------------------------------


class TestInsertFailure:
    def test_no_exception_raised_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert isinstance(result, AuditEventRecord)

    def test_degraded_true_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.degraded is True

    def test_persisted_false_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.persisted is False

    def test_degraded_reason_contains_exception_message(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.degraded_reason is not None
        assert (
            "simulated Supabase signal decision insert failure" in result.degraded_reason
        )

    def test_read_only_preserved_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.read_only is True

    def test_dry_run_preserved_on_insert_failure(self) -> None:
        result = emit_signal_decision_event(
            5, None, _insert_fn=_make_failing_insert_fn()
        )
        assert result.dry_run is True


# ---------------------------------------------------------------------------
# 9. Injectable _insert_fn — called exactly once, targets audit_events
# ---------------------------------------------------------------------------


class TestInjectableInsertFn:
    def test_insert_fn_called_exactly_once(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert len(calls) == 1

    def test_insert_fn_targets_audit_events_table(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert calls[0][0] == "audit_events"

    def test_insert_fn_not_called_on_degraded_path(self) -> None:
        fn, calls = _make_fake_insert_fn()
        # No _insert_fn, no client — degraded path, no insert attempt.
        emit_signal_decision_event(5, None)
        assert len(calls) == 0

    def test_insert_fn_called_once_with_symbol_filter(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(3, "EURUSD", _insert_fn=fn)
        assert len(calls) == 1


# ---------------------------------------------------------------------------
# 10. Metadata safety
# ---------------------------------------------------------------------------


class TestMetadataSafety:
    def test_metadata_contains_decision_count(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(7, None, _insert_fn=fn)
        assert calls[0][1]["metadata"]["decision_count"] == 7

    def test_metadata_decision_count_zero(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(0, None, _insert_fn=fn)
        assert calls[0][1]["metadata"]["decision_count"] == 0

    def test_metadata_contains_symbol_filter_none(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert "symbol_filter" in calls[0][1]["metadata"]
        assert calls[0][1]["metadata"]["symbol_filter"] is None

    def test_metadata_symbol_filter_stored_correctly(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(3, "AAPL", _insert_fn=fn)
        assert calls[0][1]["metadata"]["symbol_filter"] == "AAPL"

    def test_metadata_contains_degraded_flag(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert "degraded" in calls[0][1]["metadata"]

    def test_metadata_keys_are_only_allowed_set(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        metadata_keys = set(calls[0][1]["metadata"].keys())
        assert metadata_keys <= {"decision_count", "symbol_filter", "degraded"}

    def test_no_forbidden_keys_in_metadata(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        metadata = calls[0][1].get("metadata", {})
        forbidden = _FORBIDDEN_KEYS & metadata.keys()
        assert not forbidden, f"Forbidden keys found: {forbidden}"

    def test_no_execution_shaped_keys_in_metadata(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        metadata = calls[0][1].get("metadata", {})
        execution = _EXECUTION_KEYS & metadata.keys()
        assert not execution, f"Execution-shaped keys found: {execution}"

    # --- Explicit absence of forbidden signal-data fields ---

    def test_no_confidence_in_metadata(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        metadata = calls[0][1]["metadata"]
        assert "confidence" not in metadata

    def test_no_direction_in_metadata(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        metadata = calls[0][1]["metadata"]
        assert "direction" not in metadata

    def test_no_prices_in_metadata(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        metadata = calls[0][1]["metadata"]
        assert not (_SIGNAL_DATA_KEYS & metadata.keys())

    def test_no_account_id_in_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert "account_id" not in str(calls[0][1])

    def test_no_execution_id_in_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert "execution_id" not in str(calls[0][1])

    def test_no_order_id_in_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert "order_id" not in str(calls[0][1])

    def test_no_trade_id_in_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert "trade_id" not in str(calls[0][1])

    def test_no_service_role_in_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert "service_role" not in str(calls[0][1])

    def test_no_secrets_in_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        payload_str = str(calls[0][1]).lower()
        for key in ("secret", "password", "api_key", "token", "credential"):
            assert key not in payload_str, f"Secret-like key found: {key}"


# ---------------------------------------------------------------------------
# 11. Payload safety — read_only, dry_run, source, event_type
# ---------------------------------------------------------------------------


class TestPayloadSafety:
    def test_payload_has_read_only_true(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert calls[0][1].get("read_only") is True

    def test_payload_has_dry_run_true(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert calls[0][1].get("dry_run") is True

    def test_payload_has_source_scanner(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert calls[0][1].get("source") == "scanner"

    def test_payload_has_event_type(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert calls[0][1].get("event_type") == "signal_decision_evaluated"

    def test_payload_has_non_empty_message(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        msg = calls[0][1].get("message", "")
        assert isinstance(msg, str) and len(msg) > 0


# ---------------------------------------------------------------------------
# 12 & 13. Endpoint resilience + non-blocking behavior
# ---------------------------------------------------------------------------


class TestEndpointResilience:
    def test_decisions_endpoint_returns_200_normally(self, client) -> None:
        """Baseline: endpoint returns 200 in normal test conditions."""
        response = client.get("/api/signals/decisions")
        assert response.status_code == 200

    def test_decisions_response_has_decisions_field(self, client) -> None:
        response = client.get("/api/signals/decisions")
        data = response.json()
        assert "decisions" in data

    def test_decisions_response_has_read_only_true(self, client) -> None:
        response = client.get("/api/signals/decisions")
        data = response.json()
        # Each decision record must have read_only=True.
        for record in data.get("decisions", []):
            assert record.get("read_only") is True

    def test_decisions_response_has_dry_run_true(self, client) -> None:
        response = client.get("/api/signals/decisions")
        data = response.json()
        for record in data.get("decisions", []):
            assert record.get("dry_run") is True

    def test_decisions_returns_200_if_audit_write_raises(
        self, client, monkeypatch
    ) -> None:
        """Endpoint must still return 200 if the underlying audit write fails."""

        def _raising_write(*args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("simulated audit write failure in decisions route test")

        monkeypatch.setattr(
            "app.services.signal_decision_audit.write_audit_event",
            _raising_write,
        )

        response = client.get("/api/signals/decisions")
        assert response.status_code == 200

    def test_decisions_returns_200_if_emit_fn_raises(
        self, client, monkeypatch
    ) -> None:
        """Endpoint must still return 200 if emit_signal_decision_event raises.

        The import is local inside the route function, so we patch it at the
        source module level — the same technique used for write_audit_event.
        """

        def _raising_emit(*args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("simulated emit failure")

        # Patch at the source module so the local import picks up the mock.
        monkeypatch.setattr(
            "app.services.signal_decision_audit.emit_signal_decision_event",
            _raising_emit,
        )

        response = client.get("/api/signals/decisions")
        assert response.status_code == 200

    def test_decisions_with_symbol_param_returns_200(self, client) -> None:
        response = client.get("/api/signals/decisions?symbol=AAPL")
        assert response.status_code == 200

    def test_decisions_with_limit_param_returns_200(self, client) -> None:
        response = client.get("/api/signals/decisions?limit=10")
        assert response.status_code == 200

    def test_decisions_response_shape_unchanged_by_supa010(self, client) -> None:
        """SUPA-010 must not alter the response schema."""
        response = client.get("/api/signals/decisions")
        data = response.json()
        # decisions list must be present (the existing contract).
        assert isinstance(data.get("decisions"), list)


# ---------------------------------------------------------------------------
# 14. Symbol filter threading
# ---------------------------------------------------------------------------


class TestSymbolFilterThreading:
    def test_symbol_filter_none_stored_as_none(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(5, None, _insert_fn=fn)
        assert calls[0][1]["metadata"]["symbol_filter"] is None

    def test_symbol_filter_string_stored_verbatim(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(3, "TSLA", _insert_fn=fn)
        assert calls[0][1]["metadata"]["symbol_filter"] == "TSLA"

    def test_symbol_filter_does_not_contaminate_other_fields(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(3, "TSLA", _insert_fn=fn)
        payload = calls[0][1]
        # symbol_filter must be inside metadata only, not at the top level.
        assert "symbol_filter" not in {
            k for k in payload if k != "metadata"
        }

    def test_message_references_decision_count(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(12, None, _insert_fn=fn)
        msg = calls[0][1].get("message", "")
        assert "12" in msg

    def test_message_references_symbol_filter_when_present(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_signal_decision_event(3, "EURUSD", _insert_fn=fn)
        msg = calls[0][1].get("message", "")
        assert "EURUSD" in msg


# ---------------------------------------------------------------------------
# 15. Write client usage — signal_decisions route (SUPA-003B)
# ---------------------------------------------------------------------------


class TestSignalDecisionsWriteClient:
    """The GET /signals/decisions audit emit must use the backend write client.

    Backend writes require SUPABASE_SERVICE_ROLE_KEY to bypass RLS deny-all.
    The anon client (get_safe_supabase_client) cannot INSERT; using it silently
    degrades every audit write.  These tests confirm the route imports and calls
    get_safe_supabase_write_client for the emit_signal_decision_event path.
    """

    def test_signal_decisions_route_calls_write_client(
        self, client, monkeypatch
    ) -> None:
        """Write client must be invoked at least once per /signals/decisions call."""
        write_client_calls: list[int] = []

        def _fake_write_client() -> None:
            write_client_calls.append(1)
            return None  # None → degraded path; no real Supabase needed.

        monkeypatch.setattr(
            "app.services.supabase_client.get_safe_supabase_write_client",
            _fake_write_client,
        )

        response = client.get("/api/signals/decisions")
        assert response.status_code == 200
        assert len(write_client_calls) >= 1, (
            "get_safe_supabase_write_client must be called for the audit emit path"
        )

    def test_signal_decisions_route_response_unaffected_by_write_client_none(
        self, client, monkeypatch
    ) -> None:
        """Response shape must be unchanged when write client returns None."""
        monkeypatch.setattr(
            "app.services.supabase_client.get_safe_supabase_write_client",
            lambda: None,
        )

        response = client.get("/api/signals/decisions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data.get("decisions"), list)

    def test_signal_decisions_safety_flags_preserved_with_write_client(
        self, client, monkeypatch
    ) -> None:
        """Safety flags must remain intact regardless of write client behaviour."""
        monkeypatch.setattr(
            "app.services.supabase_client.get_safe_supabase_write_client",
            lambda: None,
        )

        data = client.get("/api/signals/decisions").json()
        assert data["dry_run"] is True
        assert data["auto_trade"] is False
        assert data["read_only"] is True
