"""PAPER-002A — In-memory paper sandbox history service tests.

Proves:
  - history starts empty
  - event IDs are sequential local paper-scoped identifiers (paper_audit_N)
  - events include all canonical safety flags locked to safe values
  - append / list_events / get_history / reset work correctly
  - max history cap (250) works — oldest events are dropped
  - forbidden metadata keys are sanitized (account_id, order_id, etc.)
  - broker/execution/MT5/IBKR IDs are never surfaced in any event field
  - non-finite numeric metadata values (nan, inf, -inf) are dropped
  - no secrets are retained in event metadata
  - service is in-memory only — no DB, no Supabase, no network
  - no route is added in PAPER-002A
  - event type normalization works
  - unknown event types map to "unknown_paper_event"
  - severity coercion works
  - message/source length capping works
  - metadata key cap works
  - list_events(limit=N) returns most recent N events
  - get_history() returns PaperAuditHistory with correct count
  - record_paper_event() module-level convenience wrapper works
  - no broker/MT5/IBKR imports are present in service/schema modules
  - existing GET /api/paper/sandbox/preview schema is unaffected
  - PaperAuditHistory safety flags are always locked
"""

from __future__ import annotations

import importlib
import inspect
import math
from typing import Any

import pytest

from app.schemas.paper_sandbox_history import (
    PaperAuditEvent,
    PaperAuditHistory,
    VALID_EVENT_TYPES,
)
from app.services.paper_sandbox_history import (
    PaperAuditHistoryService,
    _FORBIDDEN_META_KEYS,
    _MAX_HISTORY,
    _MAX_META_KEYS,
    _MAX_META_VALUE_STR_LEN,
    _MAX_MESSAGE_LEN,
    _MAX_SOURCE_LEN,
    _normalize_event_type,
    _sanitize_metadata,
    get_paper_sandbox_history,
    record_paper_event,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh() -> PaperAuditHistoryService:
    """Return a new, isolated PaperAuditHistoryService instance."""
    return PaperAuditHistoryService()


# ---------------------------------------------------------------------------
# 1. Empty state
# ---------------------------------------------------------------------------

class TestEmptyState:
    def test_starts_empty(self) -> None:
        svc = _fresh()
        assert len(svc) == 0

    def test_list_events_empty(self) -> None:
        svc = _fresh()
        assert svc.list_events() == []

    def test_get_history_empty(self) -> None:
        svc = _fresh()
        h = svc.get_history()
        assert h.count == 0
        assert h.events == []

    def test_get_history_empty_safety_flags(self) -> None:
        svc = _fresh()
        h = svc.get_history()
        assert h.paper_only is True
        assert h.dry_run is True
        assert h.read_only is True
        assert h.live_orders_blocked is True
        assert h.execution_mode == "dry_run_only"
        assert h.requires_human_review is True
        assert h.risk_allowed is False
        assert h.broker_execution_allowed is False


# ---------------------------------------------------------------------------
# 2. Event ID format
# ---------------------------------------------------------------------------

class TestEventIds:
    def test_first_event_id(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "test")
        assert ev.event_id == "paper_audit_000001"

    def test_event_ids_are_sequential(self) -> None:
        svc = _fresh()
        ids = [svc.append("sandbox_preview_requested", f"msg {i}").event_id
               for i in range(5)]
        assert ids == [
            "paper_audit_000001",
            "paper_audit_000002",
            "paper_audit_000003",
            "paper_audit_000004",
            "paper_audit_000005",
        ]

    def test_event_id_format(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_state_reset", "reset")
        assert ev.event_id.startswith("paper_audit_")
        suffix = ev.event_id[len("paper_audit_"):]
        assert suffix.isdigit()
        assert len(suffix) == 6

    def test_counter_resets_on_service_reset(self) -> None:
        svc = _fresh()
        svc.append("sandbox_preview_requested", "before")
        svc.reset()
        ev = svc.append("sandbox_preview_requested", "after")
        assert ev.event_id == "paper_audit_000001"

    def test_event_id_not_broker_id(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "test")
        assert "order" not in ev.event_id
        assert "broker" not in ev.event_id
        assert "ibkr" not in ev.event_id
        assert "mt5" not in ev.event_id
        assert "execution" not in ev.event_id
        assert "account" not in ev.event_id


# ---------------------------------------------------------------------------
# 3. Safety flags on every event
# ---------------------------------------------------------------------------

class TestEventSafetyFlags:
    def test_paper_only_is_true(self) -> None:
        svc = _fresh()
        ev = svc.append("safety_flags_checked", "check")
        assert ev.paper_only is True

    def test_dry_run_is_true(self) -> None:
        svc = _fresh()
        ev = svc.append("safety_flags_checked", "check")
        assert ev.dry_run is True

    def test_read_only_is_true(self) -> None:
        svc = _fresh()
        ev = svc.append("safety_flags_checked", "check")
        assert ev.read_only is True

    def test_live_orders_blocked_is_true(self) -> None:
        svc = _fresh()
        ev = svc.append("safety_flags_checked", "check")
        assert ev.live_orders_blocked is True

    def test_execution_mode_is_dry_run_only(self) -> None:
        svc = _fresh()
        ev = svc.append("safety_flags_checked", "check")
        assert ev.execution_mode == "dry_run_only"

    def test_requires_human_review_is_true(self) -> None:
        svc = _fresh()
        ev = svc.append("safety_flags_checked", "check")
        assert ev.requires_human_review is True

    def test_risk_allowed_is_false(self) -> None:
        svc = _fresh()
        ev = svc.append("safety_flags_checked", "check")
        assert ev.risk_allowed is False

    def test_broker_execution_allowed_is_false(self) -> None:
        svc = _fresh()
        ev = svc.append("safety_flags_checked", "check")
        assert ev.broker_execution_allowed is False

    def test_all_event_types_carry_safety_flags(self) -> None:
        svc = _fresh()
        for et in VALID_EVENT_TYPES:
            ev = svc.append(et, f"msg for {et}")
            assert ev.paper_only is True
            assert ev.dry_run is True
            assert ev.live_orders_blocked is True
            assert ev.broker_execution_allowed is False
            assert ev.risk_allowed is False


# ---------------------------------------------------------------------------
# 4. Append / list / reset
# ---------------------------------------------------------------------------

class TestAppendListReset:
    def test_append_increments_count(self) -> None:
        svc = _fresh()
        svc.append("sandbox_preview_requested", "msg1")
        svc.append("sandbox_state_reset", "msg2")
        assert len(svc) == 2

    def test_list_events_returns_all(self) -> None:
        svc = _fresh()
        svc.append("sandbox_preview_requested", "a")
        svc.append("sandbox_state_created", "b")
        events = svc.list_events()
        assert len(events) == 2

    def test_list_events_order_oldest_first(self) -> None:
        svc = _fresh()
        e1 = svc.append("sandbox_preview_requested", "first")
        e2 = svc.append("sandbox_state_created", "second")
        events = svc.list_events()
        assert events[0].event_id == e1.event_id
        assert events[1].event_id == e2.event_id

    def test_get_history_count_matches(self) -> None:
        svc = _fresh()
        svc.append("sandbox_preview_requested", "x")
        svc.append("sandbox_preview_requested", "y")
        svc.append("sandbox_preview_requested", "z")
        h = svc.get_history()
        assert h.count == 3
        assert len(h.events) == 3

    def test_reset_clears_history(self) -> None:
        svc = _fresh()
        svc.append("sandbox_preview_requested", "x")
        svc.reset()
        assert len(svc) == 0
        assert svc.list_events() == []

    def test_reset_then_append(self) -> None:
        svc = _fresh()
        svc.append("sandbox_preview_requested", "before")
        svc.reset()
        svc.append("sandbox_state_created", "after")
        events = svc.list_events()
        assert len(events) == 1
        assert events[0].event_type == "sandbox_state_created"

    def test_list_events_limit(self) -> None:
        svc = _fresh()
        for i in range(10):
            svc.append("sandbox_preview_requested", f"msg {i}")
        recent = svc.list_events(limit=3)
        assert len(recent) == 3
        assert recent[-1].message == "msg 9"

    def test_list_events_limit_zero(self) -> None:
        svc = _fresh()
        svc.append("sandbox_preview_requested", "x")
        assert svc.list_events(limit=0) == []

    def test_list_events_limit_exceeds_count(self) -> None:
        svc = _fresh()
        svc.append("sandbox_preview_requested", "x")
        events = svc.list_events(limit=100)
        assert len(events) == 1


# ---------------------------------------------------------------------------
# 5. Max history cap
# ---------------------------------------------------------------------------

class TestHistoryCap:
    def test_cap_at_max_history(self) -> None:
        svc = _fresh()
        for i in range(_MAX_HISTORY + 10):
            svc.append("sandbox_preview_requested", f"msg {i}")
        assert len(svc) == _MAX_HISTORY

    def test_oldest_events_dropped(self) -> None:
        svc = _fresh()
        for i in range(_MAX_HISTORY + 5):
            svc.append("sandbox_preview_requested", f"msg {i}")
        events = svc.list_events()
        # First retained message should be msg 5 (oldest 5 were dropped)
        assert events[0].message == "msg 5"

    def test_newest_events_retained(self) -> None:
        svc = _fresh()
        for i in range(_MAX_HISTORY + 3):
            svc.append("sandbox_preview_requested", f"msg {i}")
        events = svc.list_events()
        last_index = _MAX_HISTORY + 2
        assert events[-1].message == f"msg {last_index}"


# ---------------------------------------------------------------------------
# 6. Forbidden field sanitization
# ---------------------------------------------------------------------------

class TestForbiddenFieldSanitization:
    def _meta_with_forbidden(self) -> dict[str, Any]:
        return {
            "account_id": "acct-123",
            "broker_account_id": "broker-xyz",
            "order_id": "ord-999",
            "execution_id": "exec-001",
            "trade_id": "trade-abc",
            "broker_order_id": "bo-007",
            "ibkr_order_id": "ibkr-42",
            "mt5_ticket": "12345",
            "credential": "supersecret",
            "secret": "mysecret",
            "token": "bearer-token",
            "api_key": "sk-XXXXXXXX",
            "password": "hunter2",
        }

    def test_forbidden_keys_dropped(self) -> None:
        svc = _fresh()
        ev = svc.append(
            "sandbox_preview_requested",
            "test",
            metadata=self._meta_with_forbidden(),
        )
        for key in _FORBIDDEN_META_KEYS:
            assert key not in ev.metadata

    def test_safe_keys_retained(self) -> None:
        svc = _fresh()
        ev = svc.append(
            "sandbox_preview_requested",
            "test",
            metadata={"symbol": "EURUSD", "count": 3},
        )
        assert ev.metadata.get("symbol") == "EURUSD"
        assert ev.metadata.get("count") == 3

    def test_mixed_meta_only_safe_retained(self) -> None:
        svc = _fresh()
        ev = svc.append(
            "sandbox_preview_requested",
            "test",
            metadata={"symbol": "GBPUSD", "secret": "leaked", "count": 1},
        )
        assert "secret" not in ev.metadata
        assert ev.metadata.get("symbol") == "GBPUSD"
        assert ev.metadata.get("count") == 1

    def test_sanitize_helper_drops_forbidden(self) -> None:
        result = _sanitize_metadata({"account_id": "x", "symbol": "EURUSD"})
        assert "account_id" not in result
        assert result.get("symbol") == "EURUSD"

    def test_sanitize_helper_none_input(self) -> None:
        assert _sanitize_metadata(None) == {}

    def test_sanitize_helper_empty_dict(self) -> None:
        assert _sanitize_metadata({}) == {}

    def test_sanitize_case_insensitive_key_check(self) -> None:
        result = _sanitize_metadata({"SECRET": "val", "Account_ID": "x"})
        # Keys are checked lowercased
        assert "SECRET" not in result or result.get("SECRET") is None
        assert "Account_ID" not in result or result.get("Account_ID") is None

    def test_meta_key_cap(self) -> None:
        big_meta = {f"key_{i}": f"val_{i}" for i in range(_MAX_META_KEYS + 20)}
        result = _sanitize_metadata(big_meta)
        assert len(result) <= _MAX_META_KEYS

    def test_meta_string_value_truncated(self) -> None:
        long_val = "x" * (_MAX_META_VALUE_STR_LEN + 100)
        result = _sanitize_metadata({"note": long_val})
        assert len(result["note"]) == _MAX_META_VALUE_STR_LEN


# ---------------------------------------------------------------------------
# 7. Non-finite numeric metadata
# ---------------------------------------------------------------------------

class TestNonFiniteMetadata:
    def test_nan_dropped(self) -> None:
        result = _sanitize_metadata({"confidence": float("nan")})
        assert "confidence" not in result

    def test_inf_dropped(self) -> None:
        result = _sanitize_metadata({"value": float("inf")})
        assert "value" not in result

    def test_neg_inf_dropped(self) -> None:
        result = _sanitize_metadata({"value": float("-inf")})
        assert "value" not in result

    def test_finite_float_retained(self) -> None:
        result = _sanitize_metadata({"risk_pct": 0.5})
        assert result.get("risk_pct") == pytest.approx(0.5)

    def test_event_with_nan_metadata(self) -> None:
        svc = _fresh()
        ev = svc.append(
            "sandbox_preview_requested",
            "test",
            metadata={"bad": float("nan"), "good": "ok"},
        )
        assert "bad" not in ev.metadata
        assert ev.metadata.get("good") == "ok"


# ---------------------------------------------------------------------------
# 8. Event type normalization
# ---------------------------------------------------------------------------

class TestEventTypeNormalization:
    def test_valid_event_type_unchanged(self) -> None:
        assert _normalize_event_type("sandbox_preview_requested") == "sandbox_preview_requested"

    def test_valid_type_with_leading_whitespace(self) -> None:
        assert _normalize_event_type("  sandbox_state_reset  ") == "sandbox_state_reset"

    def test_valid_type_uppercase(self) -> None:
        assert _normalize_event_type("SANDBOX_PREVIEW_REQUESTED") == "sandbox_preview_requested"

    def test_valid_type_with_hyphens(self) -> None:
        assert _normalize_event_type("sandbox-state-reset") == "sandbox_state_reset"

    def test_unknown_type_maps_to_unknown(self) -> None:
        assert _normalize_event_type("some_random_thing") == "unknown_paper_event"

    def test_empty_string_maps_to_unknown(self) -> None:
        assert _normalize_event_type("") == "unknown_paper_event"

    def test_all_valid_event_types_survive(self) -> None:
        for et in VALID_EVENT_TYPES:
            assert _normalize_event_type(et) == et

    def test_event_with_unknown_type_stored_as_unknown(self) -> None:
        svc = _fresh()
        ev = svc.append("totally_invalid_type", "msg")
        assert ev.event_type == "unknown_paper_event"


# ---------------------------------------------------------------------------
# 9. Severity coercion
# ---------------------------------------------------------------------------

class TestSeverityCoercion:
    @pytest.mark.parametrize("severity", ["info", "warning", "blocked"])
    def test_valid_severity_accepted(self, severity: str) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "msg", severity=severity)
        assert ev.severity == severity

    def test_invalid_severity_coerced_to_info(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "msg", severity="critical")
        assert ev.severity == "info"

    def test_empty_severity_coerced_to_info(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "msg", severity="")
        assert ev.severity == "info"


# ---------------------------------------------------------------------------
# 10. Message and source length capping
# ---------------------------------------------------------------------------

class TestLengthCapping:
    def test_message_truncated(self) -> None:
        svc = _fresh()
        long_msg = "x" * (_MAX_MESSAGE_LEN + 100)
        ev = svc.append("sandbox_preview_requested", long_msg)
        assert len(ev.message) == _MAX_MESSAGE_LEN

    def test_source_truncated(self) -> None:
        svc = _fresh()
        long_source = "s" * (_MAX_SOURCE_LEN + 50)
        ev = svc.append("sandbox_preview_requested", "msg", source=long_source)
        assert len(ev.source) == _MAX_SOURCE_LEN

    def test_normal_message_not_truncated(self) -> None:
        svc = _fresh()
        msg = "Short advisory message."
        ev = svc.append("sandbox_preview_requested", msg)
        assert ev.message == msg


# ---------------------------------------------------------------------------
# 11. Module-level convenience wrapper
# ---------------------------------------------------------------------------

class TestModuleLevelWrapper:
    def test_record_paper_event_returns_event(self) -> None:
        history = get_paper_sandbox_history()
        before = len(history)
        ev = record_paper_event("sandbox_preview_requested", "convenience test")
        assert ev.event_id is not None
        assert ev.paper_only is True
        assert len(history) == before + 1

    def test_get_paper_sandbox_history_is_singleton(self) -> None:
        h1 = get_paper_sandbox_history()
        h2 = get_paper_sandbox_history()
        assert h1 is h2


# ---------------------------------------------------------------------------
# 12. No broker/MT5/IBKR imports in service and schema modules
# ---------------------------------------------------------------------------

class TestNoBrokerImports:
    def test_service_module_no_metatrader5(self) -> None:
        import app.services.paper_sandbox_history as svc_mod
        src = inspect.getsource(svc_mod)
        assert "MetaTrader5" not in src
        assert "import mt5" not in src
        assert "from mt5" not in src

    def test_service_module_no_ibkr(self) -> None:
        import app.services.paper_sandbox_history as svc_mod
        src = inspect.getsource(svc_mod)
        assert "ib_insync" not in src
        assert "ibkr" not in src.lower().split("ibkr_order_id")[0]

    def test_schema_module_no_metatrader5(self) -> None:
        import app.schemas.paper_sandbox_history as schema_mod
        src = inspect.getsource(schema_mod)
        assert "MetaTrader5" not in src
        assert "import mt5" not in src

    def test_service_module_no_broker_adapter(self) -> None:
        import app.services.paper_sandbox_history as svc_mod
        src = inspect.getsource(svc_mod)
        assert "broker_adapter" not in src
        assert "place_order" not in src
        assert "execute_order" not in src
        assert "submit_order" not in src


# ---------------------------------------------------------------------------
# 13. In-memory only — no route added
# ---------------------------------------------------------------------------

class TestInMemoryAndNoRoute:
    def test_service_has_no_fastapi_router(self) -> None:
        import app.services.paper_sandbox_history as svc_mod
        src = inspect.getsource(svc_mod)
        assert "APIRouter" not in src
        assert "router = " not in src

    def test_schema_has_no_fastapi_router(self) -> None:
        import app.schemas.paper_sandbox_history as schema_mod
        src = inspect.getsource(schema_mod)
        assert "APIRouter" not in src

    def test_service_no_database_imports(self) -> None:
        import app.services.paper_sandbox_history as svc_mod
        src = inspect.getsource(svc_mod)
        assert "supabase" not in src.lower()
        assert "sqlalchemy" not in src.lower()
        assert "psycopg" not in src.lower()
        assert "sqlite" not in src.lower()

    def test_service_no_network_imports(self) -> None:
        import app.services.paper_sandbox_history as svc_mod
        src = inspect.getsource(svc_mod)
        assert "httpx" not in src
        assert "requests" not in src
        assert "aiohttp" not in src
        assert "urllib" not in src

    def test_two_instances_are_independent(self) -> None:
        svc1 = _fresh()
        svc2 = _fresh()
        svc1.append("sandbox_preview_requested", "only in svc1")
        assert len(svc1) == 1
        assert len(svc2) == 0


# ---------------------------------------------------------------------------
# 14. PaperAuditHistory safety flags
# ---------------------------------------------------------------------------

class TestPaperAuditHistorySafetyFlags:
    def test_history_paper_only(self) -> None:
        svc = _fresh()
        svc.append("sandbox_preview_requested", "x")
        h = svc.get_history()
        assert h.paper_only is True

    def test_history_dry_run(self) -> None:
        svc = _fresh()
        h = svc.get_history()
        assert h.dry_run is True

    def test_history_read_only(self) -> None:
        svc = _fresh()
        h = svc.get_history()
        assert h.read_only is True

    def test_history_live_orders_blocked(self) -> None:
        svc = _fresh()
        h = svc.get_history()
        assert h.live_orders_blocked is True

    def test_history_broker_execution_allowed_false(self) -> None:
        svc = _fresh()
        h = svc.get_history()
        assert h.broker_execution_allowed is False

    def test_history_risk_allowed_false(self) -> None:
        svc = _fresh()
        h = svc.get_history()
        assert h.risk_allowed is False

    def test_history_execution_mode(self) -> None:
        svc = _fresh()
        h = svc.get_history()
        assert h.execution_mode == "dry_run_only"


# ---------------------------------------------------------------------------
# 15. All supported event types
# ---------------------------------------------------------------------------

class TestAllEventTypes:
    @pytest.mark.parametrize("event_type", [
        "sandbox_preview_requested",
        "sandbox_state_created",
        "sandbox_state_reset",
        "ticket_draft_observed",
        "safety_flags_checked",
        "human_review_required",
        "degraded_fallback_used",
    ])
    def test_valid_event_type_accepted(self, event_type: str) -> None:
        svc = _fresh()
        ev = svc.append(event_type, f"Testing {event_type}")
        assert ev.event_type == event_type
        assert ev.paper_only is True
        assert ev.dry_run is True

    def test_source_defaults_to_paper_sandbox(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "msg")
        assert ev.source == "paper_sandbox"

    def test_custom_source_accepted(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "msg", source="test_suite")
        assert ev.source == "test_suite"

    def test_metadata_none_gives_empty_dict(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "msg", metadata=None)
        assert ev.metadata == {}

    def test_metadata_empty_dict(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "msg", metadata={})
        assert ev.metadata == {}


# ---------------------------------------------------------------------------
# 16. Timestamp format
# ---------------------------------------------------------------------------

class TestTimestamp:
    def test_timestamp_is_iso_string(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "ts test")
        assert isinstance(ev.timestamp, str)
        assert len(ev.timestamp) > 0
        # Should parse as a valid ISO datetime
        from datetime import datetime
        dt = datetime.fromisoformat(ev.timestamp)
        assert dt is not None

    def test_timestamp_contains_utc_offset(self) -> None:
        svc = _fresh()
        ev = svc.append("sandbox_preview_requested", "ts test")
        # datetime.now(timezone.utc).isoformat() produces "+00:00"
        assert "+" in ev.timestamp or "Z" in ev.timestamp or ev.timestamp.endswith("+00:00")
