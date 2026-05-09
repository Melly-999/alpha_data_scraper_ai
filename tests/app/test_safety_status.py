"""Tests for the central safety status contract endpoint.

Locks down ``GET /api/safety/status``: shape, posture, pillar membership,
and the GET-only contract. Any drift in the safety posture (autotrade
flipping, dry-run flipping, max-risk creeping above 1%, a pillar going
missing, or the route accepting a mutating method) trips one of these
assertions.
"""

from __future__ import annotations

from datetime import datetime

import pytest

REQUIRED_PILLARS = {
    "DRY_RUN_ACTIVE",
    "READ_ONLY_ACTIVE",
    "AUTO_TRADE_DISABLED",
    "LIVE_ORDERS_BLOCKED",
    "MAX_RISK_CAPPED",
}


def test_safety_status_returns_200(client) -> None:
    response = client.get("/api/safety/status")
    assert response.status_code == 200


def test_safety_status_dry_run_is_true(client) -> None:
    payload = client.get("/api/safety/status").json()
    assert payload["dry_run"] is True


def test_safety_status_auto_trade_is_false(client) -> None:
    payload = client.get("/api/safety/status").json()
    assert payload["auto_trade"] is False


def test_safety_status_read_only_is_true(client) -> None:
    payload = client.get("/api/safety/status").json()
    assert payload["read_only"] is True


def test_safety_status_live_orders_blocked_is_true(client) -> None:
    payload = client.get("/api/safety/status").json()
    assert payload["live_orders_blocked"] is True


def test_safety_status_max_risk_at_or_below_1pct(client) -> None:
    payload = client.get("/api/safety/status").json()
    max_risk = payload.get("max_risk_per_trade_pct")
    assert max_risk is not None
    # Schema-level Field(..., le=1.0) also enforces this; defence in depth.
    assert 0.0 <= float(max_risk) <= 1.0


def test_safety_status_safety_note_present(client) -> None:
    payload = client.get("/api/safety/status").json()
    note = payload.get("safety_note")
    assert isinstance(note, str)
    assert note.strip(), "safety_note must be a non-empty string"


def test_safety_status_generated_at_is_iso_datetime(client) -> None:
    payload = client.get("/api/safety/status").json()
    raw = payload.get("generated_at")
    assert isinstance(raw, str) and raw
    # Must round-trip through fromisoformat without raising.
    datetime.fromisoformat(raw.replace("Z", "+00:00"))


def test_safety_status_contains_all_required_pillars(client) -> None:
    payload = client.get("/api/safety/status").json()
    pillars = set(payload.get("pillars") or [])
    missing = REQUIRED_PILLARS - pillars
    assert not missing, f"missing required safety pillars: {sorted(missing)}"


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_safety_status_rejects_mutating_methods(client, method: str) -> None:
    """Non-GET methods against /api/safety/status must not be accepted."""
    response = getattr(client, method)("/api/safety/status")
    # FastAPI returns 405 for an unregistered method on a registered path.
    assert response.status_code == 405, (
        f"{method.upper()} /api/safety/status should be 405, "
        f"got {response.status_code}"
    )
