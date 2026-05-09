// ResourceState renders a consistent loading / error / empty / fresh-data
// shell around any read-only polling resource. It is intentionally
// presentation-only — it never triggers a fetch, never mutates anything,
// and never exposes order or execution affordances.
//
// Usage pattern (Terminal V1 polling page):
//
//   const { data, loading, error, lastUpdatedAt } = usePollingResource(...);
//   <ResourceState
//     loading={loading}
//     error={error}
//     empty={!data || data.length === 0}
//     lastUpdatedAt={lastUpdatedAt}
//     emptyMessage="No signals match this filter."
//   >
//     <Table ... />
//   </ResourceState>
//
// The component prefers the most informative state available: an active
// error wins over empty, empty wins over loading-with-stale-data, and
// fresh data wins over everything else.

import type { ReactNode } from "react";

interface ResourceStateProps {
  loading: boolean;
  error: string | null;
  empty: boolean;
  /**
   * Wall-clock timestamp of the most recent successful fetch, surfaced
   * by usePollingResource. Optional — when present we render a small
   * "Last updated …" footer so operators can spot stale panels.
   */
  lastUpdatedAt?: Date | null;
  /**
   * Copy shown when the resource resolved successfully but contained
   * zero rows. Keep it short and human; prefer "No signals yet" over
   * "Empty list".
   */
  emptyMessage?: string;
  /**
   * Optional override for the loading skeleton text. Defaults to a
   * neutral "Loading …".
   */
  loadingMessage?: string;
  children: ReactNode;
}

function formatTimestamp(value: Date): string {
  return value.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function ResourceState({
  loading,
  error,
  empty,
  lastUpdatedAt,
  emptyMessage = "No data yet.",
  loadingMessage = "Loading …",
  children,
}: ResourceStateProps) {
  // Backend offline / degraded — show the error prominently. We keep
  // any previously-fetched data hidden because it may be stale and we
  // do not want operators acting on it.
  if (error) {
    return (
      <div className="resource-state resource-state-error" role="alert">
        <div className="resource-state-title">Backend unavailable</div>
        <div className="resource-state-detail">{error}</div>
        {lastUpdatedAt ? (
          <div className="resource-state-meta">
            Last successful update at {formatTimestamp(lastUpdatedAt)}
          </div>
        ) : (
          <div className="resource-state-meta">No successful fetch yet.</div>
        )}
      </div>
    );
  }

  // First load before any data has arrived. After the first successful
  // fetch this branch is skipped and we always show data + an unobtrusive
  // "updated at" footer instead of flicker.
  if (loading && empty) {
    return (
      <div className="resource-state resource-state-loading" role="status">
        <div className="resource-state-title">{loadingMessage}</div>
        <div className="resource-state-detail">
          Fetching read-only data from the backend …
        </div>
      </div>
    );
  }

  if (empty) {
    return (
      <div className="resource-state resource-state-empty" role="status">
        <div className="resource-state-title">{emptyMessage}</div>
        {lastUpdatedAt ? (
          <div className="resource-state-meta">
            Last checked at {formatTimestamp(lastUpdatedAt)}
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div className="resource-state resource-state-ready">
      {children}
      {lastUpdatedAt ? (
        <div className="resource-state-meta">
          Last updated at {formatTimestamp(lastUpdatedAt)}
        </div>
      ) : null}
    </div>
  );
}
