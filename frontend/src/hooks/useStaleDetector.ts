/**
 * useStaleDetector — SUPA-009
 *
 * Pure computation hook that classifies a polling timestamp as
 * "initializing" | "fresh" | "stale".  No fetch, no side effects beyond
 * a local interval timer.  Used by terminal panels to surface data-age
 * warnings in the read-only observability UI.
 *
 * Design constraints:
 *  - No fetch / apiGet / apiPost
 *  - No browser storage (localStorage / sessionStorage / cookies)
 *  - No WebSocket / EventSource
 *  - No external dependencies
 *  - Cleanup via clearInterval on unmount / dependency change
 */

import { useEffect, useState } from "react";

/** Default staleness threshold: 90 s = 3× the standard 30 s poll interval. */
const STALE_THRESHOLD_MS = 90_000;

/** Re-evaluate freshness every 15 s to keep the label current. */
const RECHECK_INTERVAL_MS = 15_000;

/** Possible freshness states returned by the hook. */
export type StaleStatus = "initializing" | "fresh" | "stale";

/**
 * Classify a `lastUpdatedAt` timestamp as initializing / fresh / stale.
 *
 * @param lastUpdatedAt - The timestamp of the most recent successful poll,
 *   or `null` if no successful poll has occurred yet.
 * @param thresholdMs   - Staleness threshold in milliseconds.
 *   Defaults to {@link STALE_THRESHOLD_MS} (90 000 ms).
 *
 * @returns
 *   - `"initializing"` — no data has arrived yet (`lastUpdatedAt` is `null`)
 *   - `"fresh"`        — data arrived within `thresholdMs`
 *   - `"stale"`        — data is older than `thresholdMs`
 */
export function useStaleDetector(
  lastUpdatedAt: Date | null,
  thresholdMs: number = STALE_THRESHOLD_MS,
): StaleStatus {
  const [status, setStatus] = useState<StaleStatus>(() => {
    if (lastUpdatedAt === null) return "initializing";
    return Date.now() - lastUpdatedAt.getTime() > thresholdMs ? "stale" : "fresh";
  });

  useEffect(() => {
    const compute = () => {
      if (lastUpdatedAt === null) {
        setStatus("initializing");
        return;
      }
      const age = Date.now() - lastUpdatedAt.getTime();
      setStatus(age > thresholdMs ? "stale" : "fresh");
    };

    // Evaluate immediately on mount / dependency change.
    compute();

    // Re-evaluate on a 15 s interval so the label stays accurate.
    const id = window.setInterval(compute, RECHECK_INTERVAL_MS);

    // Cleanup: cancel the interval when the component unmounts or
    // lastUpdatedAt / thresholdMs changes.
    return () => window.clearInterval(id);
  }, [lastUpdatedAt, thresholdMs]);

  return status;
}
