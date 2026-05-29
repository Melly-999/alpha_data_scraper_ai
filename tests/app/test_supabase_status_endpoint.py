"""Tests for SUPA-004: GET /api/supabase/status endpoint.

All Supabase interaction is eliminated through monkeypatching of:
  - environment variables (os.getenv reads in supabase_client.py)
  - _supabase_importable() (importability flag)

No real network calls. No real Supabase client instantiation.

Test categories:
  1.  HTTP contract — GET returns 200, mutating methods return 405
  2.  Response structure — all required fields present, no extra fields
  3.  Safety invariants — read_only/dry_run/writes_enabled/frontend flags
  4.  No credential leakage — response body carries no key values
  5.  Degraded path — response when env vars absent
  6.  Configured path — response when all env vars present and package mocked
  7.  OpenAPI / route safety — endpoint appears in schema, not a forbidden path
"""

from __future__ import annotations

_STATUS_PATH = "/api/supabase/status"

# ---------------------------------------------------------------------------
# Category 1 — HTTP contract
# ---------------------------------------------------------------------------


def test_supabase_status_get_returns_200(client) -> None:
    response = client.get(_STATUS_PATH)
    assert response.status_code == 200


def test_supabase_status_post_returns_405(client) -> None:
    response = client.post(_STATUS_PATH, json={})
    assert response.status_code == 405


def test_supabase_status_put_returns_405(client) -> None:
    response = client.put(_STATUS_PATH, json={})
    assert response.status_code == 405


def test_supabase_status_patch_returns_405(client) -> None:
    response = client.patch(_STATUS_PATH, json={})
    assert response.status_code == 405


def test_supabase_status_delete_returns_405(client) -> None:
    response = client.delete(_STATUS_PATH)
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# Category 2 — Response structure
# ---------------------------------------------------------------------------

_REQUIRED_FIELDS = {
    "configured",
    "available",
    "degraded",
    "url_configured",
    "anon_key_configured",
    "service_key_configured",
    "mode",
    "reason",
    "read_only",
    "dry_run",
    "writes_enabled",
    "frontend_service_key_exposed",
}


def test_supabase_status_response_has_all_required_fields(client) -> None:
    payload = client.get(_STATUS_PATH).json()
    for field in _REQUIRED_FIELDS:
        assert field in payload, f"Missing required field: {field}"


def test_supabase_status_response_has_no_extra_fields(client) -> None:
    payload = client.get(_STATUS_PATH).json()
    extra = set(payload.keys()) - _REQUIRED_FIELDS
    assert extra == set(), f"Unexpected extra fields in response: {extra}"


def test_supabase_status_mode_is_valid_literal(client) -> None:
    payload = client.get(_STATUS_PATH).json()
    assert payload["mode"] in {"disabled", "configured", "degraded"}


def test_supabase_status_reason_is_non_empty_string(client) -> None:
    payload = client.get(_STATUS_PATH).json()
    assert isinstance(payload["reason"], str)
    assert len(payload["reason"]) > 0


# ---------------------------------------------------------------------------
# Category 3 — Safety invariants always true/false
# ---------------------------------------------------------------------------


def test_supabase_status_read_only_always_true(client) -> None:
    payload = client.get(_STATUS_PATH).json()
    assert payload["read_only"] is True


def test_supabase_status_dry_run_always_true(client) -> None:
    payload = client.get(_STATUS_PATH).json()
    assert payload["dry_run"] is True


def test_supabase_status_writes_enabled_always_false(client) -> None:
    payload = client.get(_STATUS_PATH).json()
    assert payload["writes_enabled"] is False


def test_supabase_status_frontend_service_key_exposed_always_false(client) -> None:
    payload = client.get(_STATUS_PATH).json()
    assert payload["frontend_service_key_exposed"] is False


# ---------------------------------------------------------------------------
# Category 4 — No credential leakage in response body
# ---------------------------------------------------------------------------

_CREDENTIAL_PATTERNS = [
    "eyJ",  # JWT prefix (anon / service_role key values start with this)
    "service_role_key",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_URL_VALUE",
]


def test_supabase_status_response_body_contains_no_key_values(
    client, monkeypatch
) -> None:
    """Even when env vars are set, the response body must not expose their values."""
    import app.services.supabase_client as svc

    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "eyJFAKE_ANON_KEY_VALUE")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "eyJFAKE_SERVICE_ROLE_KEY_VALUE")
    monkeypatch.setattr(svc, "_supabase_importable", lambda: True)

    response = client.get(_STATUS_PATH)
    body = response.text

    assert "eyJFAKE_ANON_KEY_VALUE" not in body
    assert "eyJFAKE_SERVICE_ROLE_KEY_VALUE" not in body
    # The URL itself should also not appear as a value in the response
    assert "example.supabase.co" not in body


def test_supabase_status_service_key_configured_is_boolean_not_value(
    client, monkeypatch
) -> None:
    """service_key_configured must be a bool, never the key string itself."""
    import app.services.supabase_client as svc

    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon-key-placeholder")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key-placeholder")
    monkeypatch.setattr(svc, "_supabase_importable", lambda: True)

    payload = client.get(_STATUS_PATH).json()
    assert isinstance(payload["service_key_configured"], bool)
    assert payload["service_key_configured"] is True
    # The value must NOT contain the key string
    assert "service-role-key-placeholder" not in str(payload)


# ---------------------------------------------------------------------------
# Category 5 — Degraded path (env vars absent)
# ---------------------------------------------------------------------------


def test_supabase_status_disabled_when_no_url(client, monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    payload = client.get(_STATUS_PATH).json()
    assert payload["configured"] is False
    assert payload["available"] is False
    assert payload["degraded"] is True
    assert payload["mode"] == "disabled"
    assert payload["url_configured"] is False


def test_supabase_status_disabled_when_url_set_but_no_anon_key(
    client, monkeypatch
) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    payload = client.get(_STATUS_PATH).json()
    assert payload["configured"] is False
    assert payload["available"] is False
    assert payload["mode"] == "disabled"
    assert payload["url_configured"] is True
    assert payload["anon_key_configured"] is False


def test_supabase_status_degraded_when_env_vars_set_but_package_missing(
    client, monkeypatch
) -> None:
    import app.services.supabase_client as svc

    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon-placeholder")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.setattr(svc, "_supabase_importable", lambda: False)

    payload = client.get(_STATUS_PATH).json()
    assert payload["configured"] is True
    assert payload["available"] is False
    assert payload["degraded"] is True
    assert payload["mode"] == "degraded"


# ---------------------------------------------------------------------------
# Category 6 — Configured path (all vars set + package mocked as importable)
# ---------------------------------------------------------------------------


def test_supabase_status_configured_when_all_vars_and_package_available(
    client, monkeypatch
) -> None:
    import app.services.supabase_client as svc

    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon-placeholder")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "svc-placeholder")
    monkeypatch.setattr(svc, "_supabase_importable", lambda: True)

    payload = client.get(_STATUS_PATH).json()
    assert payload["configured"] is True
    assert payload["available"] is True
    assert payload["degraded"] is False
    assert payload["mode"] == "configured"
    assert payload["url_configured"] is True
    assert payload["anon_key_configured"] is True
    assert payload["service_key_configured"] is True
    # Safety invariants still hold in configured mode
    assert payload["read_only"] is True
    assert payload["writes_enabled"] is False
    assert payload["frontend_service_key_exposed"] is False


# ---------------------------------------------------------------------------
# Category 7 — OpenAPI / route safety
# ---------------------------------------------------------------------------


def test_supabase_status_appears_in_openapi_schema(client) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema.get("paths", {})
    assert (
        _STATUS_PATH in paths
    ), f"{_STATUS_PATH} not found in OpenAPI schema paths: {list(paths.keys())}"


def test_supabase_status_openapi_entry_is_get_only(client) -> None:
    schema = client.get("/openapi.json").json()
    methods = set(schema["paths"].get(_STATUS_PATH, {}).keys())
    assert methods == {"get"}, f"Expected only GET on {_STATUS_PATH}, found: {methods}"


def test_supabase_status_path_contains_no_forbidden_execution_segment(
    client,
) -> None:
    forbidden_segments = {
        "execute",
        "order",
        "trade",
        "broker",
        "live",
        "autotrade",
        "place",
        "submit",
        "cancel",
        "connect",
    }
    path_segments = set(_STATUS_PATH.strip("/").split("/"))
    overlap = forbidden_segments & path_segments
    assert overlap == set(), f"Route path contains forbidden segment(s): {overlap}"
