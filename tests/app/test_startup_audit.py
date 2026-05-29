"""Tests for SUPA-007: startup audit event emitter.

No real network calls — all Supabase interactions are replaced by injectable
_insert_fn or a None client to trigger the degraded path.

Test categories:
  1.  Return shape — list of exactly 3 AuditEventRecord objects
  2.  Event types — backend_started, dry_run_active, read_only_mode_confirmed
  3.  Source — all source="system"
  4.  Safety invariants — all read_only=True, dry_run=True
  5.  Success path — persisted=True, degraded=False with fake _insert_fn
  6.  Degraded path — persisted=False, degraded=True when no client/no _insert_fn
  7.  Insert failure — does not raise; degrades gracefully
  8.  Metadata safety — no forbidden keys, no execution-shaped keys, empty dict
  9.  Injectable _insert_fn — called exactly 3 times with correct arguments
  10. Payload safety — read_only=True, dry_run=True, source="system" in every payload
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from app.schemas.audit_event import AuditEventRecord
from app.services.startup_audit import emit_startup_events

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

# Known forbidden metadata keys (matches _FORBIDDEN_METADATA_KEYS in audit_event.py).
_KNOWN_FORBIDDEN_KEYS = frozenset(
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

# Known execution-shaped metadata keys (matches _EXECUTION_SHAPED_METADATA_KEYS).
_KNOWN_EXECUTION_KEYS = frozenset(
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


def _make_fake_insert_fn() -> tuple[Any, list[tuple[str, dict[str, Any]]]]:
    """Return (fn, calls) — fn records every (table, payload) call in calls."""
    calls: list[tuple[str, dict[str, Any]]] = []

    def _fn(table: str, payload: dict[str, Any]) -> Any:
        calls.append((table, dict(payload)))  # snapshot payload at call time
        response = MagicMock()
        response.data = [{"id": f"test-id-{len(calls)}"}]
        return response

    return _fn, calls


def _make_failing_insert_fn() -> Any:
    """Return an _insert_fn that always raises RuntimeError."""

    def _fn(table: str, payload: dict[str, Any]) -> Any:
        raise RuntimeError("simulated Supabase insert failure")

    return _fn


# ---------------------------------------------------------------------------
# 1. Return shape
# ---------------------------------------------------------------------------


class TestReturnShape:
    def test_returns_a_list(self) -> None:
        result = emit_startup_events()
        assert isinstance(result, list)

    def test_returns_exactly_3_records(self) -> None:
        result = emit_startup_events()
        assert len(result) == 3

    def test_all_items_are_audit_event_records(self) -> None:
        result = emit_startup_events()
        for item in result:
            assert isinstance(item, AuditEventRecord)

    def test_returns_3_records_with_insert_fn(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# 2. Event types
# ---------------------------------------------------------------------------


class TestEventTypes:
    def test_event_types_in_exact_order(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        types = [r.event_type for r in result]
        assert types == [
            "backend_started",
            "dry_run_active",
            "read_only_mode_confirmed",
        ]

    def test_backend_started_present(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        assert any(r.event_type == "backend_started" for r in result)

    def test_dry_run_active_present(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        assert any(r.event_type == "dry_run_active" for r in result)

    def test_read_only_mode_confirmed_present(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        assert any(r.event_type == "read_only_mode_confirmed" for r in result)

    def test_event_types_on_degraded_path(self) -> None:
        # Event types must be correct even when degraded.
        result = emit_startup_events()  # no client, no _insert_fn
        types = [r.event_type for r in result]
        assert types == [
            "backend_started",
            "dry_run_active",
            "read_only_mode_confirmed",
        ]


# ---------------------------------------------------------------------------
# 3. Source
# ---------------------------------------------------------------------------


class TestSource:
    def test_all_sources_are_system_on_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        for record in result:
            assert record.source == "system"

    def test_all_sources_are_system_on_degraded_path(self) -> None:
        result = emit_startup_events()
        for record in result:
            assert record.source == "system"


# ---------------------------------------------------------------------------
# 4. Safety invariants
# ---------------------------------------------------------------------------


class TestSafetyInvariants:
    def test_all_read_only_true_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        for record in result:
            assert record.read_only is True

    def test_all_dry_run_true_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        for record in result:
            assert record.dry_run is True

    def test_all_read_only_true_degraded_path(self) -> None:
        result = emit_startup_events()
        for record in result:
            assert record.read_only is True

    def test_all_dry_run_true_degraded_path(self) -> None:
        result = emit_startup_events()
        for record in result:
            assert record.dry_run is True

    def test_all_read_only_true_on_insert_failure(self) -> None:
        result = emit_startup_events(_insert_fn=_make_failing_insert_fn())
        for record in result:
            assert record.read_only is True

    def test_all_dry_run_true_on_insert_failure(self) -> None:
        result = emit_startup_events(_insert_fn=_make_failing_insert_fn())
        for record in result:
            assert record.dry_run is True


# ---------------------------------------------------------------------------
# 5. Success path
# ---------------------------------------------------------------------------


class TestSuccessPath:
    def test_all_persisted_true_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        for record in result:
            assert record.persisted is True

    def test_all_degraded_false_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        for record in result:
            assert record.degraded is False

    def test_ids_assigned_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        for record in result:
            assert record.id is not None


# ---------------------------------------------------------------------------
# 6. Degraded path
# ---------------------------------------------------------------------------


class TestDegradedPath:
    def test_all_degraded_true_when_no_client_no_fn(self) -> None:
        result = emit_startup_events()
        for record in result:
            assert record.degraded is True

    def test_all_persisted_false_when_degraded(self) -> None:
        result = emit_startup_events()
        for record in result:
            assert record.persisted is False

    def test_returns_3_records_even_when_degraded(self) -> None:
        result = emit_startup_events()
        assert len(result) == 3

    def test_degraded_reason_set_when_degraded(self) -> None:
        result = emit_startup_events()
        for record in result:
            assert record.degraded_reason is not None
            assert len(record.degraded_reason) > 0


# ---------------------------------------------------------------------------
# 7. Insert failure — does not raise
# ---------------------------------------------------------------------------


class TestInsertFailure:
    def test_no_exception_raised_on_insert_failure(self) -> None:
        # Must not raise under any circumstances.
        result = emit_startup_events(_insert_fn=_make_failing_insert_fn())
        assert len(result) == 3

    def test_all_degraded_on_insert_failure(self) -> None:
        result = emit_startup_events(_insert_fn=_make_failing_insert_fn())
        for record in result:
            assert record.degraded is True

    def test_all_not_persisted_on_insert_failure(self) -> None:
        result = emit_startup_events(_insert_fn=_make_failing_insert_fn())
        for record in result:
            assert record.persisted is False

    def test_degraded_reason_contains_exception_message(self) -> None:
        result = emit_startup_events(_insert_fn=_make_failing_insert_fn())
        for record in result:
            assert record.degraded_reason is not None
            assert "simulated Supabase insert failure" in record.degraded_reason


# ---------------------------------------------------------------------------
# 8. Metadata safety
# ---------------------------------------------------------------------------


class TestMetadataSafety:
    def test_metadata_is_empty_dict_in_all_records(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_startup_events(_insert_fn=fn)
        for record in result:
            assert record.metadata == {}

    def test_no_forbidden_keys_in_payloads(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            metadata = payload.get("metadata", {})
            forbidden_found = _KNOWN_FORBIDDEN_KEYS & metadata.keys()
            assert not forbidden_found, f"Forbidden keys found: {forbidden_found}"

    def test_no_execution_shaped_keys_in_payloads(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            metadata = payload.get("metadata", {})
            execution_found = _KNOWN_EXECUTION_KEYS & metadata.keys()
            assert (
                not execution_found
            ), f"Execution-shaped keys found: {execution_found}"

    def test_no_account_id_in_any_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            assert "account_id" not in str(payload)

    def test_no_service_role_in_any_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            assert "service_role" not in str(payload)

    def test_no_execution_id_in_any_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            assert "execution_id" not in str(payload)


# ---------------------------------------------------------------------------
# 9. Injectable _insert_fn called exactly 3 times
# ---------------------------------------------------------------------------


class TestInjectableInsertFn:
    def test_insert_fn_called_exactly_3_times(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        assert len(calls) == 3

    def test_insert_fn_always_targets_audit_events_table(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for table, _ in calls:
            assert table == "audit_events"

    def test_insert_fn_called_once_per_event_type(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        event_types_in_calls = [payload.get("event_type") for _, payload in calls]
        assert "backend_started" in event_types_in_calls
        assert "dry_run_active" in event_types_in_calls
        assert "read_only_mode_confirmed" in event_types_in_calls


# ---------------------------------------------------------------------------
# 10. Payload safety — read_only, dry_run, source in every payload
# ---------------------------------------------------------------------------


class TestPayloadSafety:
    def test_payload_has_read_only_true(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            assert payload.get("read_only") is True

    def test_payload_has_dry_run_true(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            assert payload.get("dry_run") is True

    def test_payload_has_source_system(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            assert payload.get("source") == "system"

    def test_payload_has_event_type(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            assert payload.get("event_type") is not None
            assert len(payload.get("event_type", "")) > 0

    def test_payload_has_message(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_startup_events(_insert_fn=fn)
        for _, payload in calls:
            assert payload.get("message") is not None
            assert len(payload.get("message", "")) > 0
