import { useCallback, useEffect } from "react";

import { apiGet } from "../lib/api";
import { useAppMetaStore } from "../stores/useAppMetaStore";
import type { HealthResponse } from "../types/api";
import { usePollingResource } from "./usePollingResource";

export function useHealth() {
  const setHealth = useAppMetaStore((state) => state.setHealth);
  const loader = useCallback(() => apiGet<HealthResponse>("/health"), []);
  const state = usePollingResource(loader, 5000);

  useEffect(() => {
    if (state.data) {
      setHealth(state.data);
    }
  }, [setHealth, state.data]);

  return state;
}

