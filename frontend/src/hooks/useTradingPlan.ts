// Read-only polling hook for the Daily Trading Plan preview.
//
// Uses the existing apiGet helper — there is no mutating sibling here on
// purpose. The plan endpoint is GET-only and the frontend must not learn
// how to POST/PUT/DELETE against it.

import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { TradingPlanResponse } from "../types/api";
import { usePollingResource } from "./usePollingResource";

const POLL_MS = 60_000; // The plan is static-per-day; one minute is plenty.

export function useTradingPlan() {
  const loader = useCallback(
    () => apiGet<TradingPlanResponse>("/terminal/trading-plan"),
    [],
  );
  return usePollingResource(loader, POLL_MS);
}
