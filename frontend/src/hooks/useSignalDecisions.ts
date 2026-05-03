import { useCallback } from "react";

import { apiGet } from "../lib/api";
import type {
  DecisionDirection,
  DecisionRiskStatus,
  DecisionType,
  SignalDecisionHistoryResponse,
} from "../types/api";
import { usePollingResource } from "./usePollingResource";

interface SignalDecisionParams {
  limit?: number;
  symbol?: string;
  decision?: DecisionType | "";
  riskStatus?: DecisionRiskStatus | "";
  direction?: DecisionDirection | "";
}

function buildDecisionQuery({
  limit = 50,
  symbol = "",
  decision = "",
  riskStatus = "",
  direction = "",
}: SignalDecisionParams) {
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
  if (direction !== "") {
    query.set("direction", direction);
  }
  return query.toString();
}

export function useSignalDecisions(params: SignalDecisionParams = {}) {
  const loader = useCallback(
    () =>
      apiGet<SignalDecisionHistoryResponse>(
        `/signals/decisions?${buildDecisionQuery(params)}`,
      ),
    [
      params.limit,
      params.symbol,
      params.decision,
      params.riskStatus,
      params.direction,
    ],
  );
  return usePollingResource(loader, 30_000);
}
