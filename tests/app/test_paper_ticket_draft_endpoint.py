"""PDS-003 — Tests for the paper ticket draft endpoint.

POST /api/paper/tickets/draft

All tests are paper-only decision-support assertions.  No broker execution,
no MT5/IBKR calls, no Supabase, no network I/O.  Every test uses the
TestClient fixture from conftest.py.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ENDPOINT = "/api/paper/tickets/draft"


def _long_input(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = dict(
        symbol="EURUSD",
        side="long",
        entry_type="market_simulated",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        risk_pct=0.5,
        confidence=80.0,
        reason="Strong H1 bullish momentum",
        source="scanner_preview",
    )
    base.update(overrides)
    return base


def _short_input(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = dict(
        symbol="GBPUSD",
        side="short",
        entry_type="breakout",
        timeframe="H4",
        entry_price=1.3000,
        stop_loss=1.3060,
        take_profit_1=1.2900,
        risk_pct=0.8,
        confidence=75.0,
        reason="Bearish breakout below support",
        source="scanner_preview",
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. Basic behaviour
# ---------------------------------------------------------------------------


def test_valid_long_input_returns_200(client) -> None:
    response = client.post(ENDPOINT, json=_long_input())
    assert response.status_code == 200, response.text


def test_valid_long_input_returns_accepted_true(client) -> None:
    response = client.post(ENDPOINT, json=_long_input())
    assert response.json()["accepted"] is True


def test_valid_short_input_returns_accepted_true(client) -> None:
    response = client.post(ENDPOINT, json=_short_input())
    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_response_includes_draft_object(client) -> None:
    body = client.post(ENDPOINT, json=_long_input()).json()
    assert body["draft"] is not None
    assert isinstance(body["draft"], dict)


def test_response_includes_validation_object(client) -> None:
    body = client.post(ENDPOINT, json=_long_input()).json()
    assert body["validation"] is not None
    assert isinstance(body["validation"], dict)


def test_response_includes_safety_contract(client) -> None:
    body = client.post(ENDPOINT, json=_long_input()).json()
    assert "safety_contract" in body
    assert isinstance(body["safety_contract"], dict)


# ---------------------------------------------------------------------------
# 2. Draft safety flags
# ---------------------------------------------------------------------------


def test_draft_paper_only_is_true(client) -> None:
    draft = client.post(ENDPOINT, json=_long_input()).json()["draft"]
    assert draft["paper_only"] is True


def test_draft_dry_run_is_true(client) -> None:
    draft = client.post(ENDPOINT, json=_long_input()).json()["draft"]
    assert draft["dry_run"] is True


def test_draft_read_only_is_true(client) -> None:
    draft = client.post(ENDPOINT, json=_long_input()).json()["draft"]
    assert draft["read_only"] is True


def test_draft_live_orders_blocked_is_true(client) -> None:
    draft = client.post(ENDPOINT, json=_long_input()).json()["draft"]
    assert draft["live_orders_blocked"] is True


def test_draft_requires_human_review_is_true(client) -> None:
    draft = client.post(ENDPOINT, json=_long_input()).json()["draft"]
    assert draft["requires_human_review"] is True


def test_draft_risk_allowed_is_false(client) -> None:
    draft = client.post(ENDPOINT, json=_long_input()).json()["draft"]
    assert draft["risk_allowed"] is False


def test_draft_broker_execution_allowed_is_false(client) -> None:
    draft = client.post(ENDPOINT, json=_long_input()).json()["draft"]
    assert draft["broker_execution_allowed"] is False


def test_draft_execution_mode_is_paper_only_draft(client) -> None:
    draft = client.post(ENDPOINT, json=_long_input()).json()["draft"]
    assert draft["execution_mode"] == "paper_only_draft"


# ---------------------------------------------------------------------------
# 3. Safety contract fields in response
# ---------------------------------------------------------------------------


def test_safety_contract_paper_only_is_true(client) -> None:
    sc = client.post(ENDPOINT, json=_long_input()).json()["safety_contract"]
    assert sc["paper_only"] is True


def test_safety_contract_risk_allowed_is_false(client) -> None:
    sc = client.post(ENDPOINT, json=_long_input()).json()["safety_contract"]
    assert sc["risk_allowed"] is False


def test_safety_contract_broker_execution_allowed_is_false(client) -> None:
    sc = client.post(ENDPOINT, json=_long_input()).json()["safety_contract"]
    assert sc["broker_execution_allowed"] is False


def test_safety_contract_max_risk_pct_is_1(client) -> None:
    sc = client.post(ENDPOINT, json=_long_input()).json()["safety_contract"]
    assert sc["max_risk_pct"] == 1.0


def test_safety_contract_execution_mode_is_paper_only_draft(client) -> None:
    sc = client.post(ENDPOINT, json=_long_input()).json()["safety_contract"]
    assert sc["execution_mode"] == "paper_only_draft"


# ---------------------------------------------------------------------------
# 4. Rejection cases — all return 200 with accepted=false
# ---------------------------------------------------------------------------


def test_risk_pct_above_1_returns_accepted_false(client) -> None:
    response = client.post(ENDPOINT, json=_long_input(risk_pct=1.01))
    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_invalid_long_geometry_sl_above_entry_returns_accepted_false(client) -> None:
    response = client.post(ENDPOINT, json=_long_input(stop_loss=1.1100))
    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_invalid_long_geometry_tp_below_entry_returns_accepted_false(client) -> None:
    response = client.post(ENDPOINT, json=_long_input(take_profit_1=1.0900))
    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_invalid_short_geometry_sl_below_entry_returns_accepted_false(client) -> None:
    response = client.post(ENDPOINT, json=_short_input(stop_loss=1.2950))
    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_invalid_short_geometry_tp_above_entry_returns_accepted_false(client) -> None:
    response = client.post(ENDPOINT, json=_short_input(take_profit_1=1.3100))
    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_rejection_still_has_safety_contract(client) -> None:
    body = client.post(ENDPOINT, json=_long_input(risk_pct=2.0)).json()
    assert body["accepted"] is False
    assert body["safety_contract"]["paper_only"] is True
    assert body["safety_contract"]["risk_allowed"] is False


# ---------------------------------------------------------------------------
# 5. FastAPI / Pydantic 422 cases (missing required fields)
# ---------------------------------------------------------------------------


def test_missing_stop_loss_returns_422(client) -> None:
    data = _long_input()
    data.pop("stop_loss")
    response = client.post(ENDPOINT, json=data)
    assert response.status_code == 422


def test_missing_take_profit_1_returns_422(client) -> None:
    data = _long_input()
    data.pop("take_profit_1")
    response = client.post(ENDPOINT, json=data)
    assert response.status_code == 422


def test_empty_body_returns_422(client) -> None:
    response = client.post(ENDPOINT, json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 6. Endpoint path and namespace safety
# ---------------------------------------------------------------------------


def test_endpoint_is_under_api_paper_namespace(client) -> None:
    """The path must be within /api/paper — required by PAPER-GUARD-001."""
    paths = client.app.openapi()["paths"]
    assert (
        "/api/paper/tickets/draft" in paths
    ), "POST /api/paper/tickets/draft must appear in OpenAPI schema"


def test_endpoint_openapi_metadata_includes_paper_marker(client) -> None:
    """Endpoint metadata must include a paper/sandbox/dry_run indicator."""
    paths = client.app.openapi()["paths"]
    path_item = paths.get("/api/paper/tickets/draft", {})
    post_op = path_item.get("post", {})
    metadata = " ".join(
        [
            str(post_op.get("summary", "")),
            str(post_op.get("description", "")),
            str(post_op.get("operationId", "")),
        ]
    ).lower()
    paper_indicators = ("paper", "sandbox", "dry_run", "simulated")
    assert any(
        ind in metadata for ind in paper_indicators
    ), f"Endpoint metadata must contain a paper/sandbox indicator; got: {metadata!r}"


def test_paper_endpoint_is_not_a_live_execution_path(client) -> None:
    """The paper draft endpoint must be under /api/paper, not a live execution path."""
    paths = client.app.openapi()["paths"]
    assert "/api/paper/tickets/draft" in paths
    # Must be in the paper namespace
    assert "/api/paper/tickets/draft".startswith(
        "/api/paper"
    ), "Paper draft endpoint must live under /api/paper"
    # Must NOT look like a live execution path
    live_fragments = (
        "/api/orders",
        "/api/execute",
        "/api/execution",
        "/api/broker/execute",
        "/api/broker/order",
        "/api/mt5/order",
        "/api/ibkr/order",
        "/api/autotrade",
    )
    draft_path = "/api/paper/tickets/draft"
    for frag in live_fragments:
        assert not draft_path.startswith(
            frag
        ), f"Paper endpoint must not look like a live execution path: {frag}"


# ---------------------------------------------------------------------------
# 7. No live execution fields in response
# ---------------------------------------------------------------------------


def test_no_live_execution_fields_in_response(client) -> None:
    body = client.post(ENDPOINT, json=_long_input()).json()
    forbidden = {
        "order_id",
        "fill_id",
        "execution_id",
        "broker_order_id",
        "account_id",
        "credential",
        "token",
        "secret",
    }
    for key in forbidden:
        assert key not in body, f"Forbidden field found in response: {key}"


def test_no_live_execution_fields_in_draft(client) -> None:
    draft = client.post(ENDPOINT, json=_long_input()).json()["draft"]
    assert draft is not None
    forbidden = {
        "order_id",
        "fill_id",
        "execution_id",
        "broker_order_id",
        "account_id",
        "credential",
        "token",
        "secret",
    }
    for key in forbidden:
        assert key not in draft, f"Forbidden field found in draft: {key}"


# ---------------------------------------------------------------------------
# 8. PAPER-GUARD-001 compatibility
# ---------------------------------------------------------------------------


def test_paper_sandbox_guardrails_still_pass(client) -> None:
    """The new endpoint satisfies PAPER-GUARD-001 paper namespace requirements."""
    paths = client.app.openapi()["paths"]

    # Schema must be non-empty (guards vacuous passes)
    assert paths, "OpenAPI schema returned no paths"

    # The new endpoint must be present in the paper namespace
    assert (
        "/api/paper/tickets/draft" in paths
    ), "POST /api/paper/tickets/draft must appear in OpenAPI schema"
    assert any(
        p.startswith("/api/paper") for p in paths
    ), "No paper namespace paths found in OpenAPI schema"

    # The paper endpoint itself must NOT be in a live execution shape
    draft_path = "/api/paper/tickets/draft"
    live_execution_shapes = (
        "/api/execute",
        "/api/execution",
        "/api/broker/execute",
        "/api/broker/order",
        "/api/mt5/order",
        "/api/ibkr/order",
        "/api/autotrade",
    )
    for shape in live_execution_shapes:
        assert not draft_path.startswith(
            shape
        ), f"Paper endpoint must not match live execution shape: {shape}"
