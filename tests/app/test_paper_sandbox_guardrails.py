"""PAPER-GUARD-001 — Paper sandbox safety guardrail tests.

Protects future paper-only sandbox work from accidentally introducing live
execution surfaces.  All assertions target the OpenAPI schema only; they do
not depend on the order of routes or on any paper endpoint already existing.

Safety contract enforced by this file:
  - No live execution / broker / order-placement routes outside /api/paper
    or /paper namespace.
  - Any future /api/paper or /paper endpoint must be clearly paper-only.
  - No non-GET routes on trading/execution/broker/order paths outside the
    paper namespace.
  - No autotrade-enable route exists.
  - autotrade.enabled=false, dry_run=true, read_only=true,
    live_orders_blocked=true, max_risk<=1%.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PAPER_PREFIXES = ("/api/paper", "/paper")

# Path fragments that imply live broker execution when they appear outside
# the paper namespace.  Compared by substring against the lowercased path.
LIVE_EXECUTION_FRAGMENTS: tuple[str, ...] = (
    "/orders",
    "/order",
    "/execute",
    "/execution",
    "/trade",
    "/trades",
    "/broker/execute",
    "/broker/order",
    "/mt5/order",
    "/ibkr/order",
    "/live",
    "/autotrade",
)

# Wording that must NOT appear in paper-endpoint metadata unless it is
# explicitly in a negative/safety context.
LIVE_WORDING: tuple[str, ...] = (
    "live broker",
    "real broker",
    "mt5 execution",
    "ibkr execution",
    "live order",
    "place live",
    "submit live",
)

# Wording indicating a path is explicitly paper/sandbox-safe.
PAPER_INDICATORS: tuple[str, ...] = (
    "paper",
    "sandbox",
    "dry_run",
    "simulated",
)

# HTTP methods that could mutate state.
MUTATING_METHODS: frozenset[str] = frozenset({"post", "put", "patch", "delete"})

# Path substrings that — when combined with a mutating method and appearing
# outside the paper namespace — are forbidden.
MUTATING_TRADING_FRAGMENTS: tuple[str, ...] = (
    "/order",
    "/orders",
    "/execute",
    "/execution",
    "/trade",
    "/trades",
    "/broker",
    "/mt5",
    "/ibkr",
)

# Pre-existing, reviewed admin/dry-run routes that contain a trading-adjacent
# path fragment but are NOT live execution surfaces.  Mirrored from
# ADMIN_NON_GET_ALLOWLIST in test_safety_invariants.py.
SAFE_ADMIN_NON_EXECUTION_PATHS: frozenset[str] = frozenset(
    {
        "/api/broker/dry-run-report",  # dry-run only, no live broker calls
    }
)


def _openapi_paths(client) -> dict:
    """Return the ``paths`` dict from the live OpenAPI schema."""
    schema = client.app.openapi()
    return schema.get("paths") or {}


def _is_paper_path(path: str) -> bool:
    """Return True if ``path`` lives inside the paper namespace."""
    lower = path.lower()
    return any(lower.startswith(prefix) for prefix in PAPER_PREFIXES)


def _path_metadata_text(path_item: dict) -> str:
    """Collect all summary/description/operationId strings for a path item."""
    texts: list[str] = []
    for method_obj in path_item.values():
        if not isinstance(method_obj, dict):
            continue
        for field in ("summary", "description", "operationId"):
            val = method_obj.get(field, "")
            if val:
                texts.append(str(val).lower())
    return " ".join(texts)


# ---------------------------------------------------------------------------
# 1. OpenAPI schema is readable
# ---------------------------------------------------------------------------


def test_openapi_schema_is_readable(client) -> None:
    """The schema must be non-empty — guards against vacuous passes."""
    paths = _openapi_paths(client)
    assert (
        paths
    ), "OpenAPI schema returned no paths; guardrail tests would pass vacuously"


# ---------------------------------------------------------------------------
# 2. No live execution route exists outside the paper namespace
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fragment", LIVE_EXECUTION_FRAGMENTS)
def test_no_live_execution_route_outside_paper_namespace(client, fragment: str) -> None:
    """No path containing ``fragment`` should exist outside /api/paper or /paper."""
    paths = _openapi_paths(client)
    offenders: list[str] = []

    for path in paths:
        lower = path.lower()
        if fragment in lower and not _is_paper_path(path):
            # Allow the path ONLY if it is purely read-only (no mutating
            # methods) AND its metadata does not imply order execution.
            path_item = paths[path]
            methods_present = {m for m in path_item if m in MUTATING_METHODS}
            metadata = _path_metadata_text(path_item)
            has_execution_wording = any(w in metadata for w in LIVE_WORDING)

            if methods_present or has_execution_wording:
                offenders.append(
                    f"{path!r} (methods={methods_present or 'none'}, "
                    f"wording={'yes' if has_execution_wording else 'no'})"
                )

    assert not offenders, (
        f"Live execution fragment {fragment!r} found outside paper namespace "
        f"with mutating methods or execution wording:\n"
        + "\n".join(f"  {o}" for o in offenders)
    )


# ---------------------------------------------------------------------------
# 3. Future /api/paper or /paper endpoints must be paper-only
# ---------------------------------------------------------------------------


def test_paper_namespace_endpoints_are_paper_only(client) -> None:
    """Any path under /api/paper or /paper must signal paper/sandbox intent."""
    paths = _openapi_paths(client)
    offenders: list[str] = []

    for path, path_item in paths.items():
        if not _is_paper_path(path):
            continue

        metadata = _path_metadata_text(path_item)

        # Must contain at least one paper indicator
        has_paper_indicator = any(ind in metadata for ind in PAPER_INDICATORS)
        # Must not contain live-broker wording
        has_live_wording = any(w in metadata for w in LIVE_WORDING)

        if not has_paper_indicator or has_live_wording:
            offenders.append(
                f"{path!r} (paper_indicator={'yes' if has_paper_indicator else 'MISSING'}, "
                f"live_wording={'PRESENT' if has_live_wording else 'none'})"
            )

    assert not offenders, (
        "Paper-namespace endpoint(s) missing paper/sandbox indicator or "
        "containing live-broker wording:\n" + "\n".join(f"  {o}" for o in offenders)
    )


def test_paper_namespace_passes_vacuously_if_no_paper_endpoints_exist(
    client,
) -> None:
    """Guard 3 is explicitly designed to pass when no paper endpoints exist yet."""
    paths = _openapi_paths(client)
    paper_paths = [p for p in paths if _is_paper_path(p)]
    # This is informational: assert nothing fails regardless of whether
    # paper endpoints exist.
    assert isinstance(paper_paths, list)  # always true — structural assertion


# ---------------------------------------------------------------------------
# 4. No mutating method on trading/broker/execution paths outside paper namespace
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fragment", MUTATING_TRADING_FRAGMENTS)
def test_no_mutating_method_on_trading_path_outside_paper_namespace(
    client, fragment: str
) -> None:
    """POST/PUT/PATCH/DELETE on trading/broker/order-shaped paths must be in paper ns."""
    paths = _openapi_paths(client)
    offenders: list[str] = []

    for path, path_item in paths.items():
        if _is_paper_path(path):
            continue  # paper namespace is allowed
        if path in SAFE_ADMIN_NON_EXECUTION_PATHS:
            continue  # reviewed admin/dry-run routes — not live execution
        lower = path.lower()
        if fragment not in lower:
            continue
        bad_methods = {m for m in path_item if m in MUTATING_METHODS}
        if bad_methods:
            offenders.append(f"{path!r} (methods: {sorted(bad_methods)})")

    assert not offenders, (
        f"Mutating method(s) found on trading-shaped path(s) with "
        f"fragment {fragment!r} outside paper namespace:\n"
        + "\n".join(f"  {o}" for o in offenders)
    )


# ---------------------------------------------------------------------------
# 5. No autotrade-enable route exists
# ---------------------------------------------------------------------------


def test_no_autotrade_enable_route_in_openapi(client) -> None:
    """The OpenAPI schema must contain no autotrade-enable route."""
    paths = _openapi_paths(client)
    offenders: list[str] = []

    for path, path_item in paths.items():
        lower = path.lower()
        if "autotrade" not in lower:
            continue
        bad_methods = {m for m in path_item if m in MUTATING_METHODS}
        if bad_methods:
            offenders.append(f"{path!r} (methods: {sorted(bad_methods)})")

    assert (
        not offenders
    ), "Autotrade-enable route found in OpenAPI schema:\n" + "\n".join(
        f"  {o}" for o in offenders
    )


def test_no_autotrade_enable_in_metadata(client) -> None:
    """No OpenAPI path metadata should imply enabling autotrade."""
    paths = _openapi_paths(client)
    enable_patterns = (
        "enable autotrade",
        "enable auto trade",
        "autotrade enable",
        "start autotrade",
        "autotrade=true",
        "autotrade = true",
    )
    offenders: list[str] = []

    for path, path_item in paths.items():
        metadata = _path_metadata_text(path_item)
        for pattern in enable_patterns:
            if pattern in metadata:
                offenders.append(f"{path!r} contains {pattern!r}")

    assert (
        not offenders
    ), "OpenAPI path metadata implies autotrade enablement:\n" + "\n".join(
        f"  {o}" for o in offenders
    )


# ---------------------------------------------------------------------------
# 6. Safety config invariants (belt-and-braces alongside validate_safety_config.py)
# ---------------------------------------------------------------------------


def test_config_json_autotrade_disabled() -> None:
    """config.json must have autotrade.enabled=false."""
    config = json.loads((REPO_ROOT / "config.json").read_text(encoding="utf-8"))
    autotrade = config.get("autotrade", {})
    assert autotrade.get("enabled") is False, (
        "config.json autotrade.enabled must be false; "
        f"got {autotrade.get('enabled')!r}"
    )


def test_config_json_dry_run_true() -> None:
    """config.json must have autotrade.dry_run=true."""
    config = json.loads((REPO_ROOT / "config.json").read_text(encoding="utf-8"))
    autotrade = config.get("autotrade", {})
    assert autotrade.get("dry_run") is True, (
        f"config.json autotrade.dry_run must be true; "
        f"got {autotrade.get('dry_run')!r}"
    )


# ---------------------------------------------------------------------------
# 7. Paper schema safety fields cannot be weakened
# ---------------------------------------------------------------------------


def test_paper_ticket_schema_safety_fields_cannot_be_overridden() -> None:
    """TradeTicketDraft safety fields must remain Literal-typed constants."""
    from pydantic import ValidationError

    from app.schemas.trade_ticket import TradeTicketDraft

    base = dict(
        ticket_id="GUARD-001",
        symbol="EURUSD",
        side="long",
        entry_type="manual",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        risk_pct=0.5,
        confidence=80.0,
        reason="Guardrail safety field test",
    )

    for field, bad_value in [
        ("paper_only", False),
        ("dry_run", False),
        ("read_only", False),
        ("live_orders_blocked", False),
        ("requires_human_review", False),
        ("broker_execution_allowed", True),
    ]:
        with pytest.raises(ValidationError):
            TradeTicketDraft(**{**base, field: bad_value})


def test_paper_validator_never_flips_risk_allowed() -> None:
    """TradeTicketValidator must never set risk_allowed=True."""
    from app.schemas.trade_ticket import TradeTicketDraft
    from app.services.trade_ticket_validator import TradeTicketValidator

    ticket = TradeTicketDraft(
        ticket_id="GUARD-002",
        symbol="EURUSD",
        side="long",
        entry_type="manual",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        risk_pct=0.5,
        confidence=80.0,
        reason="Validator risk_allowed guardrail",
    )
    result = TradeTicketValidator().validate(ticket)
    assert (
        result.safety_contract["risk_allowed"] is False
    ), "Validator safety_contract must never set risk_allowed=True"
    assert (
        result.safety_contract["broker_execution_allowed"] is False
    ), "Validator safety_contract must never set broker_execution_allowed=True"


def test_draft_service_never_flips_safety_fields() -> None:
    """TradeTicketDraftService must always force all safety fields correctly."""
    from app.services.trade_ticket_draft_service import TradeTicketDraftService

    svc = TradeTicketDraftService()
    result = svc.create(
        dict(
            symbol="EURUSD",
            side="long",
            entry_type="manual",
            timeframe="H1",
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit_1=1.1100,
            risk_pct=0.5,
            confidence=80.0,
            reason="Draft service safety guardrail",
        )
    )
    assert result.accepted is True
    assert result.draft is not None
    draft = result.draft
    assert draft.paper_only is True
    assert draft.dry_run is True
    assert draft.read_only is True
    assert draft.live_orders_blocked is True
    assert draft.requires_human_review is True
    assert draft.risk_allowed is False
    assert draft.broker_execution_allowed is False
    assert draft.execution_mode == "paper_only_draft"
    sc = result.safety_contract
    assert sc["paper_only"] is True
    assert sc["risk_allowed"] is False
    assert sc["broker_execution_allowed"] is False
    assert sc["max_risk_pct"] == 1.0


# ---------------------------------------------------------------------------
# 8. No live execution fields in paper schema surface
# ---------------------------------------------------------------------------


def test_paper_ticket_draft_has_no_live_execution_fields() -> None:
    """TradeTicketDraft model_fields must not contain live execution field names."""
    from app.schemas.trade_ticket import TradeTicketDraft

    forbidden_fields = {
        "order_id",
        "fill_id",
        "execution_id",
        "broker_order_id",
        "account_id",
        "credential",
        "token",
        "secret",
        "live_execute",
        "broker_execute",
    }
    model_fields = set(TradeTicketDraft.model_fields.keys())
    overlap = forbidden_fields & model_fields
    assert (
        not overlap
    ), f"TradeTicketDraft must not contain live execution fields: {overlap}"


def test_paper_ticket_draft_result_has_no_live_execution_fields() -> None:
    """TradeTicketDraftResult model_fields must not contain live execution fields."""
    from app.services.trade_ticket_draft_service import TradeTicketDraftResult

    forbidden_fields = {
        "order_id",
        "fill_id",
        "execution_id",
        "broker_order_id",
        "account_id",
        "credential",
        "token",
        "secret",
    }
    model_fields = set(TradeTicketDraftResult.model_fields.keys())
    overlap = forbidden_fields & model_fields
    assert (
        not overlap
    ), f"TradeTicketDraftResult must not contain live execution fields: {overlap}"
