"""PAPER-001 — In-memory paper broker sandbox service.

Provides a pure, side-effect-free in-memory store for paper-only ticket
submissions.  No broker calls, no network I/O, no MT5, no IBKR, no
Supabase, no file writes, no environment reads.

The sandbox accepts validated TradeTicketDraft objects, enforces all safety
flags, generates locally-scoped paper IDs, and stores entries in a process-
level dict.

No route is wired here.  Route integration is deferred to PAPER-003
("Paper-only execute endpoint behind human approval").

Safety invariants maintained at every point:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  broker_execution_allowed = False
  risk_allowed           = False
  execution_mode         = "dry_run_only"
  max_risk_pct           <= 1.0
"""

from __future__ import annotations

import hashlib
import threading
from datetime import datetime, timezone

from app.schemas.paper_sandbox import (
    PaperSandboxEntry,
    PaperSandboxState,
    PaperSandboxSubmitResult,
)
from app.schemas.trade_ticket import TradeTicketDraft

# ---------------------------------------------------------------------------
# Safety contract snapshot — never mutated at runtime.
# ---------------------------------------------------------------------------

_SAFETY_CONTRACT: dict[str, bool | str | float] = {
    "paper_only": True,
    "dry_run": True,
    "read_only": True,
    "live_orders_blocked": True,
    "requires_human_review": True,
    "risk_allowed": False,
    "broker_execution_allowed": False,
    "execution_mode": "dry_run_only",
    "max_risk_pct": 1.0,
}

_MAX_RISK_PCT: float = 1.0


# ---------------------------------------------------------------------------
# ID generation — deterministic, paper-scoped, not broker IDs
# ---------------------------------------------------------------------------


def _make_sandbox_entry_id(ticket_id: str) -> str:
    """Return a deterministic paper-scoped entry ID for the given ticket_id.

    Uses a 12-character SHA-256 prefix so the same ticket_id always maps to
    the same sandbox_entry_id.  This is NOT a broker order ID, fill ID, or
    execution ID of any kind.
    """
    digest = hashlib.sha256(ticket_id.encode()).hexdigest()[:12]
    return f"paper-sandbox-entry-{digest}"


# ---------------------------------------------------------------------------
# PaperBrokerSandbox
# ---------------------------------------------------------------------------


class PaperBrokerSandbox:
    """In-memory paper-only broker sandbox.

    Thread-safe via a reentrant lock.  State is process-local and lost on
    restart — it is intentionally ephemeral.  Meant for decision-support
    preview and testing; not for durable persistence.

    All submitted entries carry the full safety contract and are stamped
    with a UTC submission timestamp.
    """

    def __init__(self) -> None:
        # _store maps ticket_id → PaperSandboxEntry
        self._store: dict[str, PaperSandboxEntry] = {}
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit(self, draft: TradeTicketDraft) -> PaperSandboxSubmitResult:
        """Submit a validated TradeTicketDraft to the sandbox.

        Safety checks are enforced even though the schema's Literal fields
        already guarantee them — the belt-and-suspenders check ensures that
        any future schema weakening would still be caught at runtime.

        Returns PaperSandboxSubmitResult with accepted=True and the stored
        PaperSandboxEntry on success, or accepted=False with rejection_reasons
        on failure.  The safety_contract is always present in the result.

        This method never calls any broker, network service, or database.
        """
        rejection_reasons: list[str] = []

        # --- safety contract hard checks ---
        if not draft.paper_only:
            rejection_reasons.append("paper_only must be True")
        if not draft.dry_run:
            rejection_reasons.append("dry_run must be True")
        if not draft.read_only:
            rejection_reasons.append("read_only must be True")
        if not draft.live_orders_blocked:
            rejection_reasons.append("live_orders_blocked must be True")
        if not draft.requires_human_review:
            rejection_reasons.append("requires_human_review must be True")
        if draft.broker_execution_allowed:
            rejection_reasons.append("broker_execution_allowed must be False")
        if draft.risk_allowed:
            rejection_reasons.append("risk_allowed must be False")

        # --- risk ceiling ---
        if draft.risk_pct > _MAX_RISK_PCT:
            rejection_reasons.append(
                f"risk_pct {draft.risk_pct} exceeds maximum {_MAX_RISK_PCT}"
            )

        if rejection_reasons:
            return PaperSandboxSubmitResult(
                accepted=False,
                rejection_reasons=rejection_reasons,
                safety_contract=dict(_SAFETY_CONTRACT),
            )

        # --- build paper-scoped entry ---
        sandbox_entry_id = _make_sandbox_entry_id(draft.ticket_id)
        submitted_at = datetime.now(timezone.utc).isoformat()

        entry = PaperSandboxEntry(
            sandbox_entry_id=sandbox_entry_id,
            ticket_id=draft.ticket_id,
            symbol=draft.symbol,
            side=draft.side,
            entry_type=draft.entry_type,
            timeframe=draft.timeframe,
            entry_price=draft.entry_price,
            stop_loss=draft.stop_loss,
            take_profit_1=draft.take_profit_1,
            take_profit_2=draft.take_profit_2,
            risk_pct=draft.risk_pct,
            confidence=draft.confidence,
            reason=draft.reason,
            source=draft.source,
            submitted_at=submitted_at,
        )

        with self._lock:
            self._store[draft.ticket_id] = entry

        return PaperSandboxSubmitResult(
            accepted=True,
            entry=entry,
            safety_contract=dict(_SAFETY_CONTRACT),
        )

    def get_entry(self, ticket_id: str) -> PaperSandboxEntry | None:
        """Return the stored entry for the given ticket_id, or None."""
        with self._lock:
            return self._store.get(ticket_id)

    def list_entries(self) -> list[PaperSandboxEntry]:
        """Return an immutable snapshot of all stored entries."""
        with self._lock:
            return list(self._store.values())

    def get_state(self) -> PaperSandboxState:
        """Return a read-only snapshot of the full sandbox state."""
        with self._lock:
            entries = list(self._store.values())
        return PaperSandboxState(entries=entries, count=len(entries))

    def reset(self) -> None:
        """Clear all in-memory entries.  For testing only."""
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)


# ---------------------------------------------------------------------------
# Module-level singleton and convenience functions
# ---------------------------------------------------------------------------

_sandbox: PaperBrokerSandbox = PaperBrokerSandbox()


def get_paper_sandbox() -> PaperBrokerSandbox:
    """Return the module-level PaperBrokerSandbox singleton."""
    return _sandbox


def submit_to_paper_sandbox(
    draft: TradeTicketDraft,
) -> PaperSandboxSubmitResult:
    """Module-level convenience wrapper: submit a draft to the singleton sandbox."""
    return _sandbox.submit(draft)
