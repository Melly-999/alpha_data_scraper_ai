"""Tests for read-only Neon memory endpoints."""

from __future__ import annotations

from typing import Any


def _assert_safety_flags(payload: dict[str, Any]) -> None:
    assert payload["autotrade"] is False
    assert payload["dry_run"] is True
    assert payload["read_only"] is True
    assert payload["live_orders_blocked"] is True
    assert payload["execution_enabled"] is False
    assert payload["paper_only"] is True
    assert payload["requires_human_review"] is True


def _assert_no_secret_fields(payload: Any) -> None:
    banned_keys = {"account_id", "api_key", "api_secret", "token", "password", "secret"}
    if isinstance(payload, dict):
        assert not (banned_keys & set(payload))
        for value in payload.values():
            _assert_no_secret_fields(value)
    elif isinstance(payload, list):
        for value in payload:
            _assert_no_secret_fields(value)


def test_neon_memory_status_is_get_only_and_safe_without_database(client, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    response = client.get("/api/neon-memory/status")
    data = response.json()

    assert response.status_code == 200
    _assert_safety_flags(data)
    assert data["service_name"] == "neon-memory"
    assert data["database_configured"] is False
    assert data["database_reachable"] is False
    assert data["availability"] == "degraded"
    _assert_no_secret_fields(data)


def test_neon_memory_summary_is_get_only_and_safe_without_database(client, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    response = client.get("/api/neon-memory/summary")
    data = response.json()

    assert response.status_code == 200
    _assert_safety_flags(data)
    assert data["service_name"] == "neon-memory"
    assert data["tables"] == []
    _assert_no_secret_fields(data)


def test_neon_memory_status_degrades_when_psycopg_driver_missing(client, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/neondb")
    monkeypatch.setattr("app.services.neon_memory.is_driver_available", lambda: False)

    response = client.get("/api/neon-memory/status")
    data = response.json()

    assert response.status_code == 200
    _assert_safety_flags(data)
    assert data["availability"] == "degraded"
    assert data["source"] == "driver-missing"
    assert data["database_reachable"] is False
    assert "psycopg driver is not installed" in data["message"]
    _assert_no_secret_fields(data)


def test_neon_memory_defaults_do_not_expose_account_identifiers(client, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("ACE_NAMESPACE", raising=False)

    response = client.get("/api/neon-memory/status")
    data = response.json()

    assert response.status_code == 200
    assert data["neon_project_id"] == "example-project"
    assert data["ace_namespace"] == "example-workspace"


def test_openapi_has_no_forbidden_methods_for_neon_memory_paths(client):
    openapi = client.app.openapi()
    paths = openapi["paths"]
    for path, methods in paths.items():
        if path.startswith("/api/neon-memory"):
            assert set(methods) == {"get"}
