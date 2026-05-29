"""Pydantic schema for the safe Supabase client status report.

This schema is deliberately strict (``extra="forbid"``) and cannot grow
new fields silently. It carries only boolean/string metadata about whether
the backend Supabase client is configured and reachable. It never carries
key values, credentials, account IDs, or any execution-shaped field.

Safety invariants enforced by model_validator:
  - read_only is always True
  - dry_run is always True
  - writes_enabled is always False (no DB writes in SUPA-002)
  - frontend_service_key_exposed is always False
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SupabaseClientStatus(BaseModel):
    """Safe status snapshot of the backend Supabase client.

    Returned by ``get_supabase_status()`` in ``app.services.supabase_client``.
    Never includes key values, credentials, or any field that could reveal
    a service role key to the frontend or any API consumer.
    """

    model_config = ConfigDict(extra="forbid")

    configured: bool = Field(
        ...,
        description=(
            "True when both SUPABASE_URL and SUPABASE_ANON_KEY are set "
            "and the supabase Python package is importable."
        ),
    )
    available: bool = Field(
        ...,
        description=(
            "True when the client can be instantiated. May be False even "
            "when configured=True if the dependency is missing."
        ),
    )
    degraded: bool = Field(
        ...,
        description=(
            "True when the client is not fully operational — either because "
            "env vars are absent or the supabase package is unavailable."
        ),
    )
    url_configured: bool = Field(
        ...,
        description="True when SUPABASE_URL env var is non-empty.",
    )
    anon_key_configured: bool = Field(
        ...,
        description=(
            "True when SUPABASE_ANON_KEY env var is non-empty. "
            "The key value itself is never stored or returned."
        ),
    )
    service_key_configured: bool = Field(
        ...,
        description=(
            "True when SUPABASE_SERVICE_ROLE_KEY env var is non-empty. "
            "The key value is never stored or returned. "
            "The service role key is a backend-only secret — "
            "it must never be exposed to the frontend."
        ),
    )
    mode: Literal["disabled", "configured", "degraded"] = Field(
        ...,
        description=(
            "'disabled' when required env vars are absent; "
            "'degraded' when vars are present but dependency is missing; "
            "'configured' when fully operational."
        ),
    )
    reason: str = Field(
        ...,
        min_length=1,
        description="Human-readable explanation of the current mode.",
    )

    # -----------------------------------------------------------------------
    # Safety invariants — these fields are structurally locked in SUPA-002.
    # They are not configurable at call time; the model_validator enforces them.
    # -----------------------------------------------------------------------

    read_only: bool = Field(
        default=True,
        description=(
            "Always True in SUPA-002. The Supabase client layer is "
            "read-only — no audit writes are implemented in this task."
        ),
    )
    dry_run: bool = Field(
        default=True,
        description="Always True — backend Supabase layer is dry-run only.",
    )
    writes_enabled: bool = Field(
        default=False,
        description=(
            "Always False in SUPA-002. Write capability is deferred to "
            "SUPA-003 and will remain gated behind explicit configuration."
        ),
    )
    frontend_service_key_exposed: bool = Field(
        default=False,
        description=(
            "Always False. The service role key must never be sent to the "
            "frontend. This flag is a structural assertion, not a config option."
        ),
    )

    @model_validator(mode="after")
    def _enforce_safety_invariants(self) -> "SupabaseClientStatus":
        if self.read_only is not True:
            raise ValueError("read_only must always be True for SupabaseClientStatus")
        if self.dry_run is not True:
            raise ValueError("dry_run must always be True for SupabaseClientStatus")
        if self.writes_enabled is not False:
            raise ValueError(
                "writes_enabled must always be False in SUPA-002 — "
                "write capability is deferred to SUPA-003"
            )
        if self.frontend_service_key_exposed is not False:
            raise ValueError(
                "frontend_service_key_exposed must always be False — "
                "the service role key must never reach the frontend"
            )
        return self
