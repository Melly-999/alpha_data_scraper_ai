import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { PositionSummary } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useOpenPositions() {
  const loader = useCallback(
    () => apiGet<PositionSummary[]>("/positions/open"),
    [],
  );
  return usePollingResource(loader, 2000);
}

export function usePositionHistory() {
  const loader = useCallback(
    () => apiGet<PositionSummary[]>("/positions/history"),
    [],
  );
  return usePollingResource(loader, 2000);
}

