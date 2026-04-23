import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { AnalyticsSummary } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useAnalytics() {
  const loader = useCallback(
    () => apiGet<AnalyticsSummary>("/analytics/summary"),
    [],
  );
  return usePollingResource(loader, 15000);
}
