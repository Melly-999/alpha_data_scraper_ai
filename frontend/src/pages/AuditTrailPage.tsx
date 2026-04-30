import { useMemo, useState } from "react";

import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { useAuditFeed } from "../hooks/useAuditFeed";
import type { AuditEvent, AuditEventType } from "../types/melly";

const EVENT_TYPES: Array<{ value: "" | AuditEventType; label: string }> = [
  { value: "", label: "All events" },
  { value: "signal_accepted", label: "Signal accepted" },
  { value: "signal_rejected", label: "Signal rejected" },
  { value: "risk_gate_failed", label: "Risk gate failed" },
  { value: "cooldown_active", label: "Cooldown active" },
  { value: "dry_run_active", label: "Dry-run active" },
  { value: "read_only_mode_active", label: "Read-only mode active" },
  { value: "live_orders_blocked", label: "Live orders blocked" },
  { value: "mt5_connection_status", label: "MT5 connection status" },
];

function severityTone(
  severity: AuditEvent["severity"],
): "green" | "amber" | "red" | "muted" | "blue" {
  switch (severity) {
    case "info":
      return "blue";
    case "warning":
      return "amber";
    case "error":
      return "red";
    default:
      return "muted";
  }
}

function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatDetail(detail: AuditEvent["detail"]): string | null {
  if (!detail || Object.keys(detail).length === 0) {
    return null;
  }
  try {
    return JSON.stringify(detail);
  } catch {
    return null;
  }
}

export function AuditTrailPage() {
  const [eventType, setEventType] = useState<"" | AuditEventType>("");
  const { data, loading, error } = useAuditFeed({
    eventType: eventType === "" ? undefined : eventType,
    limit: 200,
  });

  const events = useMemo<AuditEvent[]>(() => {
    if (!data) return [];
    return [...data.events].sort((a, b) =>
      b.timestamp.localeCompare(a.timestamp),
    );
  }, [data]);

  return (
    <div className="page-grid passive-page">
      <div className="passive-main">
        <section className="page-header">
          <div>
            <div className="eyebrow">Audit Trail</div>
            <h1 className="page-title">Read-only event feed</h1>
            <div className="dashboard-muted">
              Risk gates, cooldowns, and safety state events from the
              MellyTrade API. No mutation actions are exposed here.
            </div>
          </div>
          <div className="page-header-meta">
            <Badge tone={data?.dry_run ? "green" : "muted"}>
              dry_run: {data ? String(data.dry_run) : "?"}
            </Badge>
            <Badge tone={data?.read_only ? "green" : "muted"}>
              read_only: {data ? String(data.read_only) : "?"}
            </Badge>
            <Badge tone={data?.live_orders_blocked ? "green" : "red"}>
              live_orders_blocked:{" "}
              {data ? String(data.live_orders_blocked) : "?"}
            </Badge>
          </div>
        </section>

        <Card
          title="Events"
          right={
            <Badge tone="muted">{events.length} entries · newest first</Badge>
          }
        >
          <div className="audit-feed-controls">
            <label htmlFor="audit-event-type" className="dashboard-muted">
              Filter
            </label>
            <select
              id="audit-event-type"
              value={eventType}
              onChange={(event) =>
                setEventType(event.target.value as "" | AuditEventType)
              }
            >
              {EVENT_TYPES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {loading && !data ? (
            <div className="state">Loading audit events...</div>
          ) : null}
          {error && !data ? (
            <div className="state error">{error}</div>
          ) : null}
          {data && events.length === 0 ? (
            <div className="state">No audit events for this filter.</div>
          ) : null}

          {events.map((event, index) => {
            const detail = formatDetail(event.detail ?? null);
            return (
              <div
                className="audit-event"
                key={`${event.timestamp}-${event.type}-${event.signal_id ?? index}`}
              >
                <div>
                  <div className="audit-event-time">
                    {formatTimestamp(event.timestamp)}
                  </div>
                </div>
                <div>
                  <Badge tone={severityTone(event.severity)}>
                    {event.type}
                  </Badge>
                </div>
                <div>
                  <div className="audit-event-message">{event.message}</div>
                  {detail ? (
                    <div className="audit-event-detail">{detail}</div>
                  ) : null}
                </div>
              </div>
            );
          })}
        </Card>
      </div>
    </div>
  );
}
