"""TEST-001 — OpenAPI forbidden path scan.

Complements ``test_safety_invariants.py`` (which scans
``client.app.routes`` — the registered FastAPI route objects) by
scanning the **OpenAPI schema** (``client.app.openapi()``) for the same
class of forbidden execution / order / trading path segments.

The two checks cover different failure modes:

* Registered routes can include endpoints with ``include_in_schema=False``
  that don't appear in the OpenAPI schema.
* OpenAPI can include paths registered through extras (mounted apps,
  custom additions) that aren't in ``client.app.routes``.

If an order-placement-shaped path ever appears in either surface, this
test fails with a clear message naming the offending path and segment.

Safety contract preserved by every assertion:
- ``autotrade.enabled = false``
- ``dry_run = true``
- ``read_only = true`` on the Terminal V1 surface
- ``live_orders_blocked = true``
- ``max_risk_per_trade <= 1%``
- No live execution paths reachable from the API.
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Forbidden segments — single-token URL segments that, if they appear as
# their own slash-delimited segment, indicate an execution-shaped route.
# Matched via exact equality against split path segments to avoid false
# positives (e.g. ``executor`` / ``executive`` / ``executable`` in legitimate
# names won't trigger ``execute``).
# ---------------------------------------------------------------------------
FORBIDDEN_SINGLE_SEGMENTS: tuple[str, ...] = (
    "execute",
    "execute-trade",
    "execute_trade",
    "live-trade",
    "live_trade",
    "place-order",
    "place_order",
    "submit-order",
    "submit_order",
    "broker-execute",
    "broker_execute",
    "disable-dry-run",
    "enable-autotrade",
)

# ---------------------------------------------------------------------------
# Forbidden compound patterns — two-segment substrings that must not
# appear adjacent in any path. Matched via plain substring search on the
# full normalised path string.
# ---------------------------------------------------------------------------
FORBIDDEN_COMPOUND_PATTERNS: tuple[str, ...] = (
    "order/place",
    "order/submit",
    "trade/execute",
    "trading/execute",
    "autotrade/enable",
    "dry-run/disable",
)


def _all_openapi_paths(client) -> list[str]:
    """Return every path key from the OpenAPI schema.

    Uses the FastAPI app's ``.openapi()`` method (cached after first call).
    Returns ``[]`` only if the schema has no ``paths`` key, which would be
    a separate red flag the test would surface.
    """
    schema = client.app.openapi()
    paths = schema.get("paths") or {}
    return list(paths.keys())


# ---------------------------------------------------------------------------
# Sanity / positive control — proves the test is actually reading the
# OpenAPI schema. If FastAPI's openapi() were ever broken, every other
# assertion in this file would pass vacuously; this one would catch that.
# ---------------------------------------------------------------------------


def test_openapi_schema_is_readable_and_non_empty(client) -> None:
    """The OpenAPI schema must list at least the canonical safety/health routes."""
    paths = set(_all_openapi_paths(client))
    assert paths, "OpenAPI schema returned no paths — read-back is broken"
    # Two well-known paths from the safety surface; both have shipped on `main`.
    assert "/api/health" in paths, (
        f"expected /api/health in OpenAPI paths, got {sorted(paths)[:5]} ..."
    )
    assert "/api/safety/status" in paths, (
        f"expected /api/safety/status (PR #57) in OpenAPI paths; "
        f"first few: {sorted(paths)[:5]}"
    )


# ---------------------------------------------------------------------------
# 1. Single-segment forbidden tokens.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("segment", FORBIDDEN_SINGLE_SEGMENTS)
def test_no_openapi_path_contains_forbidden_single_segment(
    client, segment: str
) -> None:
    """No OpenAPI path may contain ``segment`` as one of its slash parts."""
    offenders: list[str] = []
    for path in _all_openapi_paths(client):
        # Split on '/' to get exact path segments. Path-template parts like
        # ``{signal_id}`` are left intact and won't match any forbidden token.
        parts = path.split("/")
        if segment in parts:
            offenders.append(path)
    assert not offenders, (
        f"forbidden execution segment '{segment}' appears in OpenAPI "
        f"path(s): {offenders}"
    )


# ---------------------------------------------------------------------------
# 2. Compound substring patterns (two consecutive segments).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("pattern", FORBIDDEN_COMPOUND_PATTERNS)
def test_no_openapi_path_contains_forbidden_compound_pattern(
    client, pattern: str
) -> None:
    """No OpenAPI path may contain ``pattern`` as a substring."""
    offenders = [p for p in _all_openapi_paths(client) if pattern in p]
    assert not offenders, (
        f"forbidden execution pattern '{pattern}' appears in OpenAPI "
        f"path(s): {offenders}"
    )


# ---------------------------------------------------------------------------
# 3. Aggregate sanity — single, descriptive failure if any of the above
# would trip. This is mostly belt-and-braces for grep-friendly CI output.
# ---------------------------------------------------------------------------


def test_no_openapi_path_resembles_order_execution(client) -> None:
    """Aggregate: produce one consolidated failure listing every offender."""
    paths = _all_openapi_paths(client)
    aggregated: list[tuple[str, str]] = []
    for path in paths:
        parts = path.split("/")
        for seg in FORBIDDEN_SINGLE_SEGMENTS:
            if seg in parts:
                aggregated.append((path, seg))
        for pat in FORBIDDEN_COMPOUND_PATTERNS:
            if pat in path:
                aggregated.append((path, pat))
    assert not aggregated, (
        "OpenAPI schema contains paths resembling order execution / live "
        f"trading: {aggregated}"
    )
