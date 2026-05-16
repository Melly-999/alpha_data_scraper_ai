"""Tests for the SUPA-002 safe Supabase backend client foundation.

Verifies:
  1. Missing env vars          → disabled/degraded safe status.
  2. URL only                  → still degraded/disabled.
  3. URL + anon key            → configured or degraded (depends on pkg).
  4. Service role key present  → service_key_configured=True, value never
                                  returned, frontend_service_key_exposed=False,
                                  writes_enabled=False.
  5. Missing supabase pkg      → safe degraded status, no exception escapes.
  6. Fake client factory       → lazy creation without real network call.
  7. Status model rejects unsafe fields via model_validator.
  8. Service wrapper exposes no write/execution method names.
  9. No frontend files are touched by this module.
  10. Existing schema safety tests are unaffected (verified by running
      test_supabase_schema_safety.py separately — it is not re-tested here).

Design principles:
  - No real network calls. All tests are unit-level.
  - monkeypatch env vars and the importability check function.
  - The supabase package need NOT be installed for these tests to pass.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers — isolate env var state
# ---------------------------------------------------------------------------

_ENV_URL = "SUPABASE_URL"
_ENV_ANON_KEY = "SUPABASE_ANON_KEY"
_ENV_SVC_KEY = "SUPABASE_SERVICE_ROLE_KEY"


def _clear_supabase_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove all Supabase env vars so each test starts from a clean slate."""
    monkeypatch.delenv(_ENV_URL, raising=False)
    monkeypatch.delenv(_ENV_ANON_KEY, raising=False)
    monkeypatch.delenv(_ENV_SVC_KEY, raising=False)


def _patch_importable(monkeypatch: pytest.MonkeyPatch, *, available: bool) -> None:
    """Monkeypatch the importability check without touching sys.modules."""
    import app.services.supabase_client as svc

    monkeypatch.setattr(svc, "_supabase_importable", lambda: available)


# ---------------------------------------------------------------------------
# 1. Missing env vars → disabled/degraded safe status
# ---------------------------------------------------------------------------


def test_no_env_vars_returns_disabled_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    _patch_importable(monkeypatch, available=False)

    status = get_supabase_status()

    assert status.configured is False
    assert status.available is False
    assert status.degraded is True
    assert status.url_configured is False
    assert status.mode in ("disabled", "degraded")


def test_no_env_vars_safety_flags_intact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    _patch_importable(monkeypatch, available=False)

    status = get_supabase_status()

    assert status.read_only is True
    assert status.dry_run is True
    assert status.writes_enabled is False
    assert status.frontend_service_key_exposed is False


def test_no_env_vars_is_configured_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import is_supabase_configured

    _clear_supabase_env(monkeypatch)
    _patch_importable(monkeypatch, available=False)

    assert is_supabase_configured() is False


def test_no_env_vars_client_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_safe_supabase_client

    _clear_supabase_env(monkeypatch)
    _patch_importable(monkeypatch, available=False)

    assert get_safe_supabase_client() is None


# ---------------------------------------------------------------------------
# 2. URL only → still degraded/disabled
# ---------------------------------------------------------------------------


def test_url_only_returns_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    _patch_importable(monkeypatch, available=True)

    status = get_supabase_status()

    assert status.configured is False
    assert status.available is False
    assert status.degraded is True
    assert status.url_configured is True
    assert status.anon_key_configured is False
    assert status.mode == "disabled"


def test_url_only_safety_flags_intact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")

    status = get_supabase_status()

    assert status.read_only is True
    assert status.dry_run is True
    assert status.writes_enabled is False
    assert status.frontend_service_key_exposed is False


# ---------------------------------------------------------------------------
# 3. URL + anon key → configured or degraded depending on dependency
# ---------------------------------------------------------------------------


def test_url_and_anon_key_with_pkg_available_returns_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key-placeholder")
    _patch_importable(monkeypatch, available=True)

    status = get_supabase_status()

    assert status.configured is True
    assert status.available is True
    assert status.degraded is False
    assert status.mode == "configured"


def test_url_and_anon_key_without_pkg_returns_degraded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key-placeholder")
    _patch_importable(monkeypatch, available=False)

    status = get_supabase_status()

    assert status.configured is True
    assert status.available is False
    assert status.degraded is True
    assert status.mode == "degraded"


def test_configured_status_never_exposes_key_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "super-secret-anon-key-value")
    _patch_importable(monkeypatch, available=True)

    status = get_supabase_status()
    status_dict = status.model_dump()

    # The actual key value must not appear anywhere in the serialised status
    assert "super-secret-anon-key-value" not in str(status_dict)
    assert "super-secret-anon-key-value" not in str(status)


# ---------------------------------------------------------------------------
# 4. Service role key present → correctly reflected, value never returned
# ---------------------------------------------------------------------------


def test_service_key_configured_flag_is_true_when_env_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key")
    monkeypatch.setenv(_ENV_SVC_KEY, "service-role-key-value")
    _patch_importable(monkeypatch, available=True)

    status = get_supabase_status()

    assert status.service_key_configured is True


def test_service_key_value_never_returned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key")
    monkeypatch.setenv(_ENV_SVC_KEY, "very-secret-service-role-key-xyz")
    _patch_importable(monkeypatch, available=True)

    status = get_supabase_status()
    serialised = str(status.model_dump())

    assert "very-secret-service-role-key-xyz" not in serialised
    assert "very-secret-service-role-key-xyz" not in str(status)


def test_service_key_present_writes_still_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key")
    monkeypatch.setenv(_ENV_SVC_KEY, "service-role-key-value")
    _patch_importable(monkeypatch, available=True)

    status = get_supabase_status()

    assert status.writes_enabled is False
    assert status.frontend_service_key_exposed is False


# ---------------------------------------------------------------------------
# 5. Missing supabase dependency → safe degraded, no exception escapes
# ---------------------------------------------------------------------------


def test_missing_supabase_package_returns_degraded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key")
    _patch_importable(monkeypatch, available=False)

    # Must not raise
    status = get_supabase_status()

    assert status.mode == "degraded"
    assert status.available is False
    assert status.degraded is True
    assert "not installed" in status.reason.lower()


def test_missing_package_is_configured_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import is_supabase_configured

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key")
    _patch_importable(monkeypatch, available=False)

    assert is_supabase_configured() is False


def test_missing_package_client_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_safe_supabase_client

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key")
    _patch_importable(monkeypatch, available=False)

    assert get_safe_supabase_client() is None


# ---------------------------------------------------------------------------
# 6. Fake client factory → lazy creation without network
# ---------------------------------------------------------------------------


def test_fake_factory_creates_client_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_safe_supabase_client

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key")
    _patch_importable(monkeypatch, available=True)

    calls: list[tuple[str, str]] = []

    def _fake_factory(url: str, anon_key: str) -> dict[str, str]:
        calls.append((url, anon_key))
        return {"url": url, "mode": "fake"}

    client = get_safe_supabase_client(_factory=_fake_factory)

    assert client is not None
    assert client["mode"] == "fake"
    assert len(calls) == 1
    assert calls[0][0] == "https://example.supabase.co"


def test_fake_factory_not_called_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_safe_supabase_client

    _clear_supabase_env(monkeypatch)
    _patch_importable(monkeypatch, available=False)

    calls: list[Any] = []

    def _fake_factory(url: str, anon_key: str) -> dict[str, str]:
        calls.append((url, anon_key))
        return {}

    result = get_safe_supabase_client(_factory=_fake_factory)

    assert result is None
    assert len(calls) == 0


def test_factory_receives_url_not_service_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_safe_supabase_client

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_ANON_KEY, "anon-key-value")
    monkeypatch.setenv(_ENV_SVC_KEY, "service-role-secret")
    _patch_importable(monkeypatch, available=True)

    received: list[tuple[str, str]] = []

    def _fake_factory(url: str, anon_key: str) -> dict[str, str]:
        received.append((url, anon_key))
        return {}

    get_safe_supabase_client(_factory=_fake_factory)

    assert len(received) == 1
    _, received_key = received[0]
    # Factory must receive the anon key, never the service role key value
    assert received_key == "anon-key-value"
    assert received_key != "service-role-secret"


# ---------------------------------------------------------------------------
# 7. Status model rejects unsafe field values (model_validator enforcement)
# ---------------------------------------------------------------------------


def test_status_model_rejects_read_only_false() -> None:
    from app.schemas.supabase_status import SupabaseClientStatus

    with pytest.raises(ValidationError, match="read_only"):
        SupabaseClientStatus(
            configured=False,
            available=False,
            degraded=True,
            url_configured=False,
            anon_key_configured=False,
            service_key_configured=False,
            mode="disabled",
            reason="test",
            read_only=False,  # forbidden
        )


def test_status_model_rejects_dry_run_false() -> None:
    from app.schemas.supabase_status import SupabaseClientStatus

    with pytest.raises(ValidationError, match="dry_run"):
        SupabaseClientStatus(
            configured=False,
            available=False,
            degraded=True,
            url_configured=False,
            anon_key_configured=False,
            service_key_configured=False,
            mode="disabled",
            reason="test",
            dry_run=False,  # forbidden
        )


def test_status_model_rejects_writes_enabled_true() -> None:
    from app.schemas.supabase_status import SupabaseClientStatus

    with pytest.raises(ValidationError, match="writes_enabled"):
        SupabaseClientStatus(
            configured=False,
            available=False,
            degraded=True,
            url_configured=False,
            anon_key_configured=False,
            service_key_configured=False,
            mode="disabled",
            reason="test",
            writes_enabled=True,  # forbidden
        )


def test_status_model_rejects_frontend_service_key_exposed_true() -> None:
    from app.schemas.supabase_status import SupabaseClientStatus

    with pytest.raises(ValidationError, match="frontend_service_key_exposed"):
        SupabaseClientStatus(
            configured=False,
            available=False,
            degraded=True,
            url_configured=False,
            anon_key_configured=False,
            service_key_configured=False,
            mode="disabled",
            reason="test",
            frontend_service_key_exposed=True,  # forbidden
        )


def test_status_model_rejects_extra_fields() -> None:
    from app.schemas.supabase_status import SupabaseClientStatus

    with pytest.raises(ValidationError):
        SupabaseClientStatus(
            configured=False,
            available=False,
            degraded=True,
            url_configured=False,
            anon_key_configured=False,
            service_key_configured=False,
            mode="disabled",
            reason="test",
            password="hunter2",  # extra forbidden field
        )


def test_status_model_dict_contains_no_sensitive_field_names() -> None:
    from app.schemas.supabase_status import SupabaseClientStatus

    status = SupabaseClientStatus(
        configured=False,
        available=False,
        degraded=True,
        url_configured=False,
        anon_key_configured=False,
        service_key_configured=False,
        mode="disabled",
        reason="no env vars",
    )
    field_names = set(status.model_dump().keys())

    forbidden_field_names = {
        "password",
        "credential",
        "account_id",
        "order_id",
        "execution_id",
        "trade_id",
        "api_key_value",
        "anon_key_value",
        "service_key_value",
        "service_role_key",
    }
    overlap = field_names & forbidden_field_names
    assert not overlap, (
        f"Status model contains forbidden field names: {overlap}"
    )


# ---------------------------------------------------------------------------
# 8. Service wrapper exposes no write/execution method names
# ---------------------------------------------------------------------------


def test_service_module_has_no_write_method_names() -> None:
    import app.services.supabase_client as svc

    forbidden_names = {
        "insert",
        "upsert",
        "update",
        "delete",
        "write",
        "execute",
        "place_order",
        "broker_execute",
        "cancel_order",
        "modify_order",
    }

    public_names = {
        name
        for name, obj in inspect.getmembers(svc)
        if not name.startswith("_") and callable(obj)
        and inspect.getmodule(obj) is svc  # only functions defined in this module
    }

    overlap = public_names & forbidden_names
    assert not overlap, (
        f"Service module exposes forbidden write/execution method names: {overlap}"
    )


def test_service_public_api_is_read_only_named() -> None:
    import app.services.supabase_client as svc

    expected_public = {"get_supabase_status", "is_supabase_configured", "get_safe_supabase_client"}
    actual_public = {
        name
        for name, obj in inspect.getmembers(svc)
        if not name.startswith("_") and callable(obj)
        and inspect.getmodule(obj) is svc
    }
    # All expected public functions must be present
    for name in expected_public:
        assert name in actual_public, f"Expected public function '{name}' not found"


# ---------------------------------------------------------------------------
# 9. No frontend files touched
# ---------------------------------------------------------------------------


def test_supabase_client_module_has_no_frontend_imports() -> None:
    import ast

    svc_path = REPO_ROOT / "app" / "services" / "supabase_client.py"
    tree = ast.parse(svc_path.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert not name.startswith("frontend"), (
                    f"supabase_client.py imports from frontend: {name}"
                )


def test_schema_module_has_no_frontend_imports() -> None:
    import ast

    schema_path = REPO_ROOT / "app" / "schemas" / "supabase_status.py"
    tree = ast.parse(schema_path.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert not name.startswith("frontend"), (
                    f"supabase_status.py imports from frontend: {name}"
                )


# ---------------------------------------------------------------------------
# 10. Safety flags always hold across all modes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url,anon_key,pkg_available",
    [
        ("", "", False),
        ("https://example.supabase.co", "", False),
        ("https://example.supabase.co", "key", False),
        ("https://example.supabase.co", "key", True),
    ],
)
def test_safety_flags_always_true_across_modes(
    monkeypatch: pytest.MonkeyPatch,
    url: str,
    anon_key: str,
    pkg_available: bool,
) -> None:
    from app.services.supabase_client import get_supabase_status

    _clear_supabase_env(monkeypatch)
    if url:
        monkeypatch.setenv(_ENV_URL, url)
    if anon_key:
        monkeypatch.setenv(_ENV_ANON_KEY, anon_key)
    _patch_importable(monkeypatch, available=pkg_available)

    status = get_supabase_status()

    assert status.read_only is True, "read_only must always be True"
    assert status.dry_run is True, "dry_run must always be True"
    assert status.writes_enabled is False, "writes_enabled must always be False"
    assert status.frontend_service_key_exposed is False, (
        "frontend_service_key_exposed must always be False"
    )


# ---------------------------------------------------------------------------
# 11. get_safe_supabase_write_client — backend-only write client (Scope B)
# ---------------------------------------------------------------------------


def test_get_safe_supabase_write_client_returns_none_when_service_key_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_safe_supabase_write_client

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    # SUPABASE_SERVICE_ROLE_KEY deliberately absent
    _patch_importable(monkeypatch, available=True)

    assert get_safe_supabase_write_client() is None


def test_get_safe_supabase_write_client_returns_client_when_fully_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.supabase_client import get_safe_supabase_write_client

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_SVC_KEY, "service-role-key-placeholder")
    _patch_importable(monkeypatch, available=True)

    calls: list[tuple[str, str]] = []

    def _fake_write_factory(url: str, key: str) -> dict[str, str]:
        calls.append((url, key))
        return {"url": url, "mode": "write-fake"}

    client = get_safe_supabase_write_client(_factory=_fake_write_factory)

    assert client is not None
    assert client["mode"] == "write-fake"
    assert len(calls) == 1
    assert calls[0][0] == "https://example.supabase.co"


def test_get_safe_supabase_write_client_does_not_expose_service_key_in_failure_output(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Service role key value must never appear in logs when client is unavailable."""
    import logging

    from app.services.supabase_client import get_safe_supabase_write_client

    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(_ENV_URL, "https://example.supabase.co")
    monkeypatch.setenv(_ENV_SVC_KEY, "super-secret-svc-key-xyz-abc")
    _patch_importable(monkeypatch, available=False)  # package unavailable → returns None

    with caplog.at_level(logging.DEBUG):
        result = get_safe_supabase_write_client()

    assert result is None
    assert "super-secret-svc-key-xyz-abc" not in caplog.text
