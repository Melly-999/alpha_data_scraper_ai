import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { SignalDecisionHistoryResponse } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useSignalDecisions(limit = 50) {
  const loader = useCallback(
    () => apiGet<SignalDecisionHistoryResponse>(`/signals/decisions?limit=${limit}`),
    [limit],
  );
  return usePollingResource(loader, 30_000);
}
