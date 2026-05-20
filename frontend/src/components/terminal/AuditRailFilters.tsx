import { useId } from "react";

export type AuditFilterOption = {
  value: string;
  label: string;
};

type AuditRailFiltersProps = {
  searchValue: string;
  onSearchValueChange: (value: string) => void;
  severityValue: string;
  onSeverityValueChange: (value: string) => void;
  sourceValue: string;
  onSourceValueChange: (value: string) => void;
  severityOptions: AuditFilterOption[];
  sourceOptions: AuditFilterOption[];
  summary?: string;
  onClear: () => void;
};

export function AuditRailFilters({
  searchValue,
  onSearchValueChange,
  severityValue,
  onSeverityValueChange,
  sourceValue,
  onSourceValueChange,
  severityOptions,
  sourceOptions,
  summary,
  onClear,
}: AuditRailFiltersProps) {
  const uid = useId();
  const searchId = `${uid}-audit-search`;
  const severityId = `${uid}-audit-severity`;
  const sourceId = `${uid}-audit-source`;

  return (
    <div className="audit-filter-bar" aria-label="Audit event filters">
      <div className="audit-filter-grid">
        <label className="audit-filter-field audit-filter-field--search" htmlFor={searchId}>
          <span className="audit-filter-label">Search</span>
          <input
            id={searchId}
            className="audit-filter-input"
            type="search"
            value={searchValue}
            onChange={(event) => onSearchValueChange(event.target.value)}
            aria-label="Search audit events"
            placeholder="Search event, message, source"
            spellCheck={false}
          />
        </label>

        <label className="audit-filter-field" htmlFor={severityId}>
          <span className="audit-filter-label">Severity</span>
          <select
            id={severityId}
            className="audit-filter-select"
            value={severityValue}
            onChange={(event) => onSeverityValueChange(event.target.value)}
            aria-label="Filter audit events by severity"
          >
            <option value="">All severities</option>
            {severityOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="audit-filter-field" htmlFor={sourceId}>
          <span className="audit-filter-label">Source</span>
          <select
            id={sourceId}
            className="audit-filter-select"
            value={sourceValue}
            onChange={(event) => onSourceValueChange(event.target.value)}
            aria-label="Filter audit events by source"
          >
            <option value="">All sources</option>
            {sourceOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <div className="audit-filter-actions">
          <button
            type="button"
            className="audit-filter-reset"
            onClick={onClear}
            aria-label="Reset audit filters"
          >
            Reset filters
          </button>
        </div>
      </div>

      {summary ? (
        <p className="audit-filter-summary" aria-live="polite">
          {summary}
        </p>
      ) : null}
    </div>
  );
}
