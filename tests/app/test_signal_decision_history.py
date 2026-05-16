from __future__ import annotations

VALID_DIRECTIONS = {"BUY", "SELL", "HOLD", "UNKNOWN"}
VALID_RISK_STATUSES = {"pass", "warn", "blocked", "unknown"}
VALID_DECISIONS = {"dry_run_allowed", "blocked", "watch_only", "no_action"}

SECRET_PATTERNS = [
    "API_KEY",
    "TOKEN",
    "PASSWORD",
    "SECRET",
    "MT5_PASSWORD",
    "CLAUDE_API_KEY",
    "GITHUB_TOKEN",
]

UNSAFE_ROUTE_SEGMENTS = ["execute", "live-trade", "live_trade"]
UNSAFE_EXACT_PATHS = [
    "/api/order",
    "/api/trade/live",
    "/execute",
    "/api/execute",
]


def test_signal_decisions_returns_200(client) -> None:
    response = client.get("/api/signals/decisions")
    assert response.status_code == 200


def test_signal_decisions_safety_flags(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    assert payload["dry_run"] is True
    assert payload["auto_trade"] is False
    assert payload["read_only"] is True


def test_signal_decisions_not_empty(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    assert len(payload["decisions"]) > 0


def test_signal_decisions_all_records_safe(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert rec["dry_run"] is True
        assert rec["auto_trade"] is False
        assert rec["read_only"] is True
        assert rec["stop_loss_required"] is True
        assert rec["take_profit_required"] is True
        assert rec["max_risk_per_trade"] <= 0.01


def test_signal_decisions_at_least_one_blocked(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    decisions = [r["decision"] for r in payload["decisions"]]
    assert "blocked" in decisions


def test_signal_decisions_at_least_one_dry_run_allowed(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    decisions = [r["decision"] for r in payload["decisions"]]
    assert "dry_run_allowed" in decisions


def test_signal_decisions_risk_statuses(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    statuses = {r["risk_status"] for r in payload["decisions"]}
    assert statuses & {"blocked", "pass"}


def test_signal_decisions_limit_1(client) -> None:
    response = client.get("/api/signals/decisions?limit=1")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["decisions"]) <= 1


def test_signal_decisions_limit_200(client) -> None:
    response = client.get("/api/signals/decisions?limit=200")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["decisions"]) <= 200


def test_signal_decisions_high_limit_rejected(client) -> None:
    response = client.get("/api/signals/decisions?limit=500")
    assert response.status_code == 422


def test_signal_decisions_zero_limit_rejected(client) -> None:
    response = client.get("/api/signals/decisions?limit=0")
    assert response.status_code == 422


def test_signal_decisions_negative_limit_rejected(client) -> None:
    response = client.get("/api/signals/decisions?limit=-5")
    assert response.status_code == 422


def test_signal_decisions_symbol_filter_known(client) -> None:
    response = client.get("/api/signals/decisions?symbol=AAPL")
    assert response.status_code == 200
    payload = response.json()
    for rec in payload["decisions"]:
        assert rec["symbol"].upper() == "AAPL"


def test_signal_decisions_symbol_filter_unknown(client) -> None:
    response = client.get("/api/signals/decisions?symbol=ZZZZZZ")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 0
    assert payload["decisions"] == []


def test_signal_decisions_decision_filter(client) -> None:
    response = client.get("/api/signals/decisions?decision=blocked")
    assert response.status_code == 200
    payload = response.json()
    assert payload["decisions"]
    assert all(rec["decision"] == "blocked" for rec in payload["decisions"])
    assert payload["total"] == len(payload["decisions"])


def test_signal_decisions_risk_status_filter(client) -> None:
    response = client.get("/api/signals/decisions?risk_status=pass")
    assert response.status_code == 200
    payload = response.json()
    assert payload["decisions"]
    assert all(rec["risk_status"] == "pass" for rec in payload["decisions"])
    assert payload["total"] == len(payload["decisions"])


def test_signal_decisions_direction_filter(client) -> None:
    response = client.get("/api/signals/decisions?direction=BUY")
    assert response.status_code == 200
    payload = response.json()
    assert payload["decisions"]
    assert all(rec["direction"] == "BUY" for rec in payload["decisions"])
    assert payload["total"] == len(payload["decisions"])


def test_signal_decisions_symbol_and_decision_filter(client) -> None:
    response = client.get("/api/signals/decisions?symbol=AAPL&decision=blocked")
    assert response.status_code == 200
    payload = response.json()
    assert payload["decisions"]
    for rec in payload["decisions"]:
        assert rec["symbol"] == "AAPL"
        assert rec["decision"] == "blocked"
    assert payload["total"] == len(payload["decisions"])


def test_signal_decisions_unmatched_filters_safe_empty(client) -> None:
    response = client.get("/api/signals/decisions?symbol=AAPL&decision=dry_run_allowed")
    assert response.status_code == 200
    payload = response.json()
    assert payload["dry_run"] is True
    assert payload["auto_trade"] is False
    assert payload["read_only"] is True
    assert payload["total"] == 0
    assert payload["decisions"] == []


def test_signal_decisions_invalid_decision_rejected(client) -> None:
    response = client.get("/api/signals/decisions?decision=execute")
    assert response.status_code == 422


def test_signal_decisions_invalid_risk_status_rejected(client) -> None:
    response = client.get("/api/signals/decisions?risk_status=execute")
    assert response.status_code == 422


def test_signal_decisions_invalid_direction_rejected(client) -> None:
    response = client.get("/api/signals/decisions?direction=TRADE")
    assert response.status_code == 422


def test_signal_decisions_filtered_records_safe(client) -> None:
    payload = client.get("/api/signals/decisions?decision=dry_run_allowed").json()
    assert payload["dry_run"] is True
    assert payload["auto_trade"] is False
    assert payload["read_only"] is True
    for rec in payload["decisions"]:
        assert rec["dry_run"] is True
        assert rec["auto_trade"] is False
        assert rec["read_only"] is True
        assert rec["stop_loss_required"] is True
        assert rec["take_profit_required"] is True
        assert rec["max_risk_per_trade"] <= 0.01


def test_signal_decisions_no_secrets(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    raw = str(payload)
    for pattern in SECRET_PATTERNS:
        assert pattern not in raw, f"Possible secret pattern found: {pattern}"


def test_no_unsafe_execution_routes(client) -> None:
    routes = {route.path for route in client.app.routes if hasattr(route, "path")}
    for segment in UNSAFE_ROUTE_SEGMENTS:
        matching = [path for path in routes if segment in path.split("/")]
        assert not matching, f"Unsafe route segment '{segment}' found: {matching}"
    for exact in UNSAFE_EXACT_PATHS:
        assert exact not in routes, f"Unsafe exact route '{exact}' is registered"


def test_signal_decisions_ids_non_empty(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert isinstance(rec["id"], str) and len(rec["id"]) > 0


def test_signal_decisions_timestamps_present(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert "timestamp" in rec
        assert rec["timestamp"] is not None


def test_signal_decisions_symbols_non_empty(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert isinstance(rec["symbol"], str) and len(rec["symbol"]) > 0


def test_signal_decisions_confidence_in_range(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert (
            0.0 <= rec["confidence"] <= 1.0
        ), f"Confidence {rec['confidence']} out of range for {rec['id']}"


def test_signal_decisions_direction_valid(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert rec["direction"] in VALID_DIRECTIONS


def test_signal_decisions_decision_valid(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert rec["decision"] in VALID_DECISIONS


def test_signal_decisions_source_strategy_non_empty(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert isinstance(rec["source"], str) and len(rec["source"]) > 0
        assert isinstance(rec["strategy"], str) and len(rec["strategy"]) > 0


def test_signal_decisions_total_matches_decisions(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    assert payload["total"] == len(payload["decisions"])


def test_signal_decisions_existing_signals_unaffected(client) -> None:
    response = client.get("/api/signals")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# SUPA-011: fallback behaviour tests
#
# These tests verify that the history service correctly transitions between
# real Supabase data (fallback=False) and the seed fixture (fallback=True)
# depending on what read_signal_decisions() returns.
#
# No network calls are made — read_signal_decisions is monkeypatched.
# ---------------------------------------------------------------------------

from datetime import datetime, timezone  # noqa: E402 (appended to module)


def _make_real_record(
    *,
    record_id: str = "real-001",
    symbol: str = "TSLA",
    direction: str = "BUY",
    confidence: float = 0.80,
    risk_status: str = "pass",
    decision: str = "dry_run_allowed",
) -> "SignalDecisionRecord":  # type: ignore[name-defined]
    from app.schemas.signal_decision import SignalDecisionRecord

    return SignalDecisionRecord(
        id=record_id,
        timestamp=datetime.now(timezone.utc),
        symbol=symbol,
        direction=direction,  # type: ignore[arg-type]
        confidence=confidence,
        source="scanner",
        strategy="mtf_confluence",
        risk_status=risk_status,  # type: ignore[arg-type]
        decision=decision,  # type: ignore[arg-type]
        blocked_reason=None,
        dry_run=True,
        auto_trade=False,
        read_only=True,
        stop_loss_required=True,
        take_profit_required=True,
        max_risk_per_trade=0.01,
    )


class TestSupa011FallbackBehaviour:
    """Test SUPA-011 fallback logic in SignalDecisionHistoryService.list_decisions()."""

    def test_fallback_true_when_reader_returns_empty(self, monkeypatch) -> None:
        """When read_signal_decisions returns [], fallback must be True."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService
        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: [])

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions()
        assert response.fallback is True

    def test_fallback_false_when_reader_returns_records(self, monkeypatch) -> None:
        """When read_signal_decisions returns real rows, fallback must be False."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [_make_real_record(record_id="real-001")]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions()
        assert response.fallback is False

    def test_real_records_appear_in_response(self, monkeypatch) -> None:
        """Real records returned by reader should appear in the response."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [_make_real_record(symbol="TSLA", decision="dry_run_allowed")]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions()
        symbols = [d.symbol for d in response.decisions]
        assert "TSLA" in symbols

    def test_fallback_true_when_reader_raises(self, monkeypatch) -> None:
        """When read_signal_decisions raises, fallback must be True."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        import app.services.signal_decision_reader as rdr

        def _raising(**kwargs):
            raise RuntimeError("reader failed")

        monkeypatch.setattr(rdr, "read_signal_decisions", _raising)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions()
        assert response.fallback is True

    def test_seed_data_used_when_reader_returns_empty(self, monkeypatch) -> None:
        """When reader returns [], seed decisions are served."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService, _SEED_DECISIONS

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: [])

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions()
        assert response.total > 0  # seed decisions are non-empty
        assert response.total == len(response.decisions)

    def test_existing_api_shape_preserved_with_real_records(self, monkeypatch) -> None:
        """Response schema is unchanged when real records are served."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [_make_real_record()]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions()
        # Shape checks
        assert hasattr(response, "dry_run")
        assert hasattr(response, "auto_trade")
        assert hasattr(response, "read_only")
        assert hasattr(response, "total")
        assert hasattr(response, "decisions")
        assert hasattr(response, "generated_at")
        assert hasattr(response, "degraded")
        assert hasattr(response, "fallback")

    def test_safety_flags_preserved_with_real_records(self, monkeypatch) -> None:
        """dry_run/auto_trade/read_only always True/False/True with real records."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [_make_real_record()]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions()
        assert response.dry_run is True
        assert response.auto_trade is False
        assert response.read_only is True

    def test_decision_filter_applied_to_real_records(self, monkeypatch) -> None:
        """decision filter works correctly when real records are returned."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [
            _make_real_record(record_id="r1", decision="dry_run_allowed"),
            _make_real_record(record_id="r2", decision="blocked"),
        ]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions(decision="blocked")
        assert all(d.decision == "blocked" for d in response.decisions)

    def test_risk_status_filter_applied_to_real_records(self, monkeypatch) -> None:
        """risk_status filter works correctly when real records are returned."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [
            _make_real_record(record_id="r1", risk_status="pass"),
            _make_real_record(record_id="r2", risk_status="blocked"),
        ]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions(risk_status="pass")
        assert all(d.risk_status == "pass" for d in response.decisions)

    def test_direction_filter_applied_to_real_records(self, monkeypatch) -> None:
        """direction filter works correctly when real records are returned."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [
            _make_real_record(record_id="r1", direction="BUY"),
            _make_real_record(record_id="r2", direction="SELL"),
        ]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions(direction="BUY")
        assert all(d.direction == "BUY" for d in response.decisions)

    def test_limit_respected_with_real_records(self, monkeypatch) -> None:
        """limit is applied correctly when real records are returned."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [
            _make_real_record(record_id=f"r{i}") for i in range(10)
        ]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions(limit=3)
        assert len(response.decisions) <= 3

    def test_total_matches_decisions_with_real_records(self, monkeypatch) -> None:
        """total always equals len(decisions)."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [_make_real_record(record_id=f"r{i}") for i in range(5)]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions()
        assert response.total == len(response.decisions)

    def test_all_real_records_have_safety_invariants(self, monkeypatch) -> None:
        """Every record returned has dry_run=True, auto_trade=False, read_only=True."""
        from app.services.signal_decision_history_service import SignalDecisionHistoryService

        real_records = [_make_real_record(record_id=f"r{i}") for i in range(4)]

        import app.services.signal_decision_reader as rdr

        monkeypatch.setattr(rdr, "read_signal_decisions", lambda **kw: real_records)

        svc = SignalDecisionHistoryService()
        response = svc.list_decisions()
        for rec in response.decisions:
            assert rec.dry_run is True
            assert rec.auto_trade is False
            assert rec.read_only is True
            assert rec.max_risk_per_trade <= 0.01
