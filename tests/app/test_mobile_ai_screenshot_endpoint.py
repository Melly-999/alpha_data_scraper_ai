"""MOBILE-AI-007B — Tests for the screenshot upload analysis endpoint.

Covers the analysis-only contract: valid PNG/JPEG/WebP uploads return a
paper-only preview; oversized, wrong-type, signature-mismatched, and empty
uploads are rejected; and the response/source carry no execution surface.
"""

from __future__ import annotations

import inspect

import pytest

from app.api.routes import mobile_ai as route_module
from app.services import screenshot_analysis as service_module
from app.services.screenshot_analysis import MAX_UPLOAD_BYTES

PREVIEW_PATH = "/api/mobile/ai/screenshot/preview"

# Minimal valid magic-byte payloads (padded so signature checks pass).
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPEG_BYTES = b"\xff\xd8\xff" + b"\x00" * 32
WEBP_BYTES = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"\x00" * 32

FORBIDDEN_RESPONSE_KEYS = {
    "order_id",
    "account_id",
    "execution_id",
    "trade_id",
    "place_order",
    "broker_execute",
    "api_key",
    "secret",
    "token",
    "password",
}

FORBIDDEN_LIBRARIES = (
    "ib_insync",
    "ibapi",
    "MetaTrader5",
    "requests",
    "httpx",
    "websockets",
    "alpaca",
    "ccxt",
    "openai",
    "anthropic",
    "boto3",
)

FORBIDDEN_FUNCTION_NAMES = {
    "place_order",
    "cancel_order",
    "modify_order",
    "execute_trade",
    "submit_order",
    "broker_execute",
}


# ---------------------------------------------------------------------------
# Valid uploads
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mime,data",
    [
        ("image/png", PNG_BYTES),
        ("image/jpeg", JPEG_BYTES),
        ("image/webp", WEBP_BYTES),
    ],
)
def test_valid_upload_returns_paper_only_preview(client, mime, data) -> None:
    resp = client.post(PREVIEW_PATH, content=data, headers={"content-type": mime})
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["analysis_only"] is True
    assert body["paper_only"] is True
    assert body["live_orders_blocked"] is True
    assert body["broker_execution"] is False
    assert body["requires_human_review"] is True
    assert body["stored"] is False
    assert body["provider_used"] is False
    assert body["disclaimer"] == "Analysis only. Not financial advice."

    # Nested schemas keep their locked posture and 1% ceiling.
    assert body["paper_game_plan"]["status"] == "PAPER_ONLY"
    assert body["paper_game_plan"]["max_risk_per_trade_pct"] <= 1.0
    assert body["risk_assessment"]["risk_per_trade_pct"] <= 1.0


def test_response_has_no_execution_keys(client) -> None:
    resp = client.post(
        PREVIEW_PATH, content=PNG_BYTES, headers={"content-type": "image/png"}
    )
    assert resp.status_code == 200
    flat = resp.text.lower()
    for key in FORBIDDEN_RESPONSE_KEYS:
        assert key not in flat, f"forbidden key '{key}' present in response"


# ---------------------------------------------------------------------------
# Rejected uploads
# ---------------------------------------------------------------------------


def test_oversized_upload_rejected(client) -> None:
    big = b"\x89PNG\r\n\x1a\n" + b"\x00" * (MAX_UPLOAD_BYTES + 1)
    resp = client.post(PREVIEW_PATH, content=big, headers={"content-type": "image/png"})
    assert resp.status_code == 413


@pytest.mark.parametrize("mime", ["image/svg+xml", "application/pdf", "text/plain"])
def test_disallowed_mime_rejected(client, mime) -> None:
    resp = client.post(PREVIEW_PATH, content=PNG_BYTES, headers={"content-type": mime})
    assert resp.status_code == 415


def test_signature_mismatch_rejected(client) -> None:
    # PNG bytes declared as JPEG.
    resp = client.post(
        PREVIEW_PATH, content=PNG_BYTES, headers={"content-type": "image/jpeg"}
    )
    assert resp.status_code == 415


def test_non_image_bytes_rejected(client) -> None:
    resp = client.post(
        PREVIEW_PATH,
        content=b"%PDF-1.7 not an image",
        headers={"content-type": "image/png"},
    )
    assert resp.status_code == 415


def test_empty_body_rejected(client) -> None:
    resp = client.post(PREVIEW_PATH, content=b"", headers={"content-type": "image/png"})
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Source-level safety: no execution / network / provider surface
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("module", [route_module, service_module])
def test_modules_import_no_forbidden_libraries(module) -> None:
    src = inspect.getsource(module)
    for lib in FORBIDDEN_LIBRARIES:
        assert lib not in src, f"{module.__name__} references forbidden lib '{lib}'"


@pytest.mark.parametrize("module", [route_module, service_module])
def test_modules_define_no_execution_functions(module) -> None:
    names = {name for name, _ in inspect.getmembers(module, inspect.isfunction)}
    assert not (names & FORBIDDEN_FUNCTION_NAMES), (
        f"{module.__name__} defines execution-shaped function(s): "
        f"{names & FORBIDDEN_FUNCTION_NAMES}"
    )


def test_service_does_not_write_files() -> None:
    src = inspect.getsource(service_module)
    assert "open(" not in src
    assert '"wb"' not in src and "'wb'" not in src
