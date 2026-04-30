import { useCallback } from "react";

import { getSignals } from "../lib/mellyApi";
import type { SignalSummary } from "../types/melly";
import { usePollingResource } from "./usePollingResource";

const POLL_MS = 15_000;
const DEFAULT_LIMIT = 50;

export interface UseMellySignalsOptions {
  symbol?: string;
  status?: "accepted" | "rejected";
  since?: string;
  until?: string;
  limit?: number;
}

export function useMellySignals(options: UseMellySignalsOptions = {}) {
  const {
    symbol,
    status,
    since,
    until,
    limit = DEFAULT_LIMIT,
  } = options;

  const loader = useCallback(
    () =>
      getSignals({
        symbol,
        status,
        since,
        until,
        limit,
      }),
    [symbol, status, since, until, limit],
  );

  return usePollingResource<SignalSummary[]>(loader, POLL_MS);
}
