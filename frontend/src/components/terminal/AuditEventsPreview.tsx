// Audit events preview panel — SUPA-006.
//
// Enriched to display message, source, and safety_note alongside the
// existing event type, severity, and timestamp. Display-only — no
// interactivity, no buttons, no onClick handlers, no expand/collapse.

import type { TerminalEvent } from "../../lib/terminalApi";

type AuditEventsPreviewProps = {
  events: TerminalEvent[];
};

export function AuditEventsPreview({ events }: AuditEventsPreviewProps) {
  return (
    <section id="audit" className="terminal-panel">
      <div className="panel-header">
        <span>Audit events preview</span>
        <span>append-only</span>
      </div>
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
