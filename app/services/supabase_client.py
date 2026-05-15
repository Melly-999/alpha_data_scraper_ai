"""Safe backend Supabase client foundation with degraded fallback.

SUPA-002 scope — this module:
  - Reads three env vars to determine configuration status.
  - Returns a safe SupabaseClientStatus without ever exposing key values.
  - Provides a lazy client factory that degrades safely when the supabase
    package is missing or env vars are absent.
  - Does NOT write to any Supabase table (deferred to SUPA-003).
  - Does NOT expose any endpoint routes (deferred to SUPA-004).
  - Does NOT add frontend code or expose the service role key.

Env vars consumed (all optional — absence yields degraded/disabled status):
  SUPABASE_URL             — project REST URL
  SUPABASE_ANON_KEY        — public anon key (safe for read-only frontend use)
  SUPABASE_SERVICE_ROLE_KEY — backend-only write key (value never returned)

Public API (no write methods):
  get_supabase_status()    -> SupabaseClientStatus
  is_supabase_configured() -> bool
  get_safe_supabase_client(*, _factory=None) -> object | None
"""

from __future__ import annotations

import os
from typing import Any, Callable

from app.schemas.supabase_status import SupabaseClientStatus

# Env var names — referenced by name only; values are never stored or returned.
_ENV_URL = "SUPABASE_URL"
_ENV_ANON_KEY = "SUPABASE_ANON_KEY"
_ENV_SERVICE_ROLE_KEY = "SUPABASE_SERVICE_ROLE_KEY"


def _supabase_importable() -> bool:
    """Return True if the supabase Python package can be imported.

    Isolated as a named function so tests can monkeypatch it cleanly
    without manipulating sys.modules directly.
    """
    try:
        import supabase  # type: ignore  # noqa: F401

        return True
    except ImportError:
        return False


def get_supabase_status() -> SupabaseClientStatus:
    """Return a safe status snapshot of the Supabase client configuration.

    Never exposes key values. Falls back to a safe disabled/degraded status
    when env vars are absent or the supabase package is unavailable.
    All safety invariants (read_only, dry_run, writes_enabled=False,
    frontend_service_key_exposed=False) are structurally enforced by
    SupabaseClientStatus's model_validator.
    """
    url_configured = bool(os.getenv(_ENV_URL))
    anon_key_configured = bool(os.getenv(_ENV_ANON_KEY))
    service_key_configured = bool(os.getenv(_ENV_SERVICE_ROLE_KEY))

    if not url_configured:
        return SupabaseClientStatus(
            configured=False,
            available=False,
            degraded=True,
            url_configured=False,
            anon_key_configured=anon_key_configured,
            service_key_configured=service_key_configured,
            mode="disabled",
            reason="SUPABASE_URL is not configured",
        )

    if not anon_key_configured:
        return SupabaseClientStatus(
            configured=False,
            available=False,
            degraded=True,
            url_configured=True,
            anon_key_configured=False,
            service_key_configured=service_key_configured,
            mode="disabled",
            reason="SUPABASE_ANON_KEY is not configured",
        )

    if not _supabase_importable():
        return SupabaseClientStatus(
            configured=True,
            available=False,
            degraded=True,
            url_configured=True,
            anon_key_configured=True,
            service_key_configured=service_key_configured,
            mode="degraded",
            reason="supabase Python package is not installed",
        )

    return SupabaseClientStatus(
        configured=True,
        available=True,
        degraded=False,
        url_configured=True,
        anon_key_configured=True,
        service_key_configured=service_key_configured,
        mode="configured",
        reason="Supabase client is configured and available",
    )


def is_supabase_configured() -> bool:
    """Return True only when the client is fully configured and available."""
    status = get_supabase_status()
    return status.configured and status.available


def get_safe_supabase_client(
    *,
    _factory: Callable[[str, str], Any] | None = None,
) -> Any | None:
    """Return a Supabase client instance or None if not configured/available.

    This function does NOT make write calls or start realtime subscriptions.
    It returns an instantiated client object only; actual usage (read queries,
    audit writes) is deferred to SUPA-003+.

    Parameters
    ----------
    _factory:
        Injectable callable ``(url: str, anon_key: str) -> client`` used by
        tests to avoid real network calls. Pass None (default) to use the
        real supabase.create_client.
    """
    status = get_supabase_status()
    if not status.configured or not status.available:
        return None

    url = os.getenv(_ENV_URL, "")
    anon_key = os.getenv(_ENV_ANON_KEY, "")

    if _factory is not None:
        return _factory(url, anon_key)

    try:
        from supabase import create_client  # type: ignore

        return create_client(url, anon_key)
    except Exception:
        return None
