from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.signal import SignalDetail, SignalReasoning, SignalSummary
from app.schemas.signal_scanner import (
    SignalScannerBatch,
    SignalUniverseListResponse,
    SignalUniversePreset,
)
from app.schemas.signal_decision import (
    DecisionDirection,
    DecisionType,
    RiskStatus,
    SignalDecisionHistoryResponse,
)
from app.schemas.signal_lifecycle import (
    LifecycleDecision,
    LifecycleRiskStatus,
    SignalLifecycleResponse,
)
from app.schemas.signal_quality import SignalQualitySummaryResponse
from app.services.signal_decision_history_service import SignalDecisionHistoryService
from app.services.signal_lifecycle_service import SignalLifecycleService
from app.services.signal_quality_summary import SignalQualitySummaryService

router = APIRouter(tags=["signals"])

_decision_service = SignalDecisionHistoryService()
_lifecycle_service = SignalLifecycleService(_decision_service)
_quality_summary_service = SignalQualitySummaryService()
_scanner_default_symbols = ("AAPL", "NVDA", "MSFT", "TSLA", "EURUSD", "XAUUSD")
_scanner_max_symbols = 25

# Human-readable display labels for each universe name.
# Unknown names are formatted by replacing underscores with spaces and title-casing.
_UNIVERSE_LABELS: dict[str, str] = {
    "ai_mega_caps": "AI Mega Caps",
    "xtb_cfd_watchlist": "XTB / CFD Watchlist",
    "core_macro": "Core Macro",
    "polish_eu_watchlist": "Polish / EU Watchlist",
    "default_demo": "Default Demo",
}


def _universe_label(name: str) -> str:
    """Return a display label for a universe name."""
    return _UNIVERSE_LABELS.get(name, name.replace("_", " ").title())


def _resolve_scanner_symbols(
    raw_symbols: str | None,
    universe: str | None,
) -> list[str]:
    """Resolve which symbols to scan.

    Priority:
    1. Explicit ``symbols`` query param — always takes precedence.
    2. ``universe`` query param — resolved via signal_universe service;
       unknown names safely fall back to ``default_demo``.
    3. Default symbols tuple — used when neither is provided.

    No broker calls, no network calls, no persistence.
    """
    if raw_symbols is not None and raw_symbols.strip():
        return _parse_scanner_symbols(raw_symbols)
    if universe is not None and universe.strip():
        from app.services.signal_universe import list_symbols_for_universe

        universe_symbols = list_symbols_for_universe(universe.strip())
        return list(universe_symbols) or list(_scanner_default_symbols)
    return list(_scanner_default_symbols)


def _parse_scanner_symbols(raw_symbols: str | None) -> list[str]:
    if raw_symbols is None or not raw_symbols.strip():
        return list(_scanner_default_symbols)

    cleaned: list[str] = []
    seen: set[str] = set()
    for symbol in raw_symbols.split(","):
        normalized = symbol.strip()
        if not normalized:
            continue
        normalized_key = normalized.upper()
        if normalized_key in seen:
            continue
        seen.add(normalized_key)
        cleaned.append(normalized)
        if len(cleaned) >= _scanner_max_symbols:
            break
    return cleaned or list(_scanner_default_symbols)


def _action_to_direction(action: str) -> str:
    """Map a SignalAction string to a DecisionDirection string.

    LONG_SETUP → BUY, SHORT_SETUP → SELL, all others → HOLD.
    Read-only mapping — no execution semantics.
    """
    if action == "LONG_SETUP":
        return "BUY"
    if action == "SHORT_SETUP":
        return "SELL"
    return "HOLD"


@router.get(
    "/signals/scanner/universes",
    response_model=SignalUniverseListResponse,
)
def signal_scanner_universes() -> SignalUniverseListResponse:
    """Read-only universe preset list.

    Advisory-only GET endpoint that returns all available scanner universe
    presets defined in SIG-UNIVERSE-001.  No execution, no broker call,
    no mutation, no persistence.
    """
    from app.services.signal_universe import list_universes

    universe_map = list_universes()
    presets: list[SignalUniversePreset] = []

    for name, items in universe_map.items():
        symbols = [item.symbol for item in items if item.symbol]
        asset_classes = sorted({item.asset_class for item in items if item.asset_class})
        tags: set[str] = set()
        for item in items:
            tags.update(item.tags)
        presets.append(
            SignalUniversePreset(
                name=name,
                label=_universe_label(name),
                symbols=symbols,
                item_count=len(symbols),
                asset_classes=asset_classes,
                tags=sorted(tags),
            )
        )

    return SignalUniverseListResponse(universes=presets)


@router.get(
    "/signals/scanner/preview",
    response_model=SignalScannerBatch,
)
def signal_scanner_preview(
    symbols: str | None = Query(
        default=None,
        description=(
            "Optional comma-separated preview symbols. Read-only scanner preview "
            "only; no execution, broker call, or persistence."
        ),
    ),
    universe: str | None = Query(
        default=None,
        description=(
            "Optional universe preset name (e.g. 'ai_mega_caps', 'xtb_cfd_watchlist'). "
            "Ignored when symbols are explicitly provided.  Unknown names fall back to "
            "default_demo.  Read-only; no execution, broker call, or persistence."
        ),
    ),
) -> SignalScannerBatch:
    """Read-only scanner preview.

    Advisory-only GET endpoint exposing the SIG-001 scanner foundation.
    No execution, no broker call, no mutation.
    SUPA-008: audit event is emitted after the batch is assembled;
    audit persistence failure never blocks the preview response.
    SUPA-011: each scanner result is persisted as a dry-run decision record;
    persistence failure never blocks the preview response.
    """
    from app.schemas.signal_decision import SignalDecisionRecord
    from app.services.scanner_audit import emit_scanner_preview_event
    from app.services.signal_decision_persistence import write_signal_decision
    from app.services.signal_scanner import scan_symbols
    from app.services.supabase_client import get_safe_supabase_write_client

    batch = scan_symbols(_resolve_scanner_symbols(symbols, universe))

    # SUPA-011: fire-and-forget persist each scanner result as a decision record.
    # The preview response is never blocked by persistence failure.
    # Only safe bounded fields are persisted (no prices, IDs, secrets, or
    # execution semantics).  decision=watch_only; order_placed=False always.
    for result in batch.results:
        try:
            decision_record = SignalDecisionRecord(
                id=f"scan-{result.symbol}-{result.timestamp.strftime('%Y%m%dT%H%M%S%f')}",
                timestamp=result.timestamp,
                symbol=result.symbol,
                direction=_action_to_direction(result.action.value),  # type: ignore[arg-type]
                confidence=result.confidence / 100.0,
                source="scanner",
                strategy="scanner",
                risk_status="blocked",  # risk_allowed=False always for scanner
                decision="watch_only",  # scanner is advisory only; never executes
                blocked_reason=None,
                dry_run=True,
                auto_trade=False,
                read_only=True,
                stop_loss_required=True,
                take_profit_required=True,
                max_risk_per_trade=0.01,
            )
            write_signal_decision(
                decision_record, client=get_safe_supabase_write_client()
            )
        except Exception:  # noqa: BLE001
            pass

    # SUPA-008: fire-and-forget audit event — degrades gracefully.
    # The preview response is never blocked by audit persistence failure.
    try:
        emit_scanner_preview_event(batch, client=get_safe_supabase_write_client())
    except Exception:  # noqa: BLE001
        pass

    return batch


@router.get("/signals", response_model=list[SignalSummary])
def list_signals(
    container: AppContainer = Depends(get_container),
) -> list[SignalSummary]:
    return container.signal_service.list_signals()


@router.get("/signals/decisions", response_model=SignalDecisionHistoryResponse)
def signal_decisions(
    limit: int = Query(default=50, ge=1, le=200),
    symbol: str | None = Query(default=None),
    decision: DecisionType | None = Query(default=None),
    risk_status: RiskStatus | None = Query(default=None),
    direction: DecisionDirection | None = Query(default=None),
    from_date: datetime | None = Query(
        default=None,
        description=(
            "Optional inclusive lower bound for created_at (ISO 8601 / UTC). "
            "Read-only filter; no mutation or execution semantics."
        ),
    ),
    to_date: datetime | None = Query(
        default=None,
        description=(
            "Optional inclusive upper bound for created_at (ISO 8601 / UTC). "
            "Read-only filter; no mutation or execution semantics."
        ),
    ),
) -> SignalDecisionHistoryResponse:
    """Read-only signal decision history.

    Returns a log of dry-run signal decisions showing what happened to each
    signal: blocked, watch-only, or dry-run-allowed. GET-only. No mutation,
    no order placement, no broker connection.
    SUPA-010: audit event is emitted after the response is assembled;
    audit persistence failure never blocks the decisions response.
    SUPA-014: optional ``from_date`` / ``to_date`` bound created_at server-side.
    """
    from app.services.signal_decision_audit import emit_signal_decision_event
    from app.services.supabase_client import get_safe_supabase_write_client

    response = _decision_service.list_decisions(
        limit=limit,
        symbol=symbol,
        decision=decision,
        risk_status=risk_status,
        direction=direction,
        from_date=from_date,
        to_date=to_date,
    )

    # SUPA-010: fire-and-forget audit event — degrades gracefully.
    # The decisions response is never blocked by audit persistence failure.
    try:
        emit_signal_decision_event(
            len(response.decisions),
            symbol,
            client=get_safe_supabase_write_client(),
        )
    except Exception:  # noqa: BLE001
        pass

    return response


@router.get("/signals/lifecycle", response_model=SignalLifecycleResponse)
def signal_lifecycle(
    limit: int = Query(default=50, ge=1, le=200),
    symbol: str | None = Query(default=None),
    decision: LifecycleDecision | None = Query(default=None),
    risk_status: LifecycleRiskStatus | None = Query(default=None),
) -> SignalLifecycleResponse:
    """Read-only signal lifecycle view.

    Explains the path from signal receipt through confidence, risk, broker
    safety, dry-run decision, and audit correlation. GET-only. No mutation,
    no broker connection, no MT5 execution, and no order placement.
    """
    return _lifecycle_service.list_lifecycle(
        limit=limit,
        symbol=symbol,
        decision=decision,
        risk_status=risk_status,
    )


@router.get(
    "/signals/quality/summary",
    response_model=SignalQualitySummaryResponse,
)
def signal_quality_summary() -> SignalQualitySummaryResponse:
    """Read-only advisory signal quality summary.

    Aggregates scanner results into a quality snapshot for the Terminal V1
    dashboard.  Advisory only — no execution, no broker call, no mutation,
    no persistence.  All safety fields are Literal-typed and cannot be
    weakened by callers.
    """
    return _quality_summary_service.get_summary()


@router.get("/signals/{signal_id}", response_model=SignalDetail)
def signal_detail(
    signal_id: str,
    container: AppContainer = Depends(get_container),
) -> SignalDetail:
    try:
        return container.signal_service.get_signal_detail(signal_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Signal not found") from exc


@router.get("/signals/{signal_id}/reasoning", response_model=SignalReasoning)
def signal_reasoning(
    signal_id: str,
    container: AppContainer = Depends(get_container),
) -> SignalReasoning:
    try:
        return container.signal_service.get_reasoning(signal_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Signal not found") from exc
