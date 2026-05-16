"""Tests for SUPA-003: audit writer service and AuditEvent schemas.

No real network calls — all Supabase interactions are replaced by injectable
_insert_fn or a None client to trigger the degraded path.

Test categories:
  1.  AuditEventCreate — valid construction
  2.  AuditEventCreate — forbidden metadata keys rejected
  3.  AuditEventCreate — execution-shaped metadata keys rejected
  4.  AuditEventCreate — safety invariants enforced (read_only / dry_run)
  5.  AuditEventCreate — extra fields forbidden
  6.  AuditEventRecord — valid construction
  7.  write_audit_event — degraded path (client=None)
  8.  write_audit_event — success path (fake _insert_fn)
  9.  write_audit_event — insert raises → degraded (no exception to caller)
  10. write_audit_event — response with no data list → persisted=True, id=None
  11. write_audit_event — payload always includes read_only + dry_run
  12. write_audit_event — service role key never in payload
  13. AuditSeverity — only allowed literals accepted
  14. AuditEventSource — only allowed literals accepted
  15. write_audit_event — empty metadata is safe
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.audit_event import (
    AuditEventCreate,
    AuditEventRecord,
    AuditEventSource,
    AuditSeverity,
)
from app.services.audit_writer import _build_payload, write_audit_event


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_event(**overrides: Any) -> AuditEventCreate:
    defaults: dict[str, Any] = {
        "event_type": "test_event",
        "severity": "info",
        "source": "system",
        "message": "test message",
    }
    defaults.update(overrides)
    return AuditEventCreate(**defaults)


def _fake_insert_fn(row_id: str | None = "abc-123") -> Any:
    """Return an _insert_fn that yields a fake Supabase-like response."""
    def _fn(table: str, payload: dict[str, Any]) -> Any:
        response = MagicMock()
        if row_id is not None:
            response.data = [{"id": row_id}]
        else:
            response.data = []
        return response
    return _fn


# ---------------------------------------------------------------------------
# 1. AuditEventCreate — valid construction
# ---------------------------------------------------------------------------

def test_audit_event_create_minimal() -> None:
    event = AuditEventCreate(event_type="startup", message="service started")
    assert event.event_type == "startup"
    assert event.severity == "info"
    assert event.source == "system"
    assert event.read_only is True
    assert event.dry_run is True
    assert event.metadata == {}


def test_audit_event_create_all_fields() -> None:
    event = AuditEventCreate(
        event_type="scanner_complete",
        severity="success",
        source="scanner",
        message="scan finished",
        metadata={"symbol": "EURUSD", "count": 5},
    )
    assert event.severity == "success"
    assert event.source == "scanner"
    assert event.metadata["symbol"] == "EURUSD"


def test_audit_event_create_all_severities() -> None:
    for sev in ("info", "success", "warning", "error", "safety"):
        event = AuditEventCreate(event_type="e", severity=sev, message="m")  # type: ignore[arg-type]
        assert event.severity == sev


def test_audit_event_create_all_sources() -> None:
    for src in ("system", "scanner", "ai_workspace", "broker_registry", "supabase", "safety"):
        event = AuditEventCreate(event_type="e", source=src, message="m")  # type: ignore[arg-type]
        assert event.source == src


# ---------------------------------------------------------------------------
# 2. AuditEventCreate — forbidden metadata keys rejected
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "key",
    [
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
    ],
)
def test_forbidden_metadata_key_rejected(key: str) -> None:
    with pytest.raises(ValidationError, match="forbidden key"):
        AuditEventCreate(event_type="e", message="m", metadata={key: "value"})


# ---------------------------------------------------------------------------
# 3. AuditEventCreate — execution-shaped metadata keys rejected
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "key",
    [
        "place_order",
        "execute_trade",
        "broker_execute",
        "cancel_order",
        "modify_order",
        "enable_autotrade",
        "disable_dry_run",
        "connect_live",
    ],
)
def test_execution_shaped_metadata_key_rejected(key: str) -> None:
    with pytest.raises(ValidationError, match="execution-shaped key"):
        AuditEventCreate(event_type="e", message="m", metadata={key: True})


# ---------------------------------------------------------------------------
# 4. AuditEventCreate — safety invariants enforced
# ---------------------------------------------------------------------------

def test_read_only_must_be_true() -> None:
    with pytest.raises(ValidationError, match="read_only must always be True"):
        AuditEventCreate(event_type="e", message="m", read_only=False)


def test_dry_run_must_be_true() -> None:
    with pytest.raises(ValidationError, match="dry_run must always be True"):
        AuditEventCreate(event_type="e", message="m", dry_run=False)


# ---------------------------------------------------------------------------
# 5. AuditEventCreate — extra fields forbidden
# ---------------------------------------------------------------------------

def test_extra_fields_forbidden() -> None:
    with pytest.raises(ValidationError):
        AuditEventCreate(event_type="e", message="m", unknown_field="x")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# 6. AuditEventRecord — valid construction
# ---------------------------------------------------------------------------

def test_audit_event_record_defaults() -> None:
    record = AuditEventRecord(
        event_type="startup",
        severity="info",
        source="system",
        message="boot",
    )
    assert record.persisted is False
    assert record.degraded is False
    assert record.id is None
    assert record.degraded_reason is None
    assert record.read_only is True
    assert record.dry_run is True


def test_audit_event_record_persisted() -> None:
    record = AuditEventRecord(
        event_type="e",
        severity="info",
        source="system",
        message="m",
        id="uuid-xyz",
        persisted=True,
    )
    assert record.persisted is True
    assert record.id == "uuid-xyz"


def test_audit_event_record_degraded() -> None:
    record = AuditEventRecord(
        event_type="e",
        severity="warning",
        source="system",
        message="m",
        persisted=False,
        degraded=True,
        degraded_reason="client unavailable",
    )
    assert record.degraded is True
    assert record.degraded_reason == "client unavailable"


# ---------------------------------------------------------------------------
# 7. write_audit_event — degraded path (client=None)
# ---------------------------------------------------------------------------

def test_write_audit_event_no_client_returns_degraded() -> None:
    event = _make_event()
    record = write_audit_event(event, client=None)
    assert record.persisted is False
    assert record.degraded is True
    assert record.id is None
    assert record.degraded_reason is not None


def test_write_audit_event_no_client_does_not_raise() -> None:
    event = _make_event()
    result = write_audit_event(event)  # no client, no _insert_fn
    assert isinstance(result, AuditEventRecord)


# ---------------------------------------------------------------------------
# 8. write_audit_event — success path (fake _insert_fn)
# ---------------------------------------------------------------------------

def test_write_audit_event_success_returns_persisted() -> None:
    event = _make_event()
    record = write_audit_event(event, _insert_fn=_fake_insert_fn("row-uuid-1"))
    assert record.persisted is True
    assert record.degraded is False
    assert record.id == "row-uuid-1"


def test_write_audit_event_success_fields_match_event() -> None:
    event = _make_event(event_type="scanner_done", severity="success", source="scanner")
    record = write_audit_event(event, _insert_fn=_fake_insert_fn())
    assert record.event_type == "scanner_done"
    assert record.severity == "success"
    assert record.source == "scanner"


def test_write_audit_event_success_read_only_and_dry_run() -> None:
    event = _make_event()
    record = write_audit_event(event, _insert_fn=_fake_insert_fn())
    assert record.read_only is True
    assert record.dry_run is True


# ---------------------------------------------------------------------------
# 9. write_audit_event — insert raises → degraded (no exception to caller)
# ---------------------------------------------------------------------------

def test_write_audit_event_insert_raises_returns_degraded() -> None:
    def _raising_insert(table: str, payload: dict[str, Any]) -> Any:
        raise RuntimeError("connection refused")

    event = _make_event()
    record = write_audit_event(event, _insert_fn=_raising_insert)
    assert record.persisted is False
    assert record.degraded is True
    assert "connection refused" in (record.degraded_reason or "")


def test_write_audit_event_insert_raises_does_not_propagate() -> None:
    def _exploding(table: str, payload: dict[str, Any]) -> Any:
        raise ValueError("boom")

    event = _make_event()
    result = write_audit_event(event, _insert_fn=_exploding)
    assert isinstance(result, AuditEventRecord)


# ---------------------------------------------------------------------------
# 10. write_audit_event — response with empty data list → persisted=True, id=None
# ---------------------------------------------------------------------------

def test_write_audit_event_empty_data_response() -> None:
    record = write_audit_event(_make_event(), _insert_fn=_fake_insert_fn(row_id=None))
    assert record.persisted is True
    assert record.id is None


# ---------------------------------------------------------------------------
# 11. write_audit_event — payload always includes read_only + dry_run
# ---------------------------------------------------------------------------

def test_build_payload_always_includes_safety_flags() -> None:
    event = _make_event()
    payload = _build_payload(event)
    assert payload["read_only"] is True
    assert payload["dry_run"] is True


def test_build_payload_correct_fields() -> None:
    event = _make_event(
        event_type="health_check",
        severity="info",
        source="system",
        message="all ok",
        metadata={"component": "api"},
    )
    payload = _build_payload(event)
    assert payload["event_type"] == "health_check"
    assert payload["severity"] == "info"
    assert payload["source"] == "system"
    assert payload["message"] == "all ok"
    assert payload["metadata"] == {"component": "api"}


def test_insert_fn_receives_correct_table_name() -> None:
    captured: list[str] = []

    def _recording_insert(table: str, payload: dict[str, Any]) -> Any:
        captured.append(table)
        response = MagicMock()
        response.data = [{"id": "t1"}]
        return response

    write_audit_event(_make_event(), _insert_fn=_recording_insert)
    assert captured == ["audit_events"]


# ---------------------------------------------------------------------------
# 12. write_audit_event — service role key never in payload
# ---------------------------------------------------------------------------

def test_payload_does_not_contain_service_role_key() -> None:
    captured_payloads: list[dict[str, Any]] = []

    def _capturing_insert(table: str, payload: dict[str, Any]) -> Any:
        captured_payloads.append(payload)
        response = MagicMock()
        response.data = [{"id": "x"}]
        return response

    write_audit_event(_make_event(), _insert_fn=_capturing_insert)
    assert len(captured_payloads) == 1
    payload = captured_payloads[0]
    assert "service_role" not in payload
    assert "service_role_key" not in payload
    assert "SUPABASE_SERVICE_ROLE_KEY" not in str(payload)


# ---------------------------------------------------------------------------
# 13. AuditSeverity — only allowed literals accepted
# ---------------------------------------------------------------------------

def test_invalid_severity_rejected() -> None:
    with pytest.raises(ValidationError):
        AuditEventCreate(event_type="e", message="m", severity="critical")  # type: ignore[arg-type]


def test_valid_severity_safety() -> None:
    event = AuditEventCreate(event_type="e", message="m", severity="safety")
    assert event.severity == "safety"


# ---------------------------------------------------------------------------
# 14. AuditEventSource — only allowed literals accepted
# ---------------------------------------------------------------------------

def test_invalid_source_rejected() -> None:
    with pytest.raises(ValidationError):
        AuditEventCreate(event_type="e", message="m", source="frontend")  # type: ignore[arg-type]


def test_valid_source_broker_registry() -> None:
    event = AuditEventCreate(event_type="e", message="m", source="broker_registry")
    assert event.source == "broker_registry"


# ---------------------------------------------------------------------------
# 15. write_audit_event — empty metadata is safe
# ---------------------------------------------------------------------------

def test_write_audit_event_empty_metadata_is_safe() -> None:
    event = AuditEventCreate(event_type="e", message="m")
    record = write_audit_event(event, _insert_fn=_fake_insert_fn())
    assert record.persisted is True
    assert record.metadata == {}


def test_write_audit_event_safe_metadata_keys_accepted() -> None:
    event = AuditEventCreate(
        event_type="scanner_result",
        message="signal emitted",
        metadata={"symbol": "EURUSD", "route": "/scanner", "status": "ok"},
    )
    record = write_audit_event(event, _insert_fn=_fake_insert_fn())
    assert record.persisted is True
    assert record.metadata["symbol"] == "EURUSD"


# ---------------------------------------------------------------------------
# 16. AuditEventRecord — safety invariants enforced at schema level (Scope A)
# ---------------------------------------------------------------------------

def test_audit_event_record_rejects_read_only_false() -> None:
    with pytest.raises(ValidationError, match="read_only must always be True"):
        AuditEventRecord(
            event_type="test",
            severity="info",
            source="system",
            message="m",
            read_only=False,
        )


def test_audit_event_record_rejects_dry_run_false() -> None:
    with pytest.raises(ValidationError, match="dry_run must always be True"):
        AuditEventRecord(
            event_type="test",
            severity="info",
            source="system",
            message="m",
            dry_run=False,
        )


# ---------------------------------------------------------------------------
# 17. write_audit_event — real client path (MagicMock, no _insert_fn)
# ---------------------------------------------------------------------------

def test_write_audit_event_real_client_path_calls_table_insert_execute() -> None:
    from unittest.mock import MagicMock

    event = _make_event()
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "real-uuid"}
    ]

    record = write_audit_event(event, client=mock_client)

    mock_client.table.assert_called_once()
    mock_client.table.return_value.insert.assert_called_once()
    mock_client.table.return_value.insert.return_value.execute.assert_called_once()
    assert record.persisted is True
    assert record.id == "real-uuid"


def test_write_audit_event_real_client_path_table_name_is_audit_events() -> None:
    from unittest.mock import MagicMock

    event = _make_event()
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "x"}
    ]

    write_audit_event(event, client=mock_client)

    mock_client.table.assert_called_once_with("audit_events")


# ---------------------------------------------------------------------------
# 18. AuditEventCreate — empty field boundary tests
# ---------------------------------------------------------------------------

def test_audit_event_create_empty_event_type_rejected() -> None:
    with pytest.raises(ValidationError):
        AuditEventCreate(event_type="", message="some message")


def test_audit_event_create_empty_message_rejected() -> None:
    with pytest.raises(ValidationError):
        AuditEventCreate(event_type="test_event", message="")
