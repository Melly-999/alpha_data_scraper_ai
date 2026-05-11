"""BRK-008..011 — Tests for the GET-only broker endpoints.

Endpoints under test:

* ``GET /api/brokers``
* ``GET /api/brokers/{adapter_id}/status``
* ``GET /api/brokers/{adapter_id}/account``
* ``GET /api/brokers/{adapter_id}/positions``

Asserts:

* Each endpoint returns 200 for the default ``safe-disconnected`` adapter
  and the optional read-only ``ibkr-paper`` adapter.
* Responses validate against the BRK-003 schemas.
* Missing adapter ids return HTTP 404 with a clear, secret-free message.
* Non-GET HTTP methods return 405.
* No broker endpoint path contains any forbidden execution / order
  segment.
* The default registry still uses ``safe-disconnected`` as the default.
"""

from __future__ import annotations

import pytest

from app.schemas.broker import (
    BrokerAccountSnapshot,
    BrokerCapabilities,
    BrokerPosition,
    BrokerStatus,
)


# ---------------------------------------------------------------------------
# Test 1 — list endpoint returns 200 + both read-only adapters.
# ---------------------------------------------------------------------------
def test_list_brokers_returns_safe_disconnected_and_ibkr_paper(client) -> None:
    response = client.get("/api/brokers")
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["default_adapter_id"] == "safe-disconnected"
    ids = [a["adapter_id"] for a in body["adapters"]]
    assert set(ids) == {"safe-disconnected", "ibkr-paper"}


# ---------------------------------------------------------------------------
# Test 2 — capabilities payload validates with BrokerCapabilities.
# ---------------------------------------------------------------------------
def test_list_brokers_capabilities_validate(client) -> None:
    body = client.get("/api/brokers").json()
    by_id = {entry["adapter_id"]: entry for entry in body["adapters"]}

    for adapter_id in ("safe-disconnected", "ibkr-paper"):
        caps = BrokerCapabilities(**by_id[adapter_id]["capabilities"])
        assert caps.read_only is True
        assert caps.execution_enabled is False
        assert caps.live_orders_blocked is True
        assert caps.can_place_orders is False
        assert caps.can_cancel_orders is False
        assert caps.can_modify_orders is False

    ibkr_caps = BrokerCapabilities(**by_id["ibkr-paper"]["capabilities"])
    assert ibkr_caps.paper is True


# ---------------------------------------------------------------------------
# Test 3 — status endpoint validates with BrokerStatus.
# ---------------------------------------------------------------------------
def test_status_endpoint_returns_safe_disconnected_status(client) -> None:
    response = client.get("/api/brokers/safe-disconnected/status")
    assert response.status_code == 200, response.text
    status = BrokerStatus(**response.json())
    assert status.adapter_id == "safe-disconnected"
    assert status.connected is False
    assert status.degraded is True
    assert status.read_only is True
    assert status.execution_enabled is False
    assert status.live_orders_blocked is True


# ---------------------------------------------------------------------------
# Test 4 — account endpoint validates with BrokerAccountSnapshot.
# ---------------------------------------------------------------------------
def test_account_endpoint_returns_zero_safe_snapshot(client) -> None:
    response = client.get("/api/brokers/safe-disconnected/account")
    assert response.status_code == 200, response.text
    snap = BrokerAccountSnapshot(**response.json())
    assert snap.adapter_id == "safe-disconnected"
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert snap.read_only is True


# ---------------------------------------------------------------------------
# Test 5 — positions endpoint returns [] and validates as list[BrokerPosition].
# ---------------------------------------------------------------------------
def test_positions_endpoint_returns_empty_list(client) -> None:
    response = client.get("/api/brokers/safe-disconnected/positions")
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    positions = [BrokerPosition(**p) for p in body]
    assert positions == []


def test_ibkr_paper_status_endpoint_returns_safe_default(client) -> None:
    response = client.get("/api/brokers/ibkr-paper/status")
    assert response.status_code == 200, response.text
    status = BrokerStatus(**response.json())
    assert status.adapter_id == "ibkr-paper"
    assert status.connected is False
    assert status.degraded is True
    assert status.read_only is True
    assert status.execution_enabled is False
    assert status.live_orders_blocked is True


def test_ibkr_paper_account_endpoint_returns_safe_zero_snapshot(client) -> None:
    response = client.get("/api/brokers/ibkr-paper/account")
    assert response.status_code == 200, response.text
    snap = BrokerAccountSnapshot(**response.json())
    assert snap.adapter_id == "ibkr-paper"
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert snap.read_only is True


def test_ibkr_paper_positions_endpoint_returns_empty_list(client) -> None:
    response = client.get("/api/brokers/ibkr-paper/positions")
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    positions = [BrokerPosition(**p) for p in body]
    assert positions == []


# ---------------------------------------------------------------------------
# Test 6 — missing adapter returns 404 for status / account / positions.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "suffix",
    ["status", "account", "positions"],
)
def test_missing_adapter_returns_404(client, suffix: str) -> None:
    response = client.get(f"/api/brokers/mt5-live/{suffix}")
    assert response.status_code == 404, response.text
    detail = response.json().get("detail", "")
    # Clear, secret-free message that names the unknown id.
    assert "mt5-live" in detail
    for forbidden in ("password", "token", "secret", "api_key", "credential"):
        assert forbidden not in detail.lower()


# ---------------------------------------------------------------------------
# Test 7 — non-GET methods are not allowed on any new endpoint.
# ---------------------------------------------------------------------------
_GET_ONLY_PATHS: tuple[str, ...] = (
    "/api/brokers",
    "/api/brokers/safe-disconnected/status",
    "/api/brokers/safe-disconnected/account",
    "/api/brokers/safe-disconnected/positions",
    "/api/brokers/ibkr-paper/status",
    "/api/brokers/ibkr-paper/account",
    "/api/brokers/ibkr-paper/positions",
)


@pytest.mark.parametrize("path", _GET_ONLY_PATHS)
@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_non_get_methods_return_405(client, path: str, method: str) -> None:
    response = getattr(client, method)(path)
    assert response.status_code == 405, (
        f"{method.upper()} {path} -> {response.status_code} (expected 405)"
    )


# ---------------------------------------------------------------------------
# Test 8 — no new broker endpoint path contains forbidden segments.
#
# Belt-and-braces: ``tests/app/test_openapi_forbidden_paths.py`` already
# scans the OpenAPI schema for execution-shaped segments. This local
# check pins down the BRK-008..011 paths specifically so a future drift
# (e.g. adding ``/api/brokers/{id}/orders``) fails *this* test even if
# the global scan is somehow weakened.
# ---------------------------------------------------------------------------
_FORBIDDEN_SEGMENTS: tuple[str, ...] = (
    "execute",
    "order",
    "orders",
    "trade",
    "trades",
    "autotrade",
    "live",
    "place",
    "submit",
    "broker_execute",
    "broker-execute",
)


def test_new_broker_endpoint_paths_have_no_forbidden_segments(client) -> None:
    schema = client.app.openapi()
    paths = list(schema.get("paths", {}).keys())
    broker_get_paths = [p for p in paths if p.startswith("/api/brokers")]
    # The four BRK-008..011 paths must be present.
    assert "/api/brokers" in broker_get_paths
    assert "/api/brokers/{adapter_id}/status" in broker_get_paths
    assert "/api/brokers/{adapter_id}/account" in broker_get_paths
    assert "/api/brokers/{adapter_id}/positions" in broker_get_paths
    # None of them may contain a forbidden segment.
    for path in broker_get_paths:
        parts = path.split("/")
        leaked = sorted(set(parts) & set(_FORBIDDEN_SEGMENTS))
        assert not leaked, (
            f"Broker path {path!r} contains forbidden segment(s) {leaked!r}"
        )


# ---------------------------------------------------------------------------
# Test 9 — every BRK-008..011 broker endpoint is registered as GET only
# (defensive: the OpenAPI schema must not advertise any other method on
# these paths).
# ---------------------------------------------------------------------------
def test_new_broker_endpoints_are_get_only_in_openapi(client) -> None:
    schema = client.app.openapi()
    paths = schema.get("paths", {})
    for path in (
        "/api/brokers",
        "/api/brokers/{adapter_id}/status",
        "/api/brokers/{adapter_id}/account",
        "/api/brokers/{adapter_id}/positions",
    ):
        assert path in paths, f"missing OpenAPI path: {path}"
        methods = set(paths[path].keys())
        assert methods == {"get"}, (
            f"{path} advertises methods {methods!r}; expected only 'get'"
        )
