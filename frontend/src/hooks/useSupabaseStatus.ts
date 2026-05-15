// Read-only Supabase connection status hook — SUPA-005.
//
// Polls GET /api/supabase/status every 30 seconds using the established
// apiGet helper and usePollingResource infrastructure. Returns only
// boolean flags and a human-readable mode/reason string. Never stores,
// logs, or forwards key values. No writes. No mutations. No broker calls.

import { useCallback } from "react";

import { apiGet } from "../lib/api";
import { usePollingResource } from "./usePollingResource";

/**
 * Safe status snapshot of the backend Supabase client.
 *
 * Mirrors the 12-field SupabaseClientStatus Pydantic schema from
 * app/schemas/supabase_status.py exactly. No credential values are
 * ever carried — only boolean presence flags and a mode string.
 *
 * The four safety fields are typed as TypeScript literals so the
 * compiler enforces the same invariants the backend model_validator
 * enforces at runtime:
 *   read_only              : true   (always)
 *   dry_run                : true   (always)
 *   writes_enabled         : false  (always)
 *   frontend_service_key_exposed : false  (always)
 */
export interface SupabaseStatus {
  configured: boolean;
  available: boolean;
  degraded: boolean;
  url_configured: boolean;
  anon_key_configured: boolean;
  service_key_configured: boolean;
  mode: "disabled" | "configured" | "degraded";
  reason: string;
  read_only: true;
  dry_run: true;
  writes_enabled: false;
  frontend_service_key_exposed: false;
}

const SUPABASE_STATUS_INTERVAL_MS = 30_000;

/**
 * Polls GET /api/supabase/status every 30 seconds.
 *
 * Returns { data, loading, error, lastUpdatedAt } via usePollingResource.
 * GET-only. No side effects beyond the polling fetch.
 */
export function useSupabaseStatus() {
  const loader = useCallback(
    () => apiGet<SupabaseStatus>("/supabase/status"),
    [],
  );
  return usePollingResource(loader, SUPABASE_STATUS_INTERVAL_MS);
}
