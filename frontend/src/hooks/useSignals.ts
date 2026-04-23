import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { SignalSummary } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useSignals() {
  const loader = useCallback(() => apiGet<SignalSummary[]>("/signals"), []);
  return usePollingResource(loader, 5000);
}

