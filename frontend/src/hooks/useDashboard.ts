import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { DashboardSummary } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useDashboard() {
  const loader = useCallback(
    () => apiGet<DashboardSummary>("/dashboard/summary"),
    [],
  );
  return usePollingResource(loader, 2000);
}

