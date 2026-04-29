import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { BrokerAccountResponse, BrokerHealthResponse } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useBrokerHealth() {
  const loader = useCallback(() => apiGet<BrokerHealthResponse>("/broker/health"), []);
  return usePollingResource(loader, 5000);
}

export function useBrokerAccount() {
  const loader = useCallback(() => apiGet<BrokerAccountResponse>("/broker/account"), []);
  return usePollingResource(loader, 5000);
}
