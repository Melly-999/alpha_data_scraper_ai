"""Signal decision reader — SUPA-011 / SUPA-014.

Reads SignalDecisionRecord rows from mellytrade.signal_decisions in Supabase.
Falls back gracefully (returns []) when the client is unavailable or the query
fails — never raises to the caller.

Design constraints:
  - Read-only only. No writes, no mutations.
  - No realtime subscriptions, no WebSocket, no EventSource.
  - Deterministic ordering: created_at DESC.
  - Limit clamped: 1 <= limit <= 500.
  - Invalid or unparseable rows are skipped silently.
  - No account data, broker data, execution data, or live positions.
  - Never raises.

Public API:
  read_signal_decisions(
      *, symbol=None, limit=100, from_date=None, to_date=None,
      client=None, _select_fn=None
  ) -> list[SignalDecisionRecord]

SUPA-014 additions:
  - Optional ``from_date`` / ``to_date`` filters applied server-side
    against ``created_at`` via Supabase ``.gte()`` / ``.lte()``.
  - Both filters are optional and fully backwards-compatible.
  - Invalid date ranges (from_date > to_date) are tolerated; query may
    return an empty list — never raises.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable

from app.schemas.signal_decision import SignalDecisionRecord

logger = logging.getLogger(__name__)

# Table name — schema prefix handled at Supabase project level (search_path).
_DECISIONS_TABLE = "signal_decisions"

_LIMIT_MIN = 1
_LIMIT_MAX = 500
_LIMIT_DEFAULT = 100


def _clamp_limit(limit: int) -> int:
    """Return limit clamped to [_LIMIT_MIN, _LIMIT_MAX]."""
    return max(_LIMIT_MIN, min(limit, _LIMIT_MAX))


def _parse_timestamp(raw: Any) -> datetime:
    """Parse a created_at value from Supabase into a timezone-aware datetime.

    Supabase returns ISO 8601 strings or datetime objects.
    Falls back to utcnow() when the value cannot be parsed.
    """
    if isinstance(raw, datetime):
        if raw.tzinfo is None:
            return raw.replace(tzinfo=timezone.utc)
        return raw
    if isinstance(raw, str):
        try:
            # Replace trailing Z with +00:00 for Python 3.10 compat.
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _row_to_record(row: dict[str, Any]) -> SignalDecisionRecord | None:
    """Convert a Supabase row dict to a SignalDecisionRecord.

    Returns None when the row is missing required fields or contains values
    that fail Pydantic validation — the caller skips None results.

    Safety invariants are re-enforced here regardless of what the DB returned.
    """
    try:
        raw_id = row.get("id")
        if not raw_id:
            return None

        strategy_val = row.get("strategy") or "scanner"

        return SignalDecisionRecord(
            id=str(raw_id),
            timestamp=_parse_timestamp(row.get("created_at")),
            symbol=row["symbol"],
            direction=row["direction"],  # type: ignore[arg-type]
            confidence=float(row["confidence"]),
            source=row.get("source") or "scanner",
            strategy=strategy_val,
            risk_status=row["risk_status"],  # type: ignore[arg-type]
            decision=row["decision"],  # type: ignore[arg-type]
            blocked_reason=row.get("blocked_reason"),
            audit_event_id=row.get("audit_event_id"),
            # Safety invariants: always forced to safe values regardless of DB.
            dry_run=True,
            auto_trade=False,
            read_only=True,
            stop_loss_required=True,
            take_profit_required=True,
            max_risk_per_trade=0.01,
            metadata={},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "signal_decision_reader: skipping invalid row — %s. row_id=%s",
            exc,
            row.get("id", "?"),
        )
        return None


def _to_iso(value: datetime | None) -> str | None:
    """Serialize a datetime to ISO 8601 UTC for Supabase filter calls.

    Returns None when value is None.  Naive datetimes are treated as UTC.
    Read-only formatting helper — never raises.
    """
    if value is None:
        return None
    try:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    except Exception:  # noqa: BLE001
        return None


def read_signal_decisions(
    *,
    symbol: str | None = None,
    limit: int = _LIMIT_DEFAULT,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    client: Any | None = None,
    _select_fn: Callable[..., Any] | None = None,
) -> list[SignalDecisionRecord]:
    """Read signal decisions from Supabase, ordered by recency.

    Returns an empty list when Supabase is unavailable or the query fails.
    Invalid rows are skipped silently.  Never raises.

    Parameters
    ----------
    symbol:
        Optional symbol filter applied server-side.  Pass None to return all.
    limit:
        Maximum number of records to return.  Clamped to [1, 500].
        Default: 100.
    from_date:
        Optional inclusive lower bound for ``created_at`` (UTC).
        Applied server-side via ``.gte()``.  Pass None to skip the filter.
    to_date:
        Optional inclusive upper bound for ``created_at`` (UTC).
        Applied server-side via ``.lte()``.  Pass None to skip the filter.
    client:
        Supabase client from get_safe_supabase_client().
        Pass None to trigger the degraded path (returns []).
    _select_fn:
        Injectable callable used by tests to avoid real network calls.
        Signature: ``(table: str, symbol: str | None, limit: int, **kwargs)
        -> response``.  ``from_date`` and ``to_date`` are passed as keyword
        arguments (ISO 8601 strings or None).  Response must expose a
        ``data`` attribute (list[dict] or None).
        Pass None (default) to use the real client path.

    Returns
    -------
    list[SignalDecisionRecord]
        Empty list when Supabase is unavailable or query fails.
        Records with dry_run=True, auto_trade=False, read_only=True always.
    """
    bounded = _clamp_limit(limit)

    if client is None and _select_fn is None:
        logger.debug("signal_decision_reader: no client — returning empty list (degraded)")
        return []

    from_iso = _to_iso(from_date)
    to_iso = _to_iso(to_date)

    try:
        if _select_fn is not None:
            response = _select_fn(
                _DECISIONS_TABLE,
                symbol,
                bounded,
                from_date=from_iso,
                to_date=to_iso,
            )
        else:
            query = (
                client.table(_DECISIONS_TABLE)
                .select("*")
                .order("created_at", desc=True)
            )
            if symbol is not None:
                query = query.eq("symbol", symbol.upper())
            if from_iso is not None:
                query = query.gte("created_at", from_iso)
            if to_iso is not None:
                query = query.lte("created_at", to_iso)
            response = query.limit(bounded).execute()

        rows: list[dict[str, Any]] = []
        if response is not None:
            data = getattr(response, "data", None)
            if data and isinstance(data, list):
                rows = data

        records: list[SignalDecisionRecord] = []
        for row in rows:
            parsed = _row_to_record(row)
            if parsed is not None:
                records.append(parsed)

        return records

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "signal_decision_reader: query failed — returning [] (degraded): %s", exc
        )
        return []
