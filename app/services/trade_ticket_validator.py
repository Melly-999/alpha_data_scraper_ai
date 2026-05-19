"""PDS-001 — Pure, deterministic trade-ticket validator.

No broker calls, no network I/O, no Supabase, no MT5, no IBKR.
Input: TradeTicketDraft  →  Output: TradeTicketValidationResult

The validator enforces the same safety contract as the schema and adds
runtime checks that the schema alone cannot express (e.g. duplicate or
contradictory field combinations).  It never sets risk_allowed=True or
broker_execution_allowed=True, and it never returns anything that implies
live order execution.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, SkipValidation

from app.schemas.trade_ticket import (
    RiskValidationStatus,
    TradeSide,
    TradeTicketDraft,
)


class TradeTicketValidationResult(BaseModel):
    """Result of a pure, side-effect-free ticket validation pass."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool
    status: RiskValidationStatus
    rejection_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    normalized_ticket: SkipValidation[TradeTicketDraft]
    safety_contract: dict[str, bool | str | float]


class TradeTicketValidator:
    """Deterministic, side-effect-free validator for paper-only tickets."""

    MAX_RISK_PCT: float = 1.0
    MIN_CONFIDENCE_WARN: float = 70.0

    def validate(
        self, ticket: TradeTicketDraft
    ) -> TradeTicketValidationResult:
        rejection_reasons: list[str] = []
        warnings: list[str] = []

        # --- safety contract hard checks ---
        if not ticket.paper_only:
            rejection_reasons.append("paper_only must be True")
        if not ticket.dry_run:
            rejection_reasons.append("dry_run must be True")
        if not ticket.read_only:
            rejection_reasons.append("read_only must be True")
        if not ticket.live_orders_blocked:
            rejection_reasons.append("live_orders_blocked must be True")
        if not ticket.requires_human_review:
            rejection_reasons.append("requires_human_review must be True")
        if ticket.broker_execution_allowed:
            rejection_reasons.append(
                "broker_execution_allowed must be False"
            )

        # --- risk percentage ---
        if ticket.risk_pct > self.MAX_RISK_PCT:
            rejection_reasons.append(
                f"risk_pct {ticket.risk_pct} exceeds maximum {self.MAX_RISK_PCT}"
            )

        # --- price validity (entry/SL/TP must be positive) ---
        if ticket.entry_price <= 0:
            rejection_reasons.append("entry_price must be > 0")
        if ticket.stop_loss <= 0:
            rejection_reasons.append("stop_loss must be > 0")
        if ticket.take_profit_1 <= 0:
            rejection_reasons.append("take_profit_1 must be > 0")
        if ticket.take_profit_2 is not None and ticket.take_profit_2 <= 0:
            rejection_reasons.append("take_profit_2 must be > 0 when provided")

        # --- price geometry ---
        self._check_geometry(ticket, rejection_reasons)

        # --- confidence ---
        if not (0 <= ticket.confidence <= 100):
            rejection_reasons.append(
                f"confidence {ticket.confidence} must be in [0, 100]"
            )

        # --- warnings ---
        if ticket.confidence < self.MIN_CONFIDENCE_WARN:
            warnings.append(
                f"confidence {ticket.confidence} is below recommended "
                f"threshold of {self.MIN_CONFIDENCE_WARN}"
            )
        if ticket.take_profit_2 is None:
            warnings.append(
                "take_profit_2 is not set; consider adding a second target"
            )

        accepted = len(rejection_reasons) == 0

        # Build safety contract snapshot — never flips risk_allowed or
        # broker_execution_allowed to True.
        safety_contract: dict[str, bool | str | float] = {
            "paper_only": True,
            "dry_run": True,
            "read_only": True,
            "live_orders_blocked": True,
            "requires_human_review": True,
            "risk_allowed": False,
            "broker_execution_allowed": False,
            "execution_mode": "paper_only_draft",
            "max_risk_pct": self.MAX_RISK_PCT,
        }

        status = (
            RiskValidationStatus.passed
            if accepted
            else RiskValidationStatus.failed
        )

        return TradeTicketValidationResult(
            accepted=accepted,
            status=status,
            rejection_reasons=rejection_reasons,
            warnings=warnings,
            normalized_ticket=ticket,
            safety_contract=safety_contract,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_geometry(
        self,
        ticket: TradeTicketDraft,
        rejection_reasons: list[str],
    ) -> bool:
        entry = ticket.entry_price
        sl = ticket.stop_loss
        tp1 = ticket.take_profit_1
        tp2 = ticket.take_profit_2
        side = ticket.side
        ok = True

        if side == TradeSide.long:
            if sl >= entry:
                rejection_reasons.append(
                    "long setup: stop_loss must be below entry_price"
                )
                ok = False
            if tp1 <= entry:
                rejection_reasons.append(
                    "long setup: take_profit_1 must be above entry_price"
                )
                ok = False
            if tp2 is not None and tp2 <= entry:
                rejection_reasons.append(
                    "long setup: take_profit_2 must be above entry_price"
                )
                ok = False
        else:  # short
            if sl <= entry:
                rejection_reasons.append(
                    "short setup: stop_loss must be above entry_price"
                )
                ok = False
            if tp1 >= entry:
                rejection_reasons.append(
                    "short setup: take_profit_1 must be below entry_price"
                )
                ok = False
            if tp2 is not None and tp2 >= entry:
                rejection_reasons.append(
                    "short setup: take_profit_2 must be below entry_price"
                )
                ok = False

        return ok


def validate_trade_ticket(
    ticket: TradeTicketDraft,
) -> TradeTicketValidationResult:
    """Module-level convenience wrapper around TradeTicketValidator."""
    return TradeTicketValidator().validate(ticket)
