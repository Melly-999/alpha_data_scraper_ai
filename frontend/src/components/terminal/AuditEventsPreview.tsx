// Audit events preview panel — SUPA-006.
//
// Enriched to display message, source, and safety_note alongside the
// existing event type, severity, and timestamp. Display-only — no
// interactivity, no buttons, no onClick handlers, no expand/collapse.
//
// SUPA-009: optional lastUpdatedAt prop surfaces data-freshness label.
// No execution semantics — display-only indicator.

import { useStaleDetector } from "../../hooks/useStaleDetector";
import type { TerminalEvent } from "../../lib/terminalApi";

type AuditEventsPreviewProps = {
  events: TerminalEvent[];
  /** Timestamp of the most recent successful poll, or null if not yet received. */
  lastUpdatedAt?: Date | null;
};

export function AuditEventsPreview({
  events,
  lastUpdatedAt = null,
}: AuditEventsPreviewProps) {
  const staleStatus = useStaleDetector(lastUpdatedAt ?? null);

  // Build the freshness label text.
  let freshnessLabel: string;
  if (staleStatus === "initializing") {
    freshnessLabel = "polling…";
  } else {
    const timeStr = (lastUpdatedAt as Date).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
    freshnessLabel =
      staleStatus === "stale" ? `updated ${timeStr} · stale` : `updated ${timeStr}`;
  }

  return (
    <section id="audit" className="terminal-panel">
      <div className="panel-header">
        <span>Audit events preview</span>
        <span>append-only</span>
      </div>

      {/* SUPA-009: data-freshness label — display-only, no execution semantics */}
      <p
        className={`data-freshness-label${staleStatus === "stale" ? " data-stale" : ""}`}
      >
        {freshnessLabel}
      </p>

      <div className="event-list">
        {events.map((event) => (
          <div key={event.id} className={`event-entry ${event.severity}`}>
            {/* Header row: severity class drives colour; event type + time */}
            <div className="event-row">
              <strong>{event.event}</strong>
              <span className="event-time">{event.time}</span>
            </div>

            {/* Source + message row */}
            {event.message ? (
              <div className="event-detail">
                {event.source ? (
                  <span className="event-source">{event.source}</span>
                ) : null}
                <span className="event-message">{event.message}</span>
              </div>
            ) : null}

            {/* Safety note row — muted emphasis, only when present */}
            {event.safety_note ? (
              <div className="event-safety-note">{event.safety_note}</div>
            ) : null}
          </div>
        ))}
      </div>
    </section>
  );
}
