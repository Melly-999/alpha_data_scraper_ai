"""Tests for SUPA-008: scanner audit event emitter.

No real network calls — all Supabase interactions are replaced by injectable
_insert_fn or a None client to trigger the degraded path.

Test categories:
  1.  Returns a single AuditEventRecord
  2.  Event type is scanner_preview_fetched
  3.  Source is "scanner"
  4.  Safety invariants — read_only=True, dry_run=True
  5.  Success path — persisted=True, degraded=False with fake _insert_fn
  6.  Degraded path — persisted=False, degraded=True when no client/no _insert_fn
  7.  Insert failure — does not raise; degrades gracefully
  8.  Metadata safety — only safe keys, no forbidden keys, no execution-shaped keys
  9.  Injectable _insert_fn called exactly once with correct arguments
  10. Payload safety — read_only, dry_run, source in every payload
  11. Scanner endpoint returns 200 even if audit write raises
  12. Startup audit unaffected by scanner audit
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from app.schemas.audit_event import AuditEventRecord
from app.schemas.signal_scanner import SignalScannerBatch
from app.services.scanner_audit import emit_scanner_preview_event
from app.services.signal_scanner import scan_symbols

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


def _make_batch(symbols: list[str] | None = None) -> SignalScannerBatch:
    """Return a real SignalScannerBatch via scan_symbols()."""
    return scan_symbols(symbols or ["EURUSD", "XAUUSD", "AAPL"])


def _make_empty_batch() -> SignalScannerBatch:
    return scan_symbols([])


def _make_fake_insert_fn() -> tuple[Any, list[tuple[str, dict[str, Any]]]]:
    """Return (fn, calls) — fn records every (table, payload) call in calls."""
    calls: list[tuple[str, dict[str, Any]]] = []

    def _fn(table: str, payload: dict[str, Any]) -> Any:
        calls.append((table, dict(payload)))
        response = MagicMock()
        response.data = [{"id": "scanner-test-id-001"}]
        return response

    return _fn, calls


def _make_failing_insert_fn() -> Any:
    """Return an _insert_fn that always raises RuntimeError."""

    def _fn(table: str, payload: dict[str, Any]) -> Any:
        raise RuntimeError("simulated Supabase scanner insert failure")

    return _fn


# ---------------------------------------------------------------------------
# 1. Returns a single AuditEventRecord
# ---------------------------------------------------------------------------


class TestReturnShape:
    def test_returns_audit_event_record(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert isinstance(result, AuditEventRecord)

    def test_returns_single_record_not_list(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert not isinstance(result, list)

    def test_returns_record_with_insert_fn(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert isinstance(result, AuditEventRecord)

    def test_returns_record_on_empty_batch(self) -> None:
        result = emit_scanner_preview_event(_make_empty_batch())
        assert isinstance(result, AuditEventRecord)


# ---------------------------------------------------------------------------
# 2. Event type is scanner_preview_fetched
# ---------------------------------------------------------------------------


class TestEventType:
    def test_event_type_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert result.event_type == "scanner_preview_fetched"

    def test_event_type_degraded_path(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert result.event_type == "scanner_preview_fetched"

    def test_event_type_on_insert_failure(self) -> None:
        result = emit_scanner_preview_event(
            _make_batch(), _insert_fn=_make_failing_insert_fn()
        )
        assert result.event_type == "scanner_preview_fetched"


# ---------------------------------------------------------------------------
# 3. Source is "scanner"
# ---------------------------------------------------------------------------


class TestSource:
    def test_source_is_scanner_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert result.source == "scanner"

    def test_source_is_scanner_degraded_path(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert result.source == "scanner"

    def test_source_is_scanner_on_insert_failure(self) -> None:
        result = emit_scanner_preview_event(
            _make_batch(), _insert_fn=_make_failing_insert_fn()
        )
        assert result.source == "scanner"


# ---------------------------------------------------------------------------
# 4. Safety invariants
# ---------------------------------------------------------------------------


class TestSafetyInvariants:
    def test_read_only_true_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert result.read_only is True

    def test_dry_run_true_success_path(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert result.dry_run is True

    def test_read_only_true_degraded_path(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert result.read_only is True

    def test_dry_run_true_degraded_path(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert result.dry_run is True

    def test_read_only_true_on_insert_failure(self) -> None:
        result = emit_scanner_preview_event(
            _make_batch(), _insert_fn=_make_failing_insert_fn()
        )
        assert result.read_only is True

    def test_dry_run_true_on_insert_failure(self) -> None:
        result = emit_scanner_preview_event(
            _make_batch(), _insert_fn=_make_failing_insert_fn()
        )
        assert result.dry_run is True


# ---------------------------------------------------------------------------
# 5. Success path
# ---------------------------------------------------------------------------


class TestSuccessPath:
    def test_persisted_true_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert result.persisted is True

    def test_degraded_false_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert result.degraded is False

    def test_id_assigned_on_success(self) -> None:
        fn, _ = _make_fake_insert_fn()
        result = emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert result.id is not None


# ---------------------------------------------------------------------------
# 6. Degraded path
# ---------------------------------------------------------------------------


class TestDegradedPath:
    def test_degraded_true_when_no_client_no_fn(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert result.degraded is True

    def test_persisted_false_when_degraded(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert result.persisted is False

    def test_degraded_reason_set(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert result.degraded_reason is not None
        assert len(result.degraded_reason) > 0

    def test_returns_record_even_when_degraded(self) -> None:
        result = emit_scanner_preview_event(_make_batch())
        assert isinstance(result, AuditEventRecord)


# ---------------------------------------------------------------------------
# 7. Insert failure — does not raise
# ---------------------------------------------------------------------------


class TestInsertFailure:
    def test_no_exception_raised_on_insert_failure(self) -> None:
        result = emit_scanner_preview_event(
            _make_batch(), _insert_fn=_make_failing_insert_fn()
        )
        assert isinstance(result, AuditEventRecord)

    def test_degraded_true_on_insert_failure(self) -> None:
        result = emit_scanner_preview_event(
            _make_batch(), _insert_fn=_make_failing_insert_fn()
        )
        assert result.degraded is True

    def test_persisted_false_on_insert_failure(self) -> None:
        result = emit_scanner_preview_event(
            _make_batch(), _insert_fn=_make_failing_insert_fn()
        )
        assert result.persisted is False

    def test_degraded_reason_contains_exception_message(self) -> None:
        result = emit_scanner_preview_event(
            _make_batch(), _insert_fn=_make_failing_insert_fn()
        )
        assert result.degraded_reason is not None
        assert "simulated Supabase scanner insert failure" in result.degraded_reason


# ---------------------------------------------------------------------------
# 8. Metadata safety
# ---------------------------------------------------------------------------


class TestMetadataSafety:
    def test_metadata_contains_symbol_count(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(["EURUSD", "XAUUSD"]), _insert_fn=fn)
        assert len(calls) == 1
        assert calls[0][1].get("metadata", {}).get("symbol_count") == 2

    def test_metadata_symbol_count_matches_batch(self) -> None:
        fn, calls = _make_fake_insert_fn()
        batch = _make_batch(["AAPL", "NVDA", "MSFT", "TSLA"])
        emit_scanner_preview_event(batch, _insert_fn=fn)
        assert calls[0][1]["metadata"]["symbol_count"] == len(batch.results)

    def test_metadata_contains_mode(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert "mode" in calls[0][1]["metadata"]

    def test_metadata_mode_is_safe_string(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        mode = calls[0][1]["metadata"]["mode"]
        assert isinstance(mode, str)
        assert len(mode) > 0

    def test_metadata_contains_degraded_flag(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert "degraded" in calls[0][1]["metadata"]

    def test_no_forbidden_keys_in_metadata(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        metadata = calls[0][1].get("metadata", {})
        forbidden_found = _KNOWN_FORBIDDEN_KEYS & metadata.keys()
        assert not forbidden_found, f"Forbidden keys found: {forbidden_found}"

    def test_no_execution_shaped_keys_in_metadata(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        metadata = calls[0][1].get("metadata", {})
        execution_found = _KNOWN_EXECUTION_KEYS & metadata.keys()
        assert not execution_found, f"Execution-shaped keys found: {execution_found}"

    def test_no_prices_in_metadata(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        metadata = calls[0][1].get("metadata", {})
        price_keys = {"price", "bid", "ask", "open", "close", "high", "low", "ohlc"}
        assert not (price_keys & metadata.keys())

    def test_no_account_id_in_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert "account_id" not in str(calls[0][1])

    def test_no_service_role_in_payload(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert "service_role" not in str(calls[0][1])

    def test_metadata_keys_are_only_allowed_set(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        metadata_keys = set(calls[0][1].get("metadata", {}).keys())
        assert metadata_keys <= {"symbol_count", "mode", "degraded"}

    def test_symbol_count_zero_on_empty_batch(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_empty_batch(), _insert_fn=fn)
        assert calls[0][1]["metadata"]["symbol_count"] == 0


# ---------------------------------------------------------------------------
# 9. Injectable _insert_fn called exactly once
# ---------------------------------------------------------------------------


class TestInjectableInsertFn:
    def test_insert_fn_called_exactly_once(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert len(calls) == 1

    def test_insert_fn_targets_audit_events_table(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert calls[0][0] == "audit_events"

    def test_insert_fn_not_called_on_degraded_path(self) -> None:
        fn, calls = _make_fake_insert_fn()
        # No _insert_fn, no client → degraded path, no insert attempt
        emit_scanner_preview_event(_make_batch())
        assert len(calls) == 0


# ---------------------------------------------------------------------------
# 10. Payload safety — read_only, dry_run, source in every payload
# ---------------------------------------------------------------------------


class TestPayloadSafety:
    def test_payload_has_read_only_true(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert calls[0][1].get("read_only") is True

    def test_payload_has_dry_run_true(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert calls[0][1].get("dry_run") is True

    def test_payload_has_source_scanner(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert calls[0][1].get("source") == "scanner"

    def test_payload_has_event_type(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        assert calls[0][1].get("event_type") == "scanner_preview_fetched"

    def test_payload_has_message(self) -> None:
        fn, calls = _make_fake_insert_fn()
        emit_scanner_preview_event(_make_batch(), _insert_fn=fn)
        msg = calls[0][1].get("message", "")
        assert len(msg) > 0


# ---------------------------------------------------------------------------
# 11. Scanner endpoint returns 200 even if audit write raises
# ---------------------------------------------------------------------------


class TestScannerEndpointResilience:
    def test_scanner_preview_returns_200_normally(self, client) -> None:
        """Baseline: endpoint returns 200 in normal test conditions."""
        response = client.get("/api/signals/scanner/preview")
        assert response.status_code == 200

    def test_scanner_preview_response_has_required_fields(self, client) -> None:
        response = client.get("/api/signals/scanner/preview")
        data = response.json()
        assert "results" in data
        assert "read_only" in data
        assert "execution_mode" in data

    def test_scanner_preview_read_only_is_true(self, client) -> None:
        response = client.get("/api/signals/scanner/preview")
        assert response.json()["read_only"] is True

    def test_scanner_preview_execution_mode_dry_run(self, client) -> None:
        response = client.get("/api/signals/scanner/preview")
        assert response.json()["execution_mode"] == "dry_run_only"

    def test_scanner_preview_returns_200_if_audit_write_raises(
        self, client, monkeypatch
    ) -> None:
        """Endpoint must still return 200 if the underlying audit write fails."""

        def _raising_write(*args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("simulated audit write failure in route test")

        # Patch write_audit_event in scanner_audit's namespace so any call
        # from emit_scanner_preview_event raises.
        monkeypatch.setattr(
            "app.services.scanner_audit.write_audit_event", _raising_write
        )

        response = client.get("/api/signals/scanner/preview")
        assert response.status_code == 200
        data = response.json()
        assert data["read_only"] is True
        assert data["execution_mode"] == "dry_run_only"

    def test_scanner_preview_with_symbols_param_returns_200(self, client) -> None:
        response = client.get("/api/signals/scanner/preview?symbols=EURUSD,XAUUSD")
        assert response.status_code == 200

    def test_scanner_preview_results_have_no_execution_fields(self, client) -> None:
        response = client.get("/api/signals/scanner/preview")
        data = response.json()
        for result in data.get("results", []):
            assert result.get("risk_allowed") is False
            assert result.get("execution_mode") == "dry_run_only"
            assert result.get("requires_human_review") is True


# ---------------------------------------------------------------------------
# 12. Startup audit unaffected by scanner audit
# ---------------------------------------------------------------------------


class TestStartupAuditUnaffected:
    def test_emit_startup_events_still_returns_3_records(self) -> None:
        """Verify startup audit works independently of scanner audit."""
        from app.services.startup_audit import emit_startup_events

        result = emit_startup_events()
        assert len(result) == 3

    def test_emit_startup_events_source_still_system(self) -> None:
        from app.services.startup_audit import emit_startup_events

        result = emit_startup_events()
        for record in result:
            assert record.source == "system"

    def test_startup_and_scanner_use_different_sources(self) -> None:
        from app.services.startup_audit import emit_startup_events

        startup_records = emit_startup_events()
        scanner_record = emit_scanner_preview_event(_make_batch())

        assert all(r.source == "system" for r in startup_records)
        assert scanner_record.source == "scanner"
