import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { RiskConfig, RiskStatus, RiskViolation } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useRiskConfig() {
  const loader = useCallback(() => apiGet<RiskConfig>("/risk/config"), []);
  return usePollingResource(loader, 5000);
}

export function useRiskStatus() {
  const loader = useCallback(() => apiGet<RiskStatus>("/risk/status"), []);
  return usePollingResource(loader, 5000);
}

export function useRiskViolations() {
  const loader = useCallback(
    () => apiGet<RiskViolation[]>("/risk/violations"),
    [],
  );
  return usePollingResource(loader, 5000);
}

