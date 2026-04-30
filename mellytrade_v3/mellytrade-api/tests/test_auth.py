from __future__ import annotations

import sys

import pytest

HEADERS = {"X-API-Key": "test-key"}


def test_missing_api_key_returns_401(client):
    """Request without any X-API-Key header is rejected with 401."""
    resp = client.get("/signals")
    assert resp.status_code == 401
    body = resp.json()
    assert body["status"] == "rejected"
    assert body["reason"] == "unauthorized"
    assert body["detail"] == "invalid_or_missing_api_key"


def test_wrong_api_key_returns_401(client):
    """Request with an incorrect X-API-Key is rejected with 401."""
    resp = client.get("/signals", headers={"X-API-Key": "totally-wrong"})
    assert resp.status_code == 401
    body = resp.json()
    assert body["status"] == "rejected"
    assert body["reason"] == "unauthorized"
    assert body["detail"] == "invalid_or_missing_api_key"


def test_empty_header_value_returns_401(client):
    """Empty X-API-Key string is treated the same as missing."""
    resp = client.get("/signals", headers={"X-API-Key": ""})
    assert resp.status_code == 401
    body = resp.json()
    assert body["status"] == "rejected"


def test_correct_api_key_is_allowed(client):
    """Request with the correct X-API-Key passes authentication."""
    resp = client.get("/signals", headers=HEADERS)
    assert resp.status_code == 200


def test_health_requires_no_auth(client):
    """GET /health must remain publicly accessible without a key."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_audit_requires_api_key(client):
    """GET /audit must require authentication."""
    resp = client.get("/audit")
    assert resp.status_code == 401


def test_risk_config_requires_api_key(client):
    """GET /risk/config must require authentication."""
    resp = client.get("/risk/config")
    assert resp.status_code == 401


def test_empty_fastapi_key_raises_at_settings(monkeypatch, tmp_path):
    """get_settings() must raise ValueError when FASTAPI_KEY is empty."""
    # Override env: autouse fixture already set FASTAPI_KEY=test-key;
    # we override it to "" and force a fresh module import.
    monkeypatch.setenv("FASTAPI_KEY", "")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")

    for mod in list(sys.modules):
        if mod == "app" or mod.startswith("app."):
            del sys.modules[mod]

    from app.config import get_settings

    with pytest.raises(ValueError, match="FASTAPI_KEY"):
        get_settings()

    # Restore clean state for subsequent tests
    for mod in list(sys.modules):
        if mod == "app" or mod.startswith("app."):
            del sys.modules[mod]
