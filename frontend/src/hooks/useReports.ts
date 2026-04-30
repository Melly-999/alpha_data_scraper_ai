import { useCallback } from "react";

import { getDailyReport, getWeeklyReport } from "../lib/mellyApi";
import type { ReportItem } from "../types/melly";
import { usePollingResource } from "./usePollingResource";

const POLL_MS = 30_000;

export function useDailyReport() {
  const loader = useCallback(() => getDailyReport(), []);
  return usePollingResource<ReportItem>(loader, POLL_MS);
}

export function useWeeklyReport() {
  const loader = useCallback(() => getWeeklyReport(), []);
  return usePollingResource<ReportItem>(loader, POLL_MS);
}
