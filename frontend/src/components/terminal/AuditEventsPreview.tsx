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
          <div key={event.id} className={`event-row ${event.severity}`}>
            <span>{event.time}</span>
            <strong>{event.event}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
