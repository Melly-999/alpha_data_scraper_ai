import { useCallback } from "react";

import { getWatchlist } from "../lib/mellyApi";
import type { WatchlistItem } from "../types/melly";
import { usePollingResource } from "./usePollingResource";

const POLL_MS = 15_000;

export function useWatchlist() {
  const loader = useCallback(() => getWatchlist(), []);
  return usePollingResource<WatchlistItem[]>(loader, POLL_MS);
}
