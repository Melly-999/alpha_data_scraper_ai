"""Repo-wide safety regression checks for the Terminal V1 surface.

These tests are intentionally lightweight: they assert structural invariants
that can be verified statically (route inventory, JSON config values, plain
file contents). They do NOT spin up a separate test stack — they reuse the
existing pytest setup and the ``client`` fixture from ``tests/app/conftest.py``.

The point of these tests is simple: if a future change accidentally adds an
order-placement endpoint, raises the per-trade risk cap above 1%, flips
``dry_run`` to false, removes the ``LIVE ORDERS BLOCKED`` badge, or imports
a mutating API helper into a read-only Terminal page, this file fails fast
and explains why.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

# Repository root inferred from this file's location:
#   tests/app/test_safety_invariants.py  →  ../..
REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROUTES_DIR = REPO_ROOT / "app" / "api" / "routes"
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
CONFIG_JSON = REPO_ROOT / "config.json"

# Path prefixes that make up Terminal V1's read-only observability surface.
# Any registered HTTP route under these prefixes MUST be a GET. Adding a
# mutating route here is a deliberate review event and should fail this test
# loudly so it cannot ship by accident.
TERMINAL_V1_GET_ONLY_PREFIXES: tuple[str, ...] = (
    "/api/terminal",
    "/api/dashboard",
    "/api/audit",
    "/api/positions",
    "/api/orders",
    "/api/logs",
    "/api/signals",
    "/api/account",
    "/api/health",
    "/api/mt5",
    "/api/local",
)

# Small, explicit allowlist of legitimate non-GET routes outside Terminal V1.
# These are *admin / safety* operations, not order placement:
#   - /risk/config (PUT)         → operator updates risk gates
#   - /risk/emergency-stop (POST)→ kill-switch that BLOCKS trading
#   - /broker/dry-run-report (POST) → records dry-run-only execution report
#   - /paper/tickets/draft (POST) → PDS-003 paper-only decision support;
#       no broker execution, no live trading, no paper fills yet;
#       enforces paper_only=true, dry_run=true, risk_allowed=false,
#       broker_execution_allowed=false; human review always required.
# If you need to add another mutating route, add it here together with a
# justification — the review will catch unintended additions.
ADMIN_NON_GET_ALLOWLIST: frozenset[tuple[str, str]] = frozenset(
    {
        ("PUT", "/api/risk/config"),
        ("POST", "/api/risk/emergency-stop"),
        ("POST", "/api/broker/dry-run-report"),
        ("POST", "/api/paper/tickets/draft"),
    }
)

# Path-segment substrings that strongly suggest order placement / live
# execution. Any registered route containing one of these in its path
# segments fails the test. Compared full-segment to avoid false positives
# (e.g. legitimate ``/orders`` history listing — the segment ``orders`` is
# allowed; ``execute`` / ``live-trade`` is not).
DANGEROUS_PATH_SEGMENTS: tuple[str, ...] = (
    "execute",
    "live-trade",
    "live_trade",
    "place-order",
    "place_order",
    "submit-trade",
    "submit_trade",
)

# Frontend file globs that make up the *read-only* Terminal V1 surface.
# The static API-method scan only inspects these files. Files that
# legitimately use mutating helpers (e.g. RiskManagerPage for the admin
# risk-config update and emergency stop) are *deliberately* excluded.
TERMINAL_V1_FRONTEND_GLOBS: tuple[str, ...] = (
    "pages/AuditTrailPage.tsx",
    "pages/DashboardPage.tsx",
    "pages/LogsPage.tsx",
    "pages/PositionsPage.tsx",
    "pages/SignalsPage.tsx",
    "pages/TradeBlotterPage.tsx",
    "pages/AlertsPage.tsx",
    "pages/ReportsPage.tsx",
    "pages/MT5BridgePage.tsx",
)

# Mutating API symbols. Importing or calling these in a read-only Terminal
# page is a regression — the page is meant to be GET-only.
FRONTEND_MUTATING_SYMBOLS: tuple[str, ...] = (
    "apiPost",
    "apiPut",
    "apiDelete",
    "apiPatch",
)

# Function-call shaped regexes used to flag order-placement code in the
# frontend regardless of casing/style.
ORDER_PLACEMENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bplaceOrder\s*\("),
    re.compile(r"\bexecuteOrder\s*\("),
    re.compile(r"\bsubmitTrade\s*\("),
    re.compile(r"\bsubmitOrder\s*\("),
    re.compile(r"\bliveOrder\s*\("),
)

# Button-text patterns for visible JSX nodes. Matches text between an
# opening JSX tag and its close, e.g. ``<button>Place Order</button>``.
ORDER_BUTTON_TEXT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r">\s*Place\s+Order\s*<", re.IGNORECASE),
    re.compile(r">\s*Execute\s+Trade\s*<", re.IGNORECASE),
    re.compile(r">\s*Submit\s+Order\s*<", re.IGNORECASE),
    re.compile(r">\s*Send\s+Live\s+Order\s*<", re.IGNORECASE),
)


# ---------------------------------------------------------------------------
# 1. Backend route safety
# ---------------------------------------------------------------------------


def _registered_routes(client) -> list[tuple[frozenset[str], str]]:
    """Return [(methods, path), ...] for every route on the FastAPI app."""
    out: list[tuple[frozenset[str], str]] = []
    for route in client.app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if path is None or methods is None:
            continue
        # FastAPI auto-adds HEAD/OPTIONS alongside GET; ignore those.
        relevant = frozenset(m for m in methods if m not in {"HEAD", "OPTIONS"})
        if relevant:
            out.append((relevant, path))
    return out


def test_terminal_v1_prefixes_are_get_only(client) -> None:
    """Every registered route under a Terminal V1 prefix uses GET only."""
    offenders: list[str] = []
    for methods, path in _registered_routes(client):
        if not any(path.startswith(prefix) for prefix in TERMINAL_V1_GET_ONLY_PREFIXES):
            continue
        non_get = methods - {"GET"}
        if non_get:
            offenders.append(f"{sorted(non_get)} {path}")
    assert not offenders, (
        "Terminal V1 read-only surface must be GET-only; "
        f"found mutating methods on: {offenders}"
    )


def test_non_get_routes_match_admin_allowlist(client) -> None:
    """Any non-GET route on the API must be on the small admin allowlist."""
    surprises: list[tuple[str, str]] = []
    for methods, path in _registered_routes(client):
        for method in methods - {"GET"}:
            if (method, path) not in ADMIN_NON_GET_ALLOWLIST:
                surprises.append((method, path))
    assert not surprises, (
        "Unexpected non-GET route(s) registered. If this is intentional, "
        "add the (method, path) tuple to ADMIN_NON_GET_ALLOWLIST in "
        "tests/app/test_safety_invariants.py with a justification. "
        f"Offenders: {surprises}"
    )


def test_no_route_path_suggests_order_placement(client) -> None:
    """No registered route path contains an order-placement segment."""
    offenders: list[tuple[str, str]] = []
    for _methods, path in _registered_routes(client):
        segments = path.split("/")
        for danger in DANGEROUS_PATH_SEGMENTS:
            if danger in segments:
                offenders.append((danger, path))
    assert not offenders, (
        "Route path looks like an order-execution endpoint; " f"offenders: {offenders}"
    )


# ---------------------------------------------------------------------------
# 2. config.json safety
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def runtime_config() -> dict:
    assert CONFIG_JSON.is_file(), f"config.json missing at {CONFIG_JSON}"
    return json.loads(CONFIG_JSON.read_text(encoding="utf-8"))


def test_config_json_autotrade_disabled(runtime_config: dict) -> None:
    autotrade = runtime_config.get("autotrade", {})
    assert autotrade.get("enabled") is False, (
        "config.json autotrade.enabled must remain false in the repo. "
        "Live trading must never be the default committed posture."
    )


def test_config_json_dry_run_true(runtime_config: dict) -> None:
    autotrade = runtime_config.get("autotrade", {})
    assert (
        autotrade.get("dry_run") is True
    ), "config.json autotrade.dry_run must remain true."


def test_config_json_min_confidence_at_or_above_70(runtime_config: dict) -> None:
    autotrade = runtime_config.get("autotrade", {})
    min_conf = autotrade.get("min_confidence")
    assert min_conf is not None, "autotrade.min_confidence must be set in config.json"
    # Stored as a percentage (e.g. 70 or 75.0).
    assert (
        float(min_conf) >= 70.0
    ), f"autotrade.min_confidence must remain >= 70 (got {min_conf})."


# ---------------------------------------------------------------------------
# 3. Risk policy safety (live /risk/config endpoint)
# ---------------------------------------------------------------------------


def test_risk_config_endpoint_keeps_max_risk_at_or_below_1pct(client) -> None:
    response = client.get("/api/risk/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("dry_run") is True, "/risk/config dry_run must remain true"
    assert (
        payload.get("auto_trade") is False
    ), "/risk/config auto_trade must remain false"
    max_risk = payload.get("max_risk_per_trade")
    assert max_risk is not None, "max_risk_per_trade must be present"
    assert (
        float(max_risk) <= 1.0
    ), f"max_risk_per_trade must remain <= 1% (got {max_risk}%)."


# ---------------------------------------------------------------------------
# 4. Audit safety (cross-checks Task 2 changes)
# ---------------------------------------------------------------------------


def test_audit_feed_includes_live_orders_blocked(client) -> None:
    payload = client.get("/api/terminal/events").json()
    types = [e["type"] for e in payload["events"]]
    assert (
        "live_orders_blocked" in types
    ), "Terminal audit feed must always emit a live_orders_blocked event"


def test_audit_feed_every_event_is_read_only(client) -> None:
    payload = client.get("/api/terminal/events").json()
    for event in payload["events"]:
        assert (
            event.get("read_only") is True
        ), f"Audit event {event['id']} ({event['type']}) is not read_only"


def test_audit_feed_safety_severity_events_carry_safety_note(client) -> None:
    payload = client.get("/api/terminal/events").json()
    safety_events = [e for e in payload["events"] if e["severity"] == "safety"]
    assert safety_events, "expected at least one safety-severity event"
    for event in safety_events:
        note = event.get("safety_note")
        assert isinstance(note, str) and note, (
            f"safety event {event['id']} ({event['type']}) is missing a "
            "non-empty safety_note explanation"
        )


def test_audit_feed_no_event_claims_live_execution(client) -> None:
    """No audit event message should claim that a live trade was executed."""
    forbidden_phrases = (
        "live order placed",
        "live trade executed",
        "order submitted to broker",
        "live execution active",
    )
    payload = client.get("/api/terminal/events").json()
    for event in payload["events"]:
        haystack = " ".join(
            [
                event.get("message", ""),
                event.get("safety_note") or "",
            ]
        ).lower()
        for phrase in forbidden_phrases:
            assert phrase not in haystack, (
                f"Audit event {event['id']} ({event['type']}) text appears "
                f"to claim live execution: {phrase!r}"
            )


# ---------------------------------------------------------------------------
# 5. Frontend API safety (static text scan)
# ---------------------------------------------------------------------------


def _frontend_file(relpath: str) -> Path:
    path = FRONTEND_SRC / relpath
    assert path.is_file(), f"frontend file missing: {path}"
    return path


def _strip_line_comments(source: str) -> str:
    """Drop // line comments so noisy comments cannot trigger or hide a hit.

    We intentionally keep block comments and string literals untouched so the
    scan remains conservative — a block comment that says ``/* POST */`` will
    still trip the strict mellyApi.ts test below, which is fine because that
    file should not need such a comment.
    """
    out_lines: list[str] = []
    for line in source.splitlines():
        idx = line.find("//")
        out_lines.append(line[:idx] if idx != -1 else line)
    return "\n".join(out_lines)


def test_melly_api_client_is_get_only() -> None:
    """frontend/src/lib/mellyApi.ts must use GET as its only HTTP method."""
    source = _frontend_file("lib/mellyApi.ts").read_text(encoding="utf-8")
    code = _strip_line_comments(source)
    method_literals = re.findall(r"method:\s*\"([A-Z]+)\"", code)
    assert method_literals, "no `method:` literal found — has the file moved?"
    non_get = [m for m in method_literals if m != "GET"]
    assert not non_get, (
        "mellyApi.ts must remain GET-only (Terminal V1 read-only client). "
        f"Found non-GET method literal(s): {non_get}"
    )


@pytest.mark.parametrize("relpath", TERMINAL_V1_FRONTEND_GLOBS)
def test_terminal_pages_do_not_import_mutating_api_helpers(
    relpath: str,
) -> None:
    """Read-only Terminal pages must not import POST/PUT/DELETE helpers."""
    path = FRONTEND_SRC / relpath
    if not path.is_file():
        pytest.skip(f"{relpath} not present in this branch")
    source = path.read_text(encoding="utf-8")
    code = _strip_line_comments(source)
    found = [sym for sym in FRONTEND_MUTATING_SYMBOLS if re.search(rf"\b{sym}\b", code)]
    assert not found, (
        f"{relpath} imports/uses mutating API helper(s) {found}; "
        "Terminal V1 pages must remain read-only. If this is admin UX, "
        "move it out of TERMINAL_V1_FRONTEND_GLOBS with a comment."
    )


@pytest.mark.parametrize("relpath", TERMINAL_V1_FRONTEND_GLOBS)
def test_terminal_pages_have_no_order_placement_calls(relpath: str) -> None:
    """No placeOrder/executeOrder/submitTrade-style calls in Terminal pages."""
    path = FRONTEND_SRC / relpath
    if not path.is_file():
        pytest.skip(f"{relpath} not present in this branch")
    code = _strip_line_comments(path.read_text(encoding="utf-8"))
    hits = [p.pattern for p in ORDER_PLACEMENT_PATTERNS if p.search(code)]
    assert not hits, f"{relpath} contains an order-placement-shaped call: {hits}"


@pytest.mark.parametrize("relpath", TERMINAL_V1_FRONTEND_GLOBS)
def test_terminal_pages_have_no_order_button_text(relpath: str) -> None:
    """No visible JSX text suggesting an order/execution button."""
    path = FRONTEND_SRC / relpath
    if not path.is_file():
        pytest.skip(f"{relpath} not present in this branch")
    code = _strip_line_comments(path.read_text(encoding="utf-8"))
    hits = [p.pattern for p in ORDER_BUTTON_TEXT_PATTERNS if p.search(code)]
    assert not hits, f"{relpath} contains order-button-shaped JSX text: {hits}"
