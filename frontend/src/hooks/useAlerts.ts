import { useCallback } from "react";

import { getAlerts } from "../lib/mellyApi";
import type { AlertItem } from "../types/melly";
import { usePollingResource } from "./usePollingResource";

const POLL_MS = 12_000;
const DEFAULT_LIMIT = 100;

export interface UseAlertsOptions {
  limit?: number;
}

export function useAlerts(options: UseAlertsOptions = {}) {
  const { limit = DEFAULT_LIMIT } = options;
  const loader = useCallback(() => getAlerts({ limit }), [limit]);
  return usePollingResource<AlertItem[]>(loader, POLL_MS);
}
