"""Read-only Supabase integration status endpoint — SUPA-004.

``GET /api/supabase/status`` returns a safe, boolean-only snapshot of whether
the backend Supabase client is configured and available. The endpoint is
GET-only by construction; no other HTTP methods are registered.

Safety invariants (structurally enforced by SupabaseClientStatus schema):
  - read_only is always True
  - dry_run is always True
  - writes_enabled is always False
  - frontend_service_key_exposed is always False

The response never carries key values — only boolean flags and a mode string.
No Supabase writes are performed. No Supabase reads are performed. No client
is instantiated by this route; ``get_supabase_status()`` reads only env var
existence via ``bool(os.getenv(...))``.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.supabase_status import SupabaseClientStatus
from app.services.supabase_client import get_supabase_status

router = APIRouter(tags=["supabase"])


@router.get("/supabase/status", response_model=SupabaseClientStatus)
def supabase_status() -> SupabaseClientStatus:
    """Return the safe Supabase client configuration status.

    GET-only. Performs no Supabase writes, no Supabase reads, and no client
    instantiation. Returns only boolean/string metadata about whether the
    backend client is configured and available. Key values are never exposed.
    """
    return get_supabase_status()
