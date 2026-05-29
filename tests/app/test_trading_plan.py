"""Tests for the read-only Daily Trading Plan preview endpoint.

Asserts shape, safety posture, and the deliberate absence of any
execution-shaped fields. The endpoint is contract-locked: any new field
that resembles an order ticket should fail one of these tests immediately.
"""

from __future__ import annotations

VALID_BIAS = {"bullish", "bearish", "neutral", "wait"}
VALID_QUALITY = {"low", "medium", "high"}
VALID_RISK_TIER = {"low", "medium", "high"}

# Fields that, if present on a plan item, would make the response look
# like an order ticket. Their absence is part of the safety contract.
EXECUTION_SHAPED_FIELDS = (
    "quantity",
    "lot_size",
    "lot",
    "sl",
    "tp",
    "stop_loss",
    "take_profit",
    "order_id",
    "broker_ref",
    "ticket",
    "status",
    "filled_at",
)

# Imperative phrases that would imply this endpoint is issuing an order.
# We assert these never appear in plan-item text fields.
EXECUTION_PHRASES = (
    "place order",
    "execute trade",
    "submit order",
    "buy now",
    "sell now",
    "live order",
)


def test_trading_plan_endpoint_returns_200(client) -> None:
    response = client.get("/api/terminal/trading-plan")
    assert response.status_code == 200


def test_trading_plan_safety_posture(client) -> None:
    payload = client.get("/api/terminal/trading-plan").json()
    assert payload["dry_run"] is True
    assert payload["auto_trade"] is False
    assert payload["read_only"] is True


def test_trading_plan_max_risk_capped_at_or_below_1pct(client) -> None:
    payload = client.get("/api/terminal/trading-plan").json()
    assert "max_risk_per_trade_pct" in payload
    assert float(payload["max_risk_per_trade_pct"]) <= 1.0


def test_trading_plan_label_marks_read_only(client) -> None:
    payload = client.get("/api/terminal/trading-plan").json()
    label = payload.get("label", "")
    assert "READ-ONLY" in label.upper()
    assert "NO ORDERS PLACED" in label.upper()


def test_trading_plan_items_present_and_well_shaped(client) -> None:
    payload = client.get("/api/terminal/trading-plan").json()
    items = payload["items"]
    assert items, "expected at least one trading-plan item"
    for item in items:
        assert isinstance(item["instrument"], str) and item["instrument"]
        assert item["bias"] in VALID_BIAS
        assert item["setup_quality"] in VALID_QUALITY
        assert item["risk_tier"] in VALID_RISK_TIER


def test_trading_plan_every_item_has_no_trade_condition(client) -> None:
    payload = client.get("/api/terminal/trading-plan").json()
    for item in payload["items"]:
        condition = item.get("no_trade_condition")
        assert isinstance(condition, str) and condition, (
            f"item {item.get('instrument')!r} is missing a non-empty "
            "no_trade_condition"
        )


def test_trading_plan_no_execution_shaped_fields(client) -> None:
    """Plan items must not carry any field that looks like an order ticket."""
    payload = client.get("/api/terminal/trading-plan").json()
    for item in payload["items"]:
        offenders = [f for f in EXECUTION_SHAPED_FIELDS if f in item]
        assert not offenders, (
            f"item {item.get('instrument')!r} has execution-shaped "
            f"field(s): {offenders}"
        )


def test_trading_plan_no_imperative_execution_text(client) -> None:
    """Plan-item text fields must not read like trade instructions."""
    payload = client.get("/api/terminal/trading-plan").json()
    for item in payload["items"]:
        haystack = " ".join(
            str(item.get(k) or "")
            for k in ("no_trade_condition", "setup_area", "notes")
        ).lower()
        for phrase in EXECUTION_PHRASES:
            assert phrase not in haystack, (
                f"item {item.get('instrument')!r} text contains imperative "
                f"execution phrase: {phrase!r}"
            )


def test_trading_plan_generated_at_present(client) -> None:
    payload = client.get("/api/terminal/trading-plan").json()
    assert payload.get("generated_at")


def test_trading_plan_route_is_get_only(client) -> None:
    """POST/PUT/DELETE/PATCH against the plan route must not be accepted."""
    for method in ("post", "put", "delete", "patch"):
        response = getattr(client, method)("/api/terminal/trading-plan")
        # FastAPI returns 405 Method Not Allowed for unregistered methods.
        assert response.status_code == 405, (
            f"{method.upper()} /api/terminal/trading-plan should be 405, "
            f"got {response.status_code}"
        )
