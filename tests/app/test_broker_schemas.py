"""BRK-003 — Tests for typed read-only broker schemas.

Asserts:

* Safe defaults of ``BrokerCapabilities`` / ``BrokerStatus`` /
  ``BrokerAccountSnapshot`` / ``BrokerPosition``.
* Validators reject any combination that would represent an
  executable broker (``execution_enabled=True``,
  ``live_orders_blocked=False``, ``can_place_orders=True``,
  negative latency, ``read_only=False``).
* ``extra="forbid"`` rejects every forbidden execution / order /
  credential field by name.
* ``SafeDisconnectedBrokerAdapter`` outputs validate cleanly into
  the new schemas.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.broker import (
    BrokerAccountSnapshot,
    BrokerCapabilities,
    BrokerPosition,
    BrokerStatus,
)


# ---------------------------------------------------------------------------
# Test 1 — BrokerCapabilities safe defaults.
# ---------------------------------------------------------------------------
def test_broker_capabilities_safe_defaults() -> None:
    caps = BrokerCapabilities(safety_note="safe")
    assert caps.read_only is True
    assert caps.execution_enabled is False
    assert caps.live_orders_blocked is True
    assert caps.can_place_orders is False
    assert caps.can_cancel_orders is False
    assert caps.can_modify_orders is False
    assert caps.supports_account_snapshot is True
    assert caps.supports_positions is True
    assert caps.paper is False


# ---------------------------------------------------------------------------
# Test 2 — BrokerCapabilities rejects unsafe execution flags.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "kwargs",
    [
        {"execution_enabled": True},
        {"live_orders_blocked": False},
        {"can_place_orders": True},
        {"can_cancel_orders": True},
        {"can_modify_orders": True},
        {"read_only": False},
    ],
)
def test_broker_capabilities_rejects_unsafe_flags(
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        BrokerCapabilities(safety_note="x", **kwargs)


# ---------------------------------------------------------------------------
# Test 3 — BrokerStatus safe instance.
# ---------------------------------------------------------------------------
def test_broker_status_safe_instance() -> None:
    status = BrokerStatus(
        adapter_id="safe-disconnected",
        connected=False,
        degraded=True,
        degraded_reason="No broker connection configured",
        safety_note="safe",
    )
    assert status.read_only is True
    assert status.execution_enabled is False
    assert status.live_orders_blocked is True


# ---------------------------------------------------------------------------
# Test 4 — BrokerStatus rejects unsafe / invalid values.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "kwargs",
    [
        {"execution_enabled": True},
        {"live_orders_blocked": False},
        {"read_only": False},
        {"latency_ms": -1.0},
    ],
)
def test_broker_status_rejects_unsafe_values(
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        BrokerStatus(
            adapter_id="x",
            connected=False,
            safety_note="safe",
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Test 5 — BrokerAccountSnapshot safe disconnected-compatible instance.
# ---------------------------------------------------------------------------
def test_broker_account_snapshot_safe_disconnected_compatible() -> None:
    snap = BrokerAccountSnapshot(
        adapter_id="safe-disconnected",
        currency="USD",
        cash=0.0,
        equity=0.0,
        buying_power=0.0,
        safety_note="safe",
    )
    assert snap.cash == 0.0
    assert snap.equity == 0.0
    assert snap.buying_power == 0.0
    assert snap.read_only is True

    # read_only=False is rejected.
    with pytest.raises(ValidationError):
        BrokerAccountSnapshot(
            adapter_id="x",
            currency="USD",
            cash=0.0,
            equity=0.0,
            buying_power=0.0,
            read_only=False,
            safety_note="x",
        )


# ---------------------------------------------------------------------------
# Test 6 — BrokerPosition safe instance.
# ---------------------------------------------------------------------------
def test_broker_position_safe_instance() -> None:
    pos = BrokerPosition(
        adapter_id="safe-disconnected",
        symbol="EURUSD",
        quantity=0.0,
    )
    assert pos.symbol == "EURUSD"
    assert pos.read_only is True
    # No execution / order surface on the model.
    assert not hasattr(pos, "order_id")
    assert not hasattr(pos, "execution_id")
    assert not hasattr(pos, "trade_id")
    assert not hasattr(pos, "place_order")


# ---------------------------------------------------------------------------
# Test 7 — every schema forbids execution / order / credential fields.
# ---------------------------------------------------------------------------
_FORBIDDEN_FIELD_NAMES: tuple[str, ...] = (
    "order_id",
    "execution_id",
    "trade_id",
    "submit_order",
    "place_order",
    "cancel_order",
    "modify_order",
    "execute",
    "broker_execute",
    "credential",
    "credentials",
    "password",
    "token",
    "secret",
    "api_key",
    "account_id",
)


@pytest.mark.parametrize(
    "model, base_kwargs",
    [
        (
            BrokerCapabilities,
            {"safety_note": "x"},
        ),
        (
            BrokerStatus,
            {"adapter_id": "x", "connected": False, "safety_note": "x"},
        ),
        (
            BrokerAccountSnapshot,
            {
                "adapter_id": "x",
                "currency": "USD",
                "cash": 0.0,
                "equity": 0.0,
                "buying_power": 0.0,
                "safety_note": "x",
            },
        ),
        (
            BrokerPosition,
            {"adapter_id": "x", "symbol": "EURUSD", "quantity": 0.0},
        ),
    ],
)
@pytest.mark.parametrize("forbidden_field", _FORBIDDEN_FIELD_NAMES)
def test_schemas_reject_forbidden_extra_fields(
    model: type, base_kwargs: dict[str, object], forbidden_field: str
) -> None:
    bad_kwargs = dict(base_kwargs)
    bad_kwargs[forbidden_field] = "leak"
    with pytest.raises(ValidationError):
        model(**bad_kwargs)


# ---------------------------------------------------------------------------
# Test 8 — SafeDisconnectedBrokerAdapter outputs validate into the schemas.
# ---------------------------------------------------------------------------
def test_safe_disconnected_outputs_validate_into_schemas() -> None:
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    adapter = SafeDisconnectedBrokerAdapter()

    # capabilities() validates — drop adapter_id since BrokerCapabilities
    # does not carry it (capabilities are about *what* not *who*).
    caps_payload = dict(adapter.capabilities())
    caps_payload.pop("adapter_id", None)
    caps = BrokerCapabilities(**caps_payload)
    assert caps.read_only is True
    assert caps.execution_enabled is False

    # status() validates as-is.
    status = BrokerStatus(**dict(adapter.status()))
    assert status.connected is False
    assert status.degraded is True
    assert status.read_only is True

    # account_snapshot() validates as-is.
    snap = BrokerAccountSnapshot(**dict(adapter.account_snapshot()))
    assert snap.cash == 0.0
    assert snap.equity == 0.0

    # positions() — empty list is acceptable; if non-empty, each
    # element must validate as BrokerPosition.
    positions = [BrokerPosition(**dict(p)) for p in adapter.positions()]
    assert positions == []


# ---------------------------------------------------------------------------
# Test 9 — no schema declares any forbidden execution / order / credential
# field at the model level (defensive: catches a future drift where someone
# adds a forbidden field as an explicit attribute).
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "model",
    [BrokerCapabilities, BrokerStatus, BrokerAccountSnapshot, BrokerPosition],
)
def test_schemas_do_not_declare_forbidden_fields(model: type) -> None:
    declared = set(model.model_fields.keys())  # type: ignore[attr-defined]
    leaked = sorted(declared & set(_FORBIDDEN_FIELD_NAMES))
    assert not leaked, (
        f"{model.__name__} declares forbidden execution / order / credential "
        f"field(s): {leaked!r}"
    )
