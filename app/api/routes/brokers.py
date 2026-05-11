"""BRK-008..011 — GET-only broker endpoints.

Surfaces the read-only :class:`brokers.registry.BrokerRegistry` over a
GET-only FastAPI router:

* ``GET /api/brokers``                            - list registered adapters + capabilities
* ``GET /api/brokers/{adapter_id}/status``        - read-only health snapshot
* ``GET /api/brokers/{adapter_id}/account``       - read-only account snapshot
* ``GET /api/brokers/{adapter_id}/positions``     - read-only positions list

Safety contract:

* GET-only by construction. Other HTTP methods automatically return 405
  (FastAPI's standard behaviour for an unmatched method on a routed path).
* No execution, order, autotrade, or risk-mutation surface. The path
  segments are deliberately chosen (``status`` / ``account`` /
  ``positions``) to avoid every forbidden token monitored by
  ``tests/app/test_openapi_forbidden_paths.py``.
* The registry returned by :func:`_registry` is the default registry,
  which contains exactly one adapter today —
  :class:`brokers.safe_disconnected.SafeDisconnectedBrokerAdapter` —
  and never an executable adapter.
* Missing adapter lookups raise HTTP 404 with a clear, secret-free
  message that names the unknown id and lists known ids.
* Responses are validated via the BRK-003 schemas, which themselves
  reject any execution / order / credential field.

The legacy ``app/api/routes/broker.py`` (singular) is unrelated and
remains untouched.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.schemas.broker import (
    BrokerAccountSnapshot,
    BrokerCapabilities,
    BrokerPosition,
    BrokerStatus,
)
from brokers.protocol import BrokerAdapter
from brokers.registry import BrokerRegistry, create_default_registry

router = APIRouter(tags=["brokers"])


# ---------------------------------------------------------------------------
# Registry resolution.
#
# Cached on ``app.state.broker_registry`` so a single process-wide
# registry instance is reused across requests. The default factory is
# safe by construction (only ``safe-disconnected``); tests that need a
# custom registry can swap in their own via ``app.state.broker_registry``
# before issuing requests.
# ---------------------------------------------------------------------------
def _registry(request: Request) -> BrokerRegistry:
    cached = getattr(request.app.state, "broker_registry", None)
    if cached is not None:
        return cached
    registry = create_default_registry()
    request.app.state.broker_registry = registry
    return registry


def _capabilities_payload(adapter: BrokerAdapter) -> dict[str, Any]:
    """Coerce the adapter's capabilities into a plain dict and drop the
    optional ``adapter_id`` key so it can be carried as a sibling field.

    Capabilities answer *what*, not *who*; the wrapping list item already
    carries ``adapter_id``.
    """
    payload = dict(adapter.capabilities())
    payload.pop("adapter_id", None)
    return payload


def _resolve_adapter(registry: BrokerRegistry, adapter_id: str) -> BrokerAdapter:
    adapter = registry.get_optional(adapter_id)
    if adapter is None:
        known = registry.list_adapter_ids()
        raise HTTPException(
            status_code=404,
            detail=(
                f"No broker adapter registered with id '{adapter_id}'. "
                f"Known ids: {known}"
            ),
        )
    return adapter


# ---------------------------------------------------------------------------
# GET /api/brokers
# ---------------------------------------------------------------------------
@router.get("/brokers")
def list_brokers(request: Request) -> dict[str, Any]:
    """List registered broker adapters with their read-only capabilities."""
    registry = _registry(request)
    adapters_payload: list[dict[str, Any]] = []
    for adapter in registry.list_adapters():
        capabilities = BrokerCapabilities(**_capabilities_payload(adapter))
        adapters_payload.append(
            {
                "adapter_id": adapter.adapter_id,
                "capabilities": capabilities.model_dump(),
            }
        )
    return {
        "default_adapter_id": registry.default_adapter_id,
        "adapters": adapters_payload,
    }


# ---------------------------------------------------------------------------
# GET /api/brokers/{adapter_id}/status
# ---------------------------------------------------------------------------
@router.get("/brokers/{adapter_id}/status", response_model=BrokerStatus)
def broker_status(adapter_id: str, request: Request) -> BrokerStatus:
    adapter = _resolve_adapter(_registry(request), adapter_id)
    return BrokerStatus(**dict(adapter.status()))


# ---------------------------------------------------------------------------
# GET /api/brokers/{adapter_id}/account
# ---------------------------------------------------------------------------
@router.get("/brokers/{adapter_id}/account", response_model=BrokerAccountSnapshot)
def broker_account(adapter_id: str, request: Request) -> BrokerAccountSnapshot:
    adapter = _resolve_adapter(_registry(request), adapter_id)
    return BrokerAccountSnapshot(**dict(adapter.account_snapshot()))


# ---------------------------------------------------------------------------
# GET /api/brokers/{adapter_id}/positions
# ---------------------------------------------------------------------------
@router.get(
    "/brokers/{adapter_id}/positions", response_model=list[BrokerPosition]
)
def broker_positions(adapter_id: str, request: Request) -> list[BrokerPosition]:
    adapter = _resolve_adapter(_registry(request), adapter_id)
    return [BrokerPosition(**dict(p)) for p in adapter.positions()]
