import { useCallback } from "react";

import { getRiskConfig } from "../lib/mellyApi";
import { usePollingResource } from "./usePollingResource";

// Risk configuration changes rarely; poll once a minute.
const POLL_MS = 60_000;

export function useMellyRiskConfig() {
  const loader = useCallback(() => getRiskConfig(), []);
  return usePollingResource(loader, POLL_MS);
}
