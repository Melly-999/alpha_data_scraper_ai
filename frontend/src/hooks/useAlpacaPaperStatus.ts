// Read-only Alpaca Paper status hook — ALPACA-PAPER-READONLY-CARD-001.
//
// Polls GET /api/alpaca-paper/status every 30 seconds via the established
// apiGet + usePollingResource infrastructure. GET-only. No writes, no
// mutations, no broker calls. The loader never rejects (see
// fetchAlpacaPaperStatusView), so the card always has a safe snapshot.

import { useCallback } from "react";

import { fetchAlpacaPaperStatusView } from "../lib/alpacaPaperApi";
import { usePollingResource } from "./usePollingResource";

const ALPACA_PAPER_STATUS_INTERVAL_MS = 30_000;

/**
 * Polls GET /api/alpaca-paper/status every 30 seconds.
 *
 * Returns { data, loading, error, lastUpdatedAt } via usePollingResource.
 * `data` is an AlpacaPaperStatusView and is populated even when the backend
 * is unavailable (safe fallback). GET-only; no side effects beyond polling.
 */
export function useAlpacaPaperStatus() {
  const loader = useCallback(() => fetchAlpacaPaperStatusView(), []);
  return usePollingResource(loader, ALPACA_PAPER_STATUS_INTERVAL_MS);
}
