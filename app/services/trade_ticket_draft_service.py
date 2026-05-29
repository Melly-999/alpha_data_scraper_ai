"""PDS-002 — Ticket Draft Service from Scanner Preview.

Converts scanner/manual setup data into a paper-only TradeTicketDraft and
validates it with TradeTicketValidator.

Constraints:
- No broker calls, network I/O, Supabase, MT5, or IBKR.
- No route imports, no side effects, no file writes, no environment reads.
- All output is advisory-only and paper-only.
- Safety fields are forced and cannot be overridden by callers.
- ticket_id is deterministic: same input always produces the same ID.
- risk_allowed and broker_execution_allowed are never flipped to True.
"""

from __future__ import annotations

import hashlib
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.schemas.trade_ticket import (
    EntryType,
    TradeSide,
    TradeTicketDraft,
)
from app.services.trade_ticket_validator import (
    TradeTicketValidationResult,
    TradeTicketValidator,
)

_VALIDATOR = TradeTicketValidator()

# Safety contract snapshot — never mutated at runtime.
_SAFETY_CONTRACT: dict[str, bool | str | float] = {
    "paper_only": True,
    "dry_run": True,
    "read_only": True,
    "live_orders_blocked": True,
    "requires_human_review": True,
    "risk_allowed": False,
    "broker_execution_allowed": False,
    "execution_mode": "paper_only_draft",
    "max_risk_pct": TradeTicketValidator.MAX_RISK_PCT,
}


class TradeTicketDraftInput(BaseModel):
    """Input data for creating a paper-only ticket draft.

    Represents the minimal set of fields a scanner preview or manual setup
    needs to provide.  Safety fields are NOT present here — the service
    forces them unconditionally.
    """

    model_config = ConfigDict(extra="forbid")

    # --- required trade intent ---
    symbol: str = Field(min_length=1, max_length=32)
    side: TradeSide
    entry_type: EntryType
    timeframe: str = Field(min_length=1, max_length=8)
    entry_price: float
    stop_loss: float
    take_profit_1: float
    risk_pct: float
    confidence: float
    reason: str = Field(min_length=1, max_length=1024)

    # --- optional ---
    take_profit_2: float | None = None
    setup_notes: str | None = None
    scanner_signal_id: str | None = None
    source: str = "scanner_preview"


class TradeTicketDraftResult(BaseModel):
    """Result returned by the draft service.

    Carries no execution intent.  No order_id, fill_id, execution_id,
    broker_order_id, account_id, credential, token, or secret fields.
    """

    model_config = ConfigDict(extra="forbid")

    draft: TradeTicketDraft | None = None
    validation: TradeTicketValidationResult | None = None
    accepted: bool
    rejection_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    safety_contract: dict[str, bool | str | float]


def _make_ticket_id(
    source: str,
    symbol: str,
    timeframe: str,
    side: str,
) -> str:
    """Return a deterministic ticket ID derived from the key input fields.

    Uses a 10-character SHA-256 prefix so the same logical setup always
    produces the same ID — no randomness, no timestamps.
    """
    raw = f"{source}:{symbol.upper()}:{timeframe}:{side}".encode()
    digest = hashlib.sha256(raw).hexdigest()[:10]
    return f"paper-{source}-{symbol.upper()}-{timeframe}-{side}-{digest}"


class TradeTicketDraftService:
    """Pure, deterministic service for creating paper-only ticket drafts."""

    def create(
        self, input_data: TradeTicketDraftInput | dict[str, Any]
    ) -> TradeTicketDraftResult:
        # --- normalise dict input ---
        if isinstance(input_data, dict):
            try:
                input_data = TradeTicketDraftInput(**input_data)
            except (ValidationError, TypeError) as exc:
                reasons = _flatten_validation_error(exc)
                return TradeTicketDraftResult(
                    accepted=False,
                    rejection_reasons=reasons,
                    safety_contract=dict(_SAFETY_CONTRACT),
                )

        # --- build deterministic ticket_id ---
        ticket_id = _make_ticket_id(
            source=input_data.source,
            symbol=input_data.symbol,
            timeframe=input_data.timeframe,
            side=input_data.side.value,
        )

        # --- attempt schema construction with forced safety fields ---
        try:
            draft = TradeTicketDraft(
                ticket_id=ticket_id,
                symbol=input_data.symbol,
                side=input_data.side,
                entry_type=input_data.entry_type,
                timeframe=input_data.timeframe,
                entry_price=input_data.entry_price,
                stop_loss=input_data.stop_loss,
                take_profit_1=input_data.take_profit_1,
                take_profit_2=input_data.take_profit_2,
                risk_pct=input_data.risk_pct,
                confidence=input_data.confidence,
                reason=input_data.reason,
                setup_notes=input_data.setup_notes,
                scanner_signal_id=input_data.scanner_signal_id,
                source=input_data.source,
                # safety fields — always forced, never from caller
                paper_only=True,
                dry_run=True,
                read_only=True,
                live_orders_blocked=True,
                requires_human_review=True,
                risk_allowed=False,
                broker_execution_allowed=False,
                execution_mode="paper_only_draft",
            )
        except ValidationError as exc:
            reasons = _flatten_validation_error(exc)
            return TradeTicketDraftResult(
                accepted=False,
                rejection_reasons=reasons,
                safety_contract=dict(_SAFETY_CONTRACT),
            )

        # --- validate ---
        validation = _VALIDATOR.validate(draft)

        return TradeTicketDraftResult(
            draft=draft,
            validation=validation,
            accepted=validation.accepted,
            rejection_reasons=list(validation.rejection_reasons),
            warnings=list(validation.warnings),
            safety_contract=dict(_SAFETY_CONTRACT),
        )


def _flatten_validation_error(exc: Exception) -> list[str]:
    """Extract human-readable rejection reasons without leaking internals."""
    if isinstance(exc, ValidationError):
        return [
            (
                f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
                if e.get("loc")
                else e["msg"]
            )
            for e in exc.errors()
        ]
    return [str(exc)]


def create_trade_ticket_draft(
    input_data: TradeTicketDraftInput | dict[str, Any],
) -> TradeTicketDraftResult:
    """Module-level convenience wrapper around TradeTicketDraftService."""
    return TradeTicketDraftService().create(input_data)
