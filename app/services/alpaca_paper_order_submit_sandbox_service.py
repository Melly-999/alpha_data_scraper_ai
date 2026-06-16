"""ALPACA-PAPER-ORDER-SUBMIT-SANDBOX-001 — gated paper order submission sandbox.

A backend-only service that may submit **exactly one** small order to Alpaca
**Paper** — but only when every explicit gate is satisfied. It is blocked by
default and is **never** wired to any frontend control.

Why this is dangerous: it is the only path in the codebase that can place a real
(paper) order. It is therefore gated by environment flags, an acknowledgement
string, present credentials, and per-request confirmation, validated against the
existing draft risk rules, bounded by conservative sandbox caps, and isolated
from the legacy live adapter (``brokers/alpaca_adapter.py``), which is **not**
imported here.

Hard rules:
- No live endpoint. The client is built ``paper=True`` only, after re-checking
  ``ALPACA_ENV=paper``.
- No cancellation / replacement / bracket / OCO / multi-leg / options / crypto /
  futures. Exactly one market-or-limit entry order.
- No background job, no retry loop (a single attempt — never auto-retried to
  avoid duplicate orders).
- The SDK is imported lazily only inside the gated client factory.
- The response never carries a raw broker order id, account id, api key, secret,
  or token — only a redacted order id and our own client order id.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol

from app.schemas.alpaca_paper_order_draft import AlpacaPaperOrderDraftRequest
from app.schemas.alpaca_paper_order_submit_sandbox import (
    AlpacaPaperOrderSubmitSandboxRequest,
    AlpacaPaperOrderSubmitSandboxResponse,
)
from app.services.alpaca_paper_order_draft_service import (
    build_alpaca_paper_order_draft,
)

EnvReader = Callable[[str], Optional[str]]

# Conservative sandbox bounds — never unbounded.
_MAX_SANDBOX_QTY: float = 100.0
_MAX_SANDBOX_NOTIONAL: float = 5000.0
_SUBMITTABLE_ORDER_TYPES: frozenset[str] = frozenset({"market", "limit"})
_REQUIRED_ACK: str = "I_UNDERSTAND_THIS_SUBMITS_A_PAPER_ORDER"
_CLIENT_ID_PREFIX: str = "mt-paper-sandbox-"


@dataclass(frozen=True)
class SubmittedOrderResult:
    """Normalized, redaction-ready result of a single paper submission."""

    raw_order_id: str
    client_order_id: str
    status: str


class PaperOrderClient(Protocol):
    """Minimal contract for the gated paper order client.

    Only a single ``submit_paper_order`` call is part of the contract. No
    cancel / replace / list / live method is referenced anywhere.
    """

    def submit_paper_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
        time_in_force: str,
        quantity: Optional[float],
        notional: Optional[float],
        limit_price: Optional[float],
        client_order_id: str,
    ) -> SubmittedOrderResult:  # pragma: no cover - structural typing
        ...


def _flag(env: EnvReader, name: str) -> bool:
    return (env(name) or "").strip().lower() == "true"


def _is_paper_env(env: EnvReader) -> bool:
    return (env("ALPACA_ENV") or "").strip().lower() == "paper"


def _has_credentials(env: EnvReader) -> bool:
    key = env("ALPACA_API_KEY") or env("APCA_API_KEY_ID")
    secret = env("ALPACA_SECRET_KEY") or env("APCA_API_SECRET_KEY")
    return bool(key) and bool(secret)


def _redact_order_id(raw_order_id: str) -> str:
    digest = hashlib.sha256(raw_order_id.encode()).hexdigest()[:12]
    return f"alpaca-paper-sub-{digest}"


class AlpacaPaperOrderSubmitSandboxService:
    """Gated, paper-only, single-order submission sandbox."""

    def __init__(
        self,
        *,
        client: Optional[PaperOrderClient] = None,
        env_reader: EnvReader = os.getenv,
    ) -> None:
        # An injected client is an explicit, trusted paper client (tests / a
        # caller that built its own paper client). It bypasses the default
        # SDK factory but NOT the gate checks below.
        self._client = client
        self._env = env_reader

    # -- public API --------------------------------------------------------

    def submit(
        self, request: AlpacaPaperOrderSubmitSandboxRequest
    ) -> AlpacaPaperOrderSubmitSandboxResponse:
        """Attempt a gated paper order submission. Never raises for bad input."""
        # 1) Reuse the full draft risk validation (side/type/tif/qty-notional/
        #    geometry/risk cap). A blocked draft blocks submission.
        draft = build_alpaca_paper_order_draft(self._as_draft_request(request))
        if not draft.valid:
            return self._blocked(draft.reason)

        # 2) Sandbox-specific input limits.
        limit_reason = self._check_sandbox_limits(request)
        if limit_reason is not None:
            return self._blocked(limit_reason)

        # 3) Per-request confirmation gates.
        if request.source.strip() != "manual_sandbox":
            return self._blocked('source must be "manual_sandbox". Blocked.')
        if request.confirm_paper_order is not True:
            return self._blocked("confirm_paper_order must be true. Blocked.")

        # 4) Environment gates. Any failure -> no Alpaca call.
        gate_reason = self._check_env_gates()
        if gate_reason is not None:
            return self._blocked(gate_reason)

        # All gates satisfied: submission is enabled.
        if request.dry_run_preview_only:
            return AlpacaPaperOrderSubmitSandboxResponse(
                accepted=True,
                submitted_to_alpaca_paper=False,
                order_submission_enabled=True,
                blocked_reason=None,
                message=(
                    "All gates satisfied. dry_run_preview_only=true — no order "
                    "submitted to Alpaca. Not live trading."
                ),
            )

        client = self._resolve_client()
        if client is None:
            return self._blocked(
                "Paper order client unavailable (SDK missing or build failed). "
                "No order submitted."
            )

        client_order_id = f"{_CLIENT_ID_PREFIX}{uuid.uuid4().hex[:16]}"
        try:
            # Exactly one attempt — never retried (avoids duplicate orders).
            result = client.submit_paper_order(
                symbol=request.symbol.strip().upper(),
                side=request.side.strip().upper(),
                order_type=request.order_type.strip().lower(),
                time_in_force=request.time_in_force.strip().lower(),
                quantity=request.quantity,
                notional=request.notional,
                limit_price=request.limit_price,
                client_order_id=client_order_id,
            )
        except Exception:
            # Never leak the exception / credentials. Safe blocked response.
            return AlpacaPaperOrderSubmitSandboxResponse(
                accepted=False,
                submitted_to_alpaca_paper=False,
                order_submission_enabled=True,
                blocked_reason="Paper submission attempt failed; no order confirmed.",
                message="Paper submission error — see local server logs. Not live trading.",
            )

        safe_client_id = (
            result.client_order_id
            if str(result.client_order_id).startswith(_CLIENT_ID_PREFIX)
            else client_order_id
        )
        return AlpacaPaperOrderSubmitSandboxResponse(
            accepted=True,
            submitted_to_alpaca_paper=True,
            order_submission_enabled=True,
            blocked_reason=None,
            redacted_order_id=_redact_order_id(str(result.raw_order_id)),
            client_order_id=safe_client_id,
            order_status=str(result.status),
            message=(
                "Paper order submitted to Alpaca Paper sandbox. Not live trading; "
                "live orders remain blocked and dry-run posture is unchanged."
            ),
        )

    # -- helpers -----------------------------------------------------------

    def _as_draft_request(
        self, request: AlpacaPaperOrderSubmitSandboxRequest
    ) -> AlpacaPaperOrderDraftRequest:
        return AlpacaPaperOrderDraftRequest(
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            time_in_force=request.time_in_force,
            quantity=request.quantity,
            notional=request.notional,
            entry_price=request.entry_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            max_risk_pct=request.max_risk_pct,
        )

    def _check_sandbox_limits(
        self, request: AlpacaPaperOrderSubmitSandboxRequest
    ) -> Optional[str]:
        order_type = request.order_type.strip().lower()
        if order_type not in _SUBMITTABLE_ORDER_TYPES:
            return (
                f"order_type '{request.order_type}' is not submittable in the "
                "sandbox (market or limit only). Blocked."
            )
        if order_type == "limit" and not (
            request.limit_price is not None and request.limit_price > 0
        ):
            return "limit order requires a positive limit_price. Blocked."
        if request.quantity is not None and request.quantity > _MAX_SANDBOX_QTY:
            return f"quantity exceeds sandbox cap of {_MAX_SANDBOX_QTY}. Blocked."
        if request.notional is not None and request.notional > _MAX_SANDBOX_NOTIONAL:
            return f"notional exceeds sandbox cap of {_MAX_SANDBOX_NOTIONAL}. Blocked."
        return None

    def _check_env_gates(self) -> Optional[str]:
        if not _is_paper_env(self._env):
            return "ALPACA_ENV must be 'paper'. Blocked (no Alpaca call)."
        if not _flag(self._env, "ALPACA_PAPER_ORDER_SUBMIT_ENABLED"):
            return "ALPACA_PAPER_ORDER_SUBMIT_ENABLED must be 'true'. Blocked."
        ack = (self._env("ALPACA_PAPER_ORDER_SUBMIT_SANDBOX_ACK") or "").strip()
        if ack != _REQUIRED_ACK:
            return "Sandbox acknowledgement gate not satisfied. Blocked."
        if not _has_credentials(self._env):
            return "Alpaca paper credentials are not present. Blocked."
        return None

    def _resolve_client(self) -> Optional[PaperOrderClient]:
        if self._client is not None:
            return self._client
        return self._build_paper_order_client()

    def _build_paper_order_client(self) -> Optional[PaperOrderClient]:
        """Lazily build a paper-only Alpaca order client.

        Only reached after every gate has passed. Re-checks ``ALPACA_ENV=paper``
        and builds the SDK client ``paper=True`` (paper endpoint only). The live
        endpoint is never used. Returns ``None`` on any failure (degrade safely).
        """
        if not _is_paper_env(self._env):  # defense in depth
            return None
        try:
            from alpaca.trading.client import TradingClient  # type: ignore

            key = self._env("ALPACA_API_KEY") or self._env("APCA_API_KEY_ID")
            secret = self._env("ALPACA_SECRET_KEY") or self._env("APCA_API_SECRET_KEY")
            trading_client = TradingClient(key, secret, paper=True)
            return _AlpacaPaperOrderClient(trading_client)
        except Exception:
            return None

    def _blocked(self, reason: str) -> AlpacaPaperOrderSubmitSandboxResponse:
        return AlpacaPaperOrderSubmitSandboxResponse(
            accepted=False,
            submitted_to_alpaca_paper=False,
            order_submission_enabled=False,
            blocked_reason=reason,
        )


class _AlpacaPaperOrderClient:
    """Adapter over the Alpaca SDK trading client — paper submit only.

    Constructed only inside the gated factory. Lazily imports the SDK request
    types and submits exactly one market/limit order. References no cancel /
    replace / live method.
    """

    def __init__(self, trading_client: Any) -> None:
        self._client = trading_client

    def submit_paper_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
        time_in_force: str,
        quantity: Optional[float],
        notional: Optional[float],
        limit_price: Optional[float],
        client_order_id: str,
    ) -> SubmittedOrderResult:
        from alpaca.trading.enums import OrderSide, TimeInForce  # type: ignore
        from alpaca.trading.requests import (  # type: ignore
            LimitOrderRequest,
            MarketOrderRequest,
        )

        order_side = OrderSide.BUY if side == "BUY" else OrderSide.SELL
        tif = TimeInForce(time_in_force)
        common: dict[str, Any] = {
            "symbol": symbol,
            "side": order_side,
            "time_in_force": tif,
            "client_order_id": client_order_id,
        }
        if quantity is not None:
            common["qty"] = quantity
        if notional is not None:
            common["notional"] = notional

        if order_type == "limit":
            request_obj = LimitOrderRequest(limit_price=limit_price, **common)
        else:
            request_obj = MarketOrderRequest(**common)

        submitted = self._client.submit_order(order_data=request_obj)
        return SubmittedOrderResult(
            raw_order_id=str(getattr(submitted, "id", "")),
            client_order_id=str(getattr(submitted, "client_order_id", client_order_id)),
            status=str(getattr(submitted, "status", "")),
        )
