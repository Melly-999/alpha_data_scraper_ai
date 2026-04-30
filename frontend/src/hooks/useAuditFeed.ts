import { useCallback } from "react";

import { getAuditFeed } from "../lib/mellyApi";
import type { AuditEventType, AuditFeed } from "../types/melly";
import { usePollingResource } from "./usePollingResource";

const POLL_MS = 12_000;
const DEFAULT_LIMIT = 100;

export interface UseAuditFeedOptions {
  eventType?: AuditEventType;
  limit?: number;
}

export function useAuditFeed(options: UseAuditFeedOptions = {}) {
  const { eventType, limit = DEFAULT_LIMIT } = options;
  const loader = useCallback(
    () =>
      getAuditFeed({
        event_type: eventType,
        limit,
      }),
    [eventType, limit],
  );
  return usePollingResource<AuditFeed>(loader, POLL_MS);
}
