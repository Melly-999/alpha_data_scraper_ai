import { useMemo, useState } from "react";
import { useStaleDetector } from "../../hooks/useStaleDetector";
import type { TerminalEvent } from "../../lib/terminalApi";
import { AuditRailFilters, type AuditFilterOption } from "./AuditRailFilters";

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
  const [searchValue, setSearchValue] = useState("");
  const [severityValue, setSeverityValue] = useState("");
  const [sourceValue, setSourceValue] = useState("");

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

  const severityOptions: AuditFilterOption[] = [
    { value: "success", label: "Success" },
    { value: "info", label: "Info" },
    { value: "warning", label: "Warning" },
  ];

  const sourceOptions = useMemo<AuditFilterOption[]>(
    () =>
      Array.from(new Set(events.map((event) => event.source)))
        .filter((source) => source.trim().length > 0)
        .sort((left, right) => left.localeCompare(right))
        .map((source) => ({ value: source, label: source })),
    [events],
  );

  const filteredEvents = useMemo(
    () =>
      events.filter((event) => {
        if (severityValue && event.severity !== severityValue) {
          return false;
        }
        if (sourceValue && event.source !== sourceValue) {
          return false;
        }
        const query = searchValue.trim().toLowerCase();
        if (!query) {
          return true;
        }
        const searchable = [
          event.event,
          event.severity,
          event.time,
          event.source,
          event.message,
          event.safety_note ?? "",
        ]
          .join(" ")
          .toLowerCase();
        return searchable.includes(query);
      }),
    [events, searchValue, severityValue, sourceValue],
  );

  const hasActiveFilters =
    searchValue.trim().length > 0 || severityValue.length > 0 || sourceValue.length > 0;
  const filterSummary = hasActiveFilters
    ? `Showing ${filteredEvents.length} of ${events.length} audit events.`
    : undefined;

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

      <AuditRailFilters
        searchValue={searchValue}
        onSearchValueChange={setSearchValue}
        severityValue={severityValue}
        onSeverityValueChange={setSeverityValue}
        sourceValue={sourceValue}
        onSourceValueChange={setSourceValue}
        severityOptions={severityOptions}
        sourceOptions={sourceOptions}
        summary={filterSummary}
        onClear={() => {
          setSearchValue("");
          setSeverityValue("");
          setSourceValue("");
        }}
      />

      <div className="event-list">
        {events.length === 0 ? (
          <p className="event-list-empty">No events recorded yet.</p>
        ) : null}
        {events.length > 0 && filteredEvents.length === 0 ? (
          <p className="event-list-empty event-list-empty--filtered">
            No audit events match the current filters.
          </p>
        ) : null}
        {filteredEvents.map((event) => (
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
