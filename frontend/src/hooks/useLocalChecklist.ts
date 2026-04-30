import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type { LocalChecklistResponse } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useLocalChecklist() {
  const loader = useCallback(
    () => apiGet<LocalChecklistResponse>("/local/checklist"),
    [],
  );
  return usePollingResource(loader, 5000);
}
