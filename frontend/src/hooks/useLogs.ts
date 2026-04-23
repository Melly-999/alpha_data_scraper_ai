import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { LogEntry } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useLogs() {
  const loader = useCallback(() => apiGet<LogEntry[]>("/logs?limit=100"), []);
  return usePollingResource(loader, 5000);
}

