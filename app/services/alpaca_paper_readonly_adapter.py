"""Alpaca Paper read-only adapter.

ALPACA-PAPER-READONLY-ADAPTER-001.

A safety-first, GET/read-only adapter that can optionally read Alpaca **paper**
account/positions data and expose a sanitized preview. It is the foundation for
later paper order *testing* — but this module intentionally implements **no**
order placement, cancellation, or replacement of any kind.

Behaviour:

* Default (no credentials, or read-only not explicitly enabled): a safe
  ``degraded_demo`` response. No network call, no SDK import, no crash.
* Explicitly enabled paper read-only (``ALPACA_PAPER_READONLY_ENABLED=true`` and
  ``ALPACA_ENV=paper`` with credentials present) **or** an injected client:
  read-only client calls only (``get_all_positions``), with every output
  sanitized. Any error degrades safely.
* Unsafe configuration (e.g. ``ALPACA_ENV`` not ``paper``): degrade; do not call
  Alpaca.

The adapter never stores or logs credential values, and never represents
``account_id`` / ``broker_order_id`` / ``execution_id`` / ``api_key`` /
``secret`` / ``token`` in its output.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Literal, Optional, Protocol

from app.schemas.alpaca_paper_readonly import (
    AlpacaPaperPositionsPreview,
    AlpacaPaperReadOnlyPosition,
)

EnvReader = Callable[[str], Optional[str]]


class ReadOnlyPositionsClient(Protocol):
    """Minimal read-only client contract used by the adapter.

    Only the read-only ``get_all_positions`` call is part of the contract. The
    adapter never references any mutating method (submit/cancel/replace).
    """

    def get_all_positions(self) -> Any:  # pragma: no cover - structural typing
        ...


def _flag(env: EnvReader, name: str) -> bool:
    return (env(name) or "").strip().lower() == "true"


def _is_paper_env(env: EnvReader) -> bool:
    # Default to "paper" when unset; anything other than paper is treated unsafe.
    return (env("ALPACA_ENV") or "paper").strip().lower() == "paper"


def _has_credentials(env: EnvReader) -> bool:
    key = env("ALPACA_API_KEY") or env("APCA_API_KEY_ID")
    secret = env("ALPACA_SECRET_KEY") or env("APCA_API_SECRET_KEY")
    return bool(key) and bool(secret)


def _coerce_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _coerce_side(value: Any) -> Literal["long", "short", "unknown"]:
    text = str(value or "").strip().lower()
    if "short" in text:
        return "short"
    if "long" in text:
        return "long"
    return "unknown"


def _attr(raw: Any, name: str) -> Any:
    if isinstance(raw, dict):
        return raw.get(name)
    return getattr(raw, name, None)


class AlpacaPaperReadOnlyAdapter:
    """Read-only adapter for Alpaca Paper account/positions previews."""

    def __init__(
        self,
        *,
        client: Optional[ReadOnlyPositionsClient] = None,
        env_reader: EnvReader = os.getenv,
    ) -> None:
        # An injected client is treated as an explicit, trusted read-only client
        # (used by tests and by callers that build their own paper client).
        self._client = client
        self._env = env_reader

    # -- client resolution -------------------------------------------------

    def _resolve_client(self) -> Optional[ReadOnlyPositionsClient]:
        if self._client is not None:
            return self._client
        # Only build a default client when read-only is explicitly enabled for a
        # paper environment with credentials present. Otherwise: no Alpaca call.
        if not (
            _flag(self._env, "ALPACA_PAPER_READONLY_ENABLED")
            and _is_paper_env(self._env)
            and _has_credentials(self._env)
        ):
            return None
        return self._build_default_client()

    def _build_default_client(self) -> Optional[ReadOnlyPositionsClient]:
        """Lazily build a paper-only Alpaca trading client.

        Imported lazily so the module works without the Alpaca SDK installed
        (CI runs without it). ``paper=True`` forces the paper endpoint; the live
        endpoint is never used here. Credentials are read locally and passed to
        the SDK only — never stored on the adapter, never logged.
        """
        try:
            from alpaca.trading.client import TradingClient  # type: ignore

            key = self._env("ALPACA_API_KEY") or self._env("APCA_API_KEY_ID")
            secret = self._env("ALPACA_SECRET_KEY") or self._env("APCA_API_SECRET_KEY")
            return TradingClient(key, secret, paper=True)
        except Exception:
            # Any import/construction failure degrades safely.
            return None

    # -- preview -----------------------------------------------------------

    def get_positions_preview(self) -> AlpacaPaperPositionsPreview:
        """Return a sanitized, read-only positions preview.

        Never raises and never places an order. On any failure or when no
        read-only client is available, returns a safe ``degraded_demo`` preview.
        """
        client = self._resolve_client()
        if client is None:
            return self._degraded()

        try:
            raw_positions = client.get_all_positions()
            positions = self._sanitize_positions(raw_positions)
        except Exception:
            # Malformed client / network / SDK error -> degrade safely.
            return self._degraded()

        return AlpacaPaperPositionsPreview(
            mode="paper_readonly",
            connected=True,
            source="alpaca_paper_readonly",
            count=len(positions),
            positions=positions,
        )

    # -- helpers -----------------------------------------------------------

    def _sanitize_positions(
        self, raw_positions: Any
    ) -> list[AlpacaPaperReadOnlyPosition]:
        if not isinstance(raw_positions, (list, tuple)):
            return []
        sanitized: list[AlpacaPaperReadOnlyPosition] = []
        for raw in raw_positions:
            symbol = str(_attr(raw, "symbol") or "").strip().upper()
            if not symbol:
                continue
            sanitized.append(
                AlpacaPaperReadOnlyPosition(
                    symbol=symbol,
                    qty=_coerce_float(_attr(raw, "qty")),
                    market_value=_coerce_float(_attr(raw, "market_value")),
                    unrealized_pl=_coerce_float(_attr(raw, "unrealized_pl")),
                    side=_coerce_side(_attr(raw, "side")),
                )
            )
        return sanitized

    def _degraded(self) -> AlpacaPaperPositionsPreview:
        return AlpacaPaperPositionsPreview(
            mode="degraded_demo",
            connected=False,
            source="fallback",
            count=0,
            positions=[],
        )
