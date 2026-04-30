import { useCallback } from "react";

import { getHealth } from "../lib/mellyApi";
import { usePollingResource } from "./usePollingResource";

const POLL_MS = 30_000;

export function useMellyHealth() {
  const loader = useCallback(() => getHealth(), []);
  return usePollingResource(loader, POLL_MS);
}
