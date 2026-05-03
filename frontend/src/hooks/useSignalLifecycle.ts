import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { SignalLifecycleResponse } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useSignalLifecycle(limit = 50) {
  const loader = useCallback(
    () => apiGet<SignalLifecycleResponse>(`/signals/lifecycle?limit=${limit}`),
    [limit],
  );
  return usePollingResource(loader, 30_000);
}
