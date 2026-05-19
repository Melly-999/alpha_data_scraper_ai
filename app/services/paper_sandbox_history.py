"""PAPER-002A — In-memory paper sandbox activity/audit history service.

Provides a pure, side-effect-free in-memory store for paper sandbox
audit/activity events.  No broker calls, no network I/O, no broker APIs,
no database connections, no file writes, no environment reads.

Events are stored in a bounded deque (max 250).  Each event carries a
locally-generated sequential ID (paper_audit_000001, paper_audit_000002, …)
that is NOT a broker order ID, fill ID, execution ID, or account ID.

Event metadata is sanitized before storage: forbidden keys (account_id,
order_id, execution_id, broker IDs, credentials, tokens, secrets) are
silently dropped.  Non-finite numeric values are dropped.  String values are
truncated.  Total metadata keys are capped.

No route is wired here.  Route integration is deferred to PAPER-002B.
Frontend panel is deferred to PAPER-002C.
Service integration with paper_sandbox.py is deferred to PAPER-002B to
avoid premature coupling.

Safety invariants maintained at every point:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  broker_execution_allowed = False
  risk_allowed           = False
  execution_mode         = "dry_run_only"
"""

from __future__ import annotations

import math
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any

from app.schemas.paper_sandbox_history import (
    PaperAuditEvent,
    PaperAuditHistory,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MAX_HISTORY: int = 250
_MAX_META_KEYS: int = 16
_MAX_META_VALUE_STR_LEN: int = 256
_MAX_SOURCE_LEN: int = 128
_MAX_MESSAGE_LEN: int = 512

# Forbidden metadata keys — dropped silently during sanitization.
# This set mirrors the forbidden-field list in the schema docstring and the
# safety contract document.
_FORBIDDEN_META_KEYS: frozenset[str] = frozenset({
    "account_id",
    "broker_account_id",
    "order_id",
    "execution_id",
    "trade_id",
    "broker_order_id",
    "ibkr_order_id",
    "mt5_ticket",
    "credential",
    "secret",
    "token",
    "api_key",
    "password",
})

# Valid event type set — mirrors the Literal in PaperAuditEvent.
_VALID_EVENT_TYPES: frozenset[str] = frozenset({
    "sandbox_preview_requested",
    "sandbox_state_created",
    "sandbox_state_reset",
    "ticket_draft_observed",
    "safety_flags_checked",
    "human_review_required",
    "degraded_fallback_used",
    "unknown_paper_event",
})

_VALID_SEVERITIES: frozenset[str] = frozenset({"info", "warning", "blocked"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize_event_type(raw: str) -> str:
    """Normalize and validate an event type string.

    Strips whitespace, lowercases, replaces hyphens and spaces with
    underscores.  Returns ``"unknown_paper_event"`` if the result is not
    in the allowed set.
    """
    normalized = raw.strip().lower().replace("-", "_").replace(" ", "_")
    return normalized if normalized in _VALID_EVENT_TYPES else "unknown_paper_event"


def _sanitize_metadata(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Sanitize a metadata dict for safe storage.

    - Drops any key whose lowercased name is in ``_FORBIDDEN_META_KEYS``.
    - Drops float values that are not finite (nan, inf, -inf).
    - Truncates string values to ``_MAX_META_VALUE_STR_LEN`` characters.
    - Caps the total number of retained keys at ``_MAX_META_KEYS``.
    - Returns an empty dict if ``raw`` is None or empty.

    This function never raises — it drops problematic entries silently.
    """
    if not raw:
        return {}

    sanitized: dict[str, Any] = {}
    for key, value in raw.items():
        if len(sanitized) >= _MAX_META_KEYS:
            break
        if str(key).lower() in _FORBIDDEN_META_KEYS:
            continue
        if isinstance(value, float) and not math.isfinite(value):
            continue
        if isinstance(value, str):
            value = value[:_MAX_META_VALUE_STR_LEN]
        sanitized[key] = value

    return sanitized


# ---------------------------------------------------------------------------
# PaperAuditHistoryService
# ---------------------------------------------------------------------------

class PaperAuditHistoryService:
    """In-memory paper-only sandbox audit/activity history service.

    Thread-safe via a reentrant lock.  State is process-local and lost on
    restart — it is intentionally ephemeral.  Meant for advisory audit
    trails and testing; not for durable persistence.

    Event IDs are sequential, locally-generated, paper-scoped identifiers
    (``paper_audit_000001``, ``paper_audit_000002``, …).  They are NOT
    broker order IDs, fill IDs, or execution IDs of any kind.

    The history is bounded to ``_MAX_HISTORY`` events.  When the cap is
    reached, the oldest events are dropped (FIFO).
    """

    def __init__(self) -> None:
        self._events: deque[PaperAuditEvent] = deque(maxlen=_MAX_HISTORY)
        self._counter: int = 0
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_event_id(self) -> str:
        """Return the next sequential paper-scoped event ID.

        Must be called with ``self._lock`` already held.
        """
        self._counter += 1
        return f"paper_audit_{self._counter:06d}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append(
        self,
        event_type: str,
        message: str,
        source: str = "paper_sandbox",
        severity: str = "info",
        metadata: dict[str, Any] | None = None,
    ) -> PaperAuditEvent:
        """Append a new advisory audit event to the history.

        - ``event_type`` is normalized; unknown types map to
          ``"unknown_paper_event"``.
        - ``severity`` must be ``"info"``, ``"warning"``, or ``"blocked"``;
          any other value is coerced to ``"info"``.
        - ``metadata`` is sanitized: forbidden keys, non-finite floats, and
          oversized strings are stripped before storage.
        - ``message`` is truncated to ``_MAX_MESSAGE_LEN`` characters.
        - ``source`` is truncated to ``_MAX_SOURCE_LEN`` characters.

        Returns the stored ``PaperAuditEvent``.
        """
        safe_event_type = _normalize_event_type(event_type)
        safe_severity = severity if severity in _VALID_SEVERITIES else "info"
        safe_message = str(message)[:_MAX_MESSAGE_LEN]
        safe_source = str(source)[:_MAX_SOURCE_LEN]
        safe_meta = _sanitize_metadata(metadata)
        ts = datetime.now(timezone.utc).isoformat()

        with self._lock:
            event_id = self._make_event_id()
            event = PaperAuditEvent(
                event_id=event_id,
                timestamp=ts,
                event_type=safe_event_type,  # type: ignore[arg-type]
                source=safe_source,
                severity=safe_severity,  # type: ignore[arg-type]
                message=safe_message,
                metadata=safe_meta,
            )
            self._events.append(event)

        return event

    def list_events(self, limit: int | None = None) -> list[PaperAuditEvent]:
        """Return a snapshot of stored events, most-recent last.

        If ``limit`` is given, returns the most recent ``limit`` events.
        """
        with self._lock:
            events = list(self._events)
        if limit is not None:
            limit = max(0, limit)
            if limit == 0:
                return []
            return events[-limit:] if limit < len(events) else events
        return events

    def get_history(self) -> PaperAuditHistory:
        """Return a read-only ``PaperAuditHistory`` snapshot."""
        events = self.list_events()
        return PaperAuditHistory(events=events, count=len(events))

    def reset(self) -> None:
        """Clear all events and reset the counter.  For testing only."""
        with self._lock:
            self._events.clear()
            self._counter = 0

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)


# ---------------------------------------------------------------------------
# Module-level singleton and convenience functions
# ---------------------------------------------------------------------------

_history: PaperAuditHistoryService = PaperAuditHistoryService()


def get_paper_sandbox_history() -> PaperAuditHistoryService:
    """Return the module-level PaperAuditHistoryService singleton."""
    return _history


def record_paper_event(
    event_type: str,
    message: str,
    source: str = "paper_sandbox",
    severity: str = "info",
    metadata: dict[str, Any] | None = None,
) -> PaperAuditEvent:
    """Module-level convenience wrapper: append an event to the singleton history."""
    return _history.append(
        event_type=event_type,
        message=message,
        source=source,
        severity=severity,
        metadata=metadata,
    )
