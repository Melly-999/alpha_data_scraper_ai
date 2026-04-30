import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { AuditEventFeedResponse } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useTerminalEvents(limit = 50) {
  const loader = useCallback(
    () => apiGet<AuditEventFeedResponse>(`/terminal/events?limit=${limit}`),
    [limit],
  );
  return usePollingResource(loader, 30_000);
}
