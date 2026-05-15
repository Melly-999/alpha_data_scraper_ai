// Read-only Supabase connection status card — SUPA-005.
//
// Display-only component. No buttons, no onClick handlers, no forms,
// no toggles, no execution controls, no broker controls.
// Key values are never rendered — only boolean flags and human-readable
// mode/reason text received from useSupabaseStatus().
//
// SUPA-009: stale indicator added to the "updated HH:MM:SS" timestamp line.

import { useStaleDetector } from "../../hooks/useStaleDetector";
import { useSupabaseStatus } from "../../hooks/useSupabaseStatus";

const MODE_LABEL: Record<string, string> = {
  configured: "configured",
  degraded: "degraded",
  disabled: "disabled",
};

const MODE_STATUS_CLASS: Record<string, string> = {
  configured: "status-ok",
  degraded: "status-warn",
  disabled: "status-muted",
};

export function SupabaseStatusCard() {
  const { data, loading, error, lastUpdatedAt } = useSupabaseStatus();

  // SUPA-009: classify timestamp age for stale indicator — display-only.
  const staleStatus = useStaleDetector(lastUpdatedAt);

  const modeLabel = data ? (MODE_LABEL[data.mode] ?? data.mode) : "—";
  const modeClass = data ? (MODE_STATUS_CLASS[data.mode] ?? "status-muted") : "status-muted";

  const rows: Array<[string, string]> = data
    ? [
        ["configured", String(data.configured)],
        ["available", String(data.available)],
        ["degraded", String(data.degraded)],
        ["url_configured", String(data.url_configured)],
        ["anon_key_configured", String(data.anon_key_configured)],
        ["service_key_configured", String(data.service_key_configured)],
        ["read_only", String(data.read_only)],
        ["writes_enabled", String(data.writes_enabled)],
      ]
    : [];

  return (
    <section id="supabase-status" className="terminal-panel">
      <div className="panel-header">
        <span>Supabase</span>
        <span className={modeClass}>
          {loading && !data ? "polling…" : modeLabel}
        </span>
      </div>

      {error ? (
        <div className="guardrail-list">
          <div className="guardrail-row">
            <span>status</span>
            <strong>fetch error</strong>
          </div>
          <div className="guardrail-row">
            <span>detail</span>
            <strong>{error}</strong>
          </div>
        </div>
      ) : (
        <>
          <div className="guardrail-list">
            {rows.map(([label, value]) => (
              <div key={label} className="guardrail-row">
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>

          {data?.reason ? (
            <p className="panel-note">{data.reason}</p>
          ) : null}

          {lastUpdatedAt ? (
            <p
              className={`panel-note${staleStatus === "stale" ? " data-stale" : ""}`}
            >
              updated{" "}
              {lastUpdatedAt.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              })}
              {staleStatus === "stale" ? " · stale" : ""}
            </p>
          ) : null}
        </>
      )}
    </section>
  );
}
