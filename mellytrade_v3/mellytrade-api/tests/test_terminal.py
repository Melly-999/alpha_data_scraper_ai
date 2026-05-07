"""Tests for the read-only Terminal UI endpoints.

Asserts the safety contract (dry_run / auto_trade / read_only / risk caps),
absence of execution routes, and that responses do not leak likely secrets.
"""

from __future__ import annotations

import json
import re
from typing import Iterable, List

UNSAFE_PATH_FRAGMENTS = (
    "/execute",
    "/order",
    "/live-trade",
    "/trade/live",
    "/api/execute",
    "/api/order",
    "/api/live-trade",
)

SECRET_TOKENS = (
    "API_KEY",
    "TOKEN",
    "PASSWORD",
    "SECRET",
    "CLAUDE_API_KEY",
    "GITHUB_TOKEN",
    "MT5_PASSWORD",
)

TERMINAL_ENDPOINTS = (
    "/api/terminal/summary",
    "/api/market/overview",
    "/api/watchlist",
    "/api/signals/feed",
    "/api/risk/status",
    "/api/risk/policy",
    "/api/backtest/summary",
    "/api/news/sentiment",
    "/api/positions",
    "/api/mt5/status",
    "/api/terminal/events",
)


def _all_paths(client) -> List[str]:
    schema = client.get("/openapi.json").json()
    return list(schema["paths"].keys())


def _all_methods(client) -> Iterable[tuple[str, str]]:
    schema = client.get("/openapi.json").json()
    for path, ops in schema["paths"].items():
        for method in ops:
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                yield method.upper(), path


def test_terminal_summary_safety_flags(client):
    resp = client.get("/api/terminal/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == "read-only"
    assert body["safety"]["dry_run"] is True
    assert body["safety"]["auto_trade"] is False
    assert body["safety"]["read_only"] is True
    assert body["safety"]["live_orders_blocked"] is True
    broker = body["broker"]
    assert broker["read_only"] is True
    assert broker["execution_enabled"] is False
    assert broker["permissions"]["orders"] == "denied"
    assert broker["permissions"]["live_execution"] == "denied"


def test_risk_status_caps_and_flags(client):
    resp = client.get("/api/risk/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["max_risk_per_trade_pct"] <= 1.0
    assert body["max_risk_per_trade_pct"] > 0
    assert body["dry_run"] is True
    assert body["auto_trade"] is False
    assert body["read_only"] is True
    assert body["stop_loss_required"] is True
    assert body["take_profit_required"] is True
    assert body["live_orders_blocked"] is True


def test_risk_policy_requires_sl_tp_and_blocks_live(client):
    resp = client.get("/api/risk/policy")
    assert resp.status_code == 200
    body = resp.json()
    assert body["requires_stop_loss"] is True
    assert body["requires_take_profit"] is True
    assert body["live_orders_blocked"] is True
    assert body["execution_enabled"] is False


def test_mt5_status_is_read_only(client):
    resp = client.get("/api/mt5/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["read_only"] is True
    assert body.get("execution_enabled", False) is False


def test_terminal_events_include_safety_markers(client):
    resp = client.get("/api/terminal/events")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) > 0
    event_ids = {e["event"] for e in body}
    for required in (
        "dry_run_active",
        "autotrade_disabled",
        "read_only_mode_confirmed",
        "live_orders_blocked",
    ):
        assert required in event_ids, f"missing required event: {required}"


def test_terminal_endpoints_are_get_only(client):
    methods_by_path: dict[str, set[str]] = {}
    for method, path in _all_methods(client):
        methods_by_path.setdefault(path, set()).add(method)
    for path in TERMINAL_ENDPOINTS:
        assert path in methods_by_path, f"terminal endpoint missing: {path}"
        assert methods_by_path[path] == {"GET"}, (
            f"terminal endpoint {path} exposes non-GET methods: "
            f"{methods_by_path[path]}"
        )


def test_no_unsafe_execution_routes(client):
    paths = _all_paths(client)
    for path in paths:
        for unsafe in UNSAFE_PATH_FRAGMENTS:
            assert (
                unsafe not in path
            ), f"unsafe route fragment {unsafe!r} found in registered path {path!r}"


def test_terminal_responses_do_not_leak_secret_tokens(client):
    pattern = re.compile("|".join(re.escape(t) for t in SECRET_TOKENS), re.IGNORECASE)
    for path in TERMINAL_ENDPOINTS:
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} did not return 200"
        body_text = json.dumps(resp.json())
        match = pattern.search(body_text)
        assert (
            match is None
        ), f"{path} response leaks likely secret token: {match.group(0) if match else ''}"


def test_terminal_endpoints_unauthenticated(client):
    """Frontend calls these without an X-API-Key header."""
    for path in TERMINAL_ENDPOINTS:
        resp = client.get(path)
        assert (
            resp.status_code == 200
        ), f"{path} requires auth or failed: {resp.status_code}"
