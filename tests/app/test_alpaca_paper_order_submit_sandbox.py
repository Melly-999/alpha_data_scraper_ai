"""TEST-ALPACA-PAPER-ORDER-SUBMIT-SANDBOX — gated paper submission safety.

Verifies ALPACA-PAPER-ORDER-SUBMIT-SANDBOX-001:

- Blocked by default and on every individual gate failure (env/ACK/creds/
  confirm/source) — and no Alpaca/network call is made when blocked.
- Reuses the draft risk validation (side/type/tif/qty-notional/geometry/risk).
- Submits exactly once via an injected fake client only when every gate passes;
  returns a redacted order id (never the raw broker order id / account id /
  credentials).
- dry_run_preview_only exercises the gates without submitting.
- A raising client degrades to a safe response (no leak).
- The route is POST-only; GET/PUT/PATCH/DELETE → 405; OpenAPI exposes the
  sandbox route and no submit/place/execute/cancel live paths.
- The narrow guardrail allowlists do NOT exempt live-execution path names.

No test requires real Alpaca credentials or performs real network calls.
"""

from __future__ import annotations

from collections.abc import Iterable

import pytest

from app.schemas.alpaca_paper_order_submit_sandbox import (
    AlpacaPaperOrderSubmitSandboxRequest,
)
from app.services import alpaca_paper_order_submit_sandbox_service as sandbox_module
from app.services.alpaca_paper_order_submit_sandbox_service import (
    AlpacaPaperOrderSubmitSandboxService,
    SubmittedOrderResult,
)

_REQUIRED_ACK = "I_UNDERSTAND_THIS_SUBMITS_A_PAPER_ORDER"

_GATED_ENV = {
    "ALPACA_ENV": "paper",
    "ALPACA_PAPER_ORDER_SUBMIT_ENABLED": "true",
    "ALPACA_PAPER_ORDER_SUBMIT_SANDBOX_ACK": _REQUIRED_ACK,
    "ALPACA_API_KEY": "present-key",
    "ALPACA_SECRET_KEY": "present-secret",
}

_FORBIDDEN_KEYS = frozenset(
    {
        "account_id",
        "broker_account_id",
        "broker_order_id",
        "raw_order_id",
        "api_key",
        "api_secret",
        "secret",
        "token",
        "password",
    }
)


def _walk_keys(value: object) -> Iterable[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _walk_keys(nested)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_keys(item)


def _req(**overrides: object) -> AlpacaPaperOrderSubmitSandboxRequest:
    base: dict[str, object] = {
        "symbol": "AAPL",
        "side": "BUY",
        "order_type": "market",
        "time_in_force": "day",
        "quantity": 10,
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "take_profit": 110.0,
        "max_risk_pct": 0.5,
        "confirm_paper_order": True,
        "source": "manual_sandbox",
    }
    base.update(overrides)
    return AlpacaPaperOrderSubmitSandboxRequest(**base)  # type: ignore[arg-type]


class _FakeClient:
    def __init__(self, *, raises: bool = False) -> None:
        self.calls = 0
        self._raises = raises
        self.last_kwargs: dict[str, object] = {}

    def submit_paper_order(self, **kwargs: object) -> SubmittedOrderResult:
        self.calls += 1
        self.last_kwargs = kwargs
        if self._raises:
            raise RuntimeError("simulated paper submission failure")
        return SubmittedOrderResult(
            raw_order_id="BROKER-RAW-ORDER-ID-12345",
            client_order_id=str(kwargs.get("client_order_id", "")),
            status="accepted",
        )


def _service(env: dict | None = None, **kw) -> AlpacaPaperOrderSubmitSandboxService:
    reader = (env if env is not None else {}).get
    return AlpacaPaperOrderSubmitSandboxService(env_reader=reader, **kw)


def _assert_locked_safety(payload: dict) -> None:
    assert payload["paper_only"] is True
    assert payload["live_trading"] is False
    assert payload["live_orders_blocked"] is True
    assert payload["dry_run"] is True
    assert payload["read_only_posture_preserved"] is True
    assert payload["execution_enabled"] is False
    assert payload["requires_human_review"] is True


# --- default blocked / gate failures ---------------------------------------


def test_blocked_with_no_env_and_no_client() -> None:
    fake = _FakeClient()
    resp = _service({}, client=fake).submit(_req())
    payload = resp.model_dump()
    _assert_locked_safety(payload)
    assert payload["accepted"] is False
    assert payload["submitted_to_alpaca_paper"] is False
    assert payload["order_submission_enabled"] is False
    assert payload["blocked_reason"]
    assert fake.calls == 0  # never reached the client


@pytest.mark.parametrize(
    "drop_key",
    [
        "ALPACA_ENV",
        "ALPACA_PAPER_ORDER_SUBMIT_ENABLED",
        "ALPACA_PAPER_ORDER_SUBMIT_SANDBOX_ACK",
        "ALPACA_API_KEY",
        "ALPACA_SECRET_KEY",
    ],
)
def test_blocked_when_any_env_gate_missing(drop_key: str) -> None:
    env = {k: v for k, v in _GATED_ENV.items() if k != drop_key}
    fake = _FakeClient()
    resp = _service(env, client=fake).submit(_req())
    assert resp.accepted is False
    assert resp.submitted_to_alpaca_paper is False
    assert fake.calls == 0


def test_blocked_when_env_is_live() -> None:
    env = dict(_GATED_ENV, ALPACA_ENV="live")
    fake = _FakeClient()
    resp = _service(env, client=fake).submit(_req())
    assert resp.accepted is False
    assert "paper" in (resp.blocked_reason or "").lower()
    assert fake.calls == 0


def test_blocked_when_ack_wrong() -> None:
    env = dict(_GATED_ENV, ALPACA_PAPER_ORDER_SUBMIT_SANDBOX_ACK="nope")
    fake = _FakeClient()
    resp = _service(env, client=fake).submit(_req())
    assert resp.accepted is False
    assert fake.calls == 0


def test_blocked_when_confirm_false() -> None:
    fake = _FakeClient()
    resp = _service(_GATED_ENV, client=fake).submit(_req(confirm_paper_order=False))
    assert resp.accepted is False
    assert fake.calls == 0


def test_blocked_when_source_wrong() -> None:
    fake = _FakeClient()
    resp = _service(_GATED_ENV, client=fake).submit(_req(source="api"))
    assert resp.accepted is False
    assert fake.calls == 0


# --- reused draft validation + sandbox limits ------------------------------


@pytest.mark.parametrize(
    "overrides",
    [
        {"side": "HOLD"},
        {"order_type": "iceberg"},
        {"time_in_force": "forever"},
        {"quantity": 10, "notional": 1000.0},  # both
        {"quantity": None, "notional": None},  # neither
        {"quantity": 0},  # non-positive
        {"max_risk_pct": 1.5},  # over cap
        {"stop_loss": None},  # missing protective level
        {"order_type": "stop"},  # not submittable in sandbox
        {"quantity": 1000},  # exceeds sandbox qty cap
        {"quantity": None, "notional": 999999.0},  # exceeds notional cap
        {"order_type": "limit", "limit_price": None},  # limit needs price
    ],
)
def test_invalid_requests_blocked_before_submission(overrides: dict) -> None:
    fake = _FakeClient()
    resp = _service(_GATED_ENV, client=fake).submit(_req(**overrides))
    assert resp.accepted is False
    assert resp.submitted_to_alpaca_paper is False
    assert fake.calls == 0


# --- successful gated submission -------------------------------------------


def test_all_gates_satisfied_submits_once_via_fake_client() -> None:
    fake = _FakeClient()
    resp = _service(_GATED_ENV, client=fake).submit(_req())
    payload = resp.model_dump()

    _assert_locked_safety(payload)
    assert payload["accepted"] is True
    assert payload["submitted_to_alpaca_paper"] is True
    assert payload["order_submission_enabled"] is True
    assert fake.calls == 1  # exactly once, never retried
    assert payload["order_status"] == "accepted"


def test_submission_redacts_ids_and_leaks_no_secrets() -> None:
    fake = _FakeClient()
    resp = _service(_GATED_ENV, client=fake).submit(_req())
    payload = resp.model_dump()

    # Redacted id present; raw broker id never surfaced anywhere.
    assert payload["redacted_order_id"].startswith("alpaca-paper-sub-")
    blob = repr(payload)
    assert "BROKER-RAW-ORDER-ID-12345" not in blob
    assert "present-key" not in blob and "present-secret" not in blob
    # Our own client_order_id prefix is safe to echo.
    assert payload["client_order_id"].startswith("mt-paper-sandbox-")
    leaked = sorted(set(_walk_keys(payload)) & _FORBIDDEN_KEYS)
    assert not leaked, f"forbidden keys leaked: {leaked!r}"


def test_limit_order_submits_with_price() -> None:
    fake = _FakeClient()
    resp = _service(_GATED_ENV, client=fake).submit(
        _req(order_type="limit", limit_price=99.0)
    )
    assert resp.accepted is True and resp.submitted_to_alpaca_paper is True
    assert fake.last_kwargs.get("limit_price") == 99.0


def test_dry_run_preview_only_does_not_submit() -> None:
    fake = _FakeClient()
    resp = _service(_GATED_ENV, client=fake).submit(_req(dry_run_preview_only=True))
    assert resp.accepted is True
    assert resp.submitted_to_alpaca_paper is False
    assert resp.order_submission_enabled is True
    assert fake.calls == 0  # gates passed but no submission


def test_raising_client_degrades_safely() -> None:
    fake = _FakeClient(raises=True)
    resp = _service(_GATED_ENV, client=fake).submit(_req())
    payload = resp.model_dump()
    _assert_locked_safety(payload)
    assert payload["accepted"] is False
    assert payload["submitted_to_alpaca_paper"] is False
    assert fake.calls == 1
    # No exception detail / credential leaked.
    assert "RuntimeError" not in repr(payload)
    assert "present-secret" not in repr(payload)


def test_no_network_opened_in_blocked_or_fake_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import socket

    def _boom(*_a: object, **_k: object) -> object:
        raise AssertionError("network access attempted in sandbox submit")

    monkeypatch.setattr(socket, "socket", _boom)
    # Blocked path (no env) and gated fake path must both avoid sockets.
    assert _service({}).submit(_req()).accepted is False
    assert _service(_GATED_ENV, client=_FakeClient()).submit(_req()).accepted is True


def test_service_source_uses_paper_only_and_no_live_endpoint() -> None:
    from pathlib import Path

    source = Path(sandbox_module.__file__).read_text(encoding="utf-8")
    assert "paper=True" in source  # client is paper-only
    assert "api.alpaca.markets" not in source  # no hard-coded live endpoint
    # Lazy SDK import lives inside the gated builder/client, not at module top.
    assert "from alpaca.trading.client import TradingClient" in source


# --- route / OpenAPI -------------------------------------------------------

_PATH = "/api/alpaca-paper/order-submit-sandbox"

_VALID_BODY = {
    "symbol": "AAPL",
    "side": "BUY",
    "order_type": "market",
    "time_in_force": "day",
    "quantity": 10,
    "entry_price": 100.0,
    "stop_loss": 95.0,
    "take_profit": 110.0,
    "max_risk_pct": 0.5,
    "confirm_paper_order": True,
    "source": "manual_sandbox",
}


def test_route_is_blocked_by_default(client) -> None:
    # The process env in tests has no submit gates -> blocked, HTTP 200.
    response = client.post(_PATH, json=_VALID_BODY)
    assert response.status_code == 200
    payload = response.json()
    _assert_locked_safety(payload)
    assert payload["accepted"] is False
    assert payload["submitted_to_alpaca_paper"] is False


@pytest.mark.parametrize("method", ("get", "put", "patch", "delete"))
def test_route_rejects_non_post(client, method: str) -> None:
    assert getattr(client, method)(_PATH).status_code == 405


def test_openapi_route_is_post_only_and_no_live_paths(client) -> None:
    schema = client.app.openapi()
    paths = schema.get("paths", {})
    assert _PATH in paths
    assert set(paths[_PATH].keys()) == {"post"}
    forbidden = (
        "submit-order",
        "place-order",
        "/execute",
        "cancel-order",
        "replace-order",
    )
    bad = [p for p in paths if any(f in p for f in forbidden)]
    assert not bad, f"unexpected live-execution-shaped paths: {bad}"


def test_guardrail_allowlists_do_not_exempt_live_paths() -> None:
    from tests.app.test_paper_sandbox_guardrails import (
        SAFE_ADMIN_NON_EXECUTION_PATHS,
    )
    from tests.app.test_safety_invariants import ADMIN_NON_GET_ALLOWLIST

    live_shaped = (
        "/api/alpaca-paper/submit-order",
        "/api/alpaca-paper/place-order",
        "/api/alpaca-paper/execute",
        "/api/alpaca-paper/cancel-order",
        "/api/alpaca-paper/replace-order",
    )
    for path in live_shaped:
        assert path not in SAFE_ADMIN_NON_EXECUTION_PATHS
        assert ("POST", path) not in ADMIN_NON_GET_ALLOWLIST
