import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type {
  DecisionRiskStatus,
  DecisionType,
  SignalLifecycleResponse,
} from "../types/api";
import { usePollingResource } from "./usePollingResource";

interface SignalLifecycleParams {
  limit?: number;
  symbol?: string;
  decision?: DecisionType | "";
  riskStatus?: DecisionRiskStatus | "";
}

function buildLifecycleQuery({
  limit = 20,
  symbol = "",
  decision = "",
  riskStatus = "",
}: SignalLifecycleParams) {
  const query = new URLSearchParams();
  query.set("limit", String(limit));
  const trimmedSymbol = symbol.trim();
  if (trimmedSymbol !== "") {
    query.set("symbol", trimmedSymbol);
  }
  if (decision !== "") {
    query.set("decision", decision);
  }
  if (riskStatus !== "") {
    query.set("risk_status", riskStatus);
  }
  return query.toString();
}

export function useSignalLifecycle(params: SignalLifecycleParams = {}) {
  const loader = useCallback(
    () =>
      apiGet<SignalLifecycleResponse>(
        `/signals/lifecycle?${buildLifecycleQuery(params)}`,
      ),
    [params.limit, params.symbol, params.decision, params.riskStatus],
  );
  return usePollingResource(loader, 30_000);
}
