import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { MT5Status } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useMt5Status() {
  const loader = useCallback(() => apiGet<MT5Status>("/mt5/status"), []);
  return usePollingResource(loader, 3000);
}

