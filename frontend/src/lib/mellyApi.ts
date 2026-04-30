// Read-only client for the Sprint 1A `mellytrade-api` backend.
//
// The base URL defaults to `/melly-api` so the dev server can proxy to
// the local FastAPI instance, but operators can point it at any host
// via `VITE_MELLY_API_BASE_URL`. Optional `VITE_MELLY_API_KEY` is sent
// as `X-API-Key` because every endpoint except `/health` is gated by
// `require_api_key`.
//
// Only GET helpers are exported on purpose: this module must NEVER
// place orders, modify risk gates, or otherwise mutate the backend.

import type {
  AuditFeed,
  AuditQuery,
  HealthInfo,
  RiskConfig,
  SignalSummary,
  SignalsQuery,
} from "../types/melly";

const RAW_BASE = (import.meta.env.VITE_MELLY_API_BASE_URL ??
  "/melly-api") as string;
const MELLY_BASE = RAW_BASE.replace(/\/+$/, "");
const MELLY_KEY = (import.meta.env.VITE_MELLY_API_KEY ?? "") as string;

function joinUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${MELLY_BASE}${suffix}`;
}

function appendParam(
  params: URLSearchParams,
  key: string,
  value: string | number | undefined | null,
): void {
  if (value === undefined || value === null || value === "") {
    return;
  }
  params.append(key, String(value));
}

async function parseError(response: Response): Promise<string> {
  const fallback = `${response.status} ${response.statusText}`;
  try {
    const text = await response.text();
    if (!text) {
      return fallback;
    }
    try {
      const parsed = JSON.parse(text);
      if (parsed && typeof parsed === "object") {
        const detail = (parsed as { detail?: unknown }).detail;
        if (typeof detail === "string" && detail.length > 0) {
          return detail;
        }
        if (
          detail &&
          typeof detail === "object" &&
          "detail" in (detail as Record<string, unknown>)
        ) {
          const inner = (detail as { detail?: unknown }).detail;
          if (typeof inner === "string" && inner.length > 0) {
            return inner;
          }
        }
        const reason = (parsed as { reason?: unknown }).reason;
        if (typeof reason === "string" && reason.length > 0) {
          return reason;
        }
      }
    } catch {
      // not JSON; fall through to text
    }
    return text.length > 240 ? `${text.slice(0, 240)}...` : text;
  } catch {
    return fallback;
  }
}

async function mellyGet<T>(path: string): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (MELLY_KEY) {
    headers["X-API-Key"] = MELLY_KEY;
  }
  const response = await fetch(joinUrl(path), {
    method: "GET",
    headers,
    credentials: "same-origin",
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  if (response.status === 204) {
    return undefined as unknown as T;
  }
  return (await response.json()) as T;
}

export function getHealth(): Promise<HealthInfo> {
  return mellyGet<HealthInfo>("/health");
}

export function getSignals(query: SignalsQuery = {}): Promise<SignalSummary[]> {
  const params = new URLSearchParams();
  appendParam(params, "symbol", query.symbol);
  appendParam(params, "status", query.status);
  appendParam(params, "since", query.since);
  appendParam(params, "until", query.until);
  appendParam(params, "limit", query.limit);
  const qs = params.toString();
  return mellyGet<SignalSummary[]>(`/signals${qs ? `?${qs}` : ""}`);
}

export function getAuditFeed(query: AuditQuery = {}): Promise<AuditFeed> {
  const params = new URLSearchParams();
  appendParam(params, "event_type", query.event_type);
  appendParam(params, "limit", query.limit);
  const qs = params.toString();
  return mellyGet<AuditFeed>(`/audit${qs ? `?${qs}` : ""}`);
}

export function getRiskConfig(): Promise<RiskConfig> {
  return mellyGet<RiskConfig>("/risk/config");
}
