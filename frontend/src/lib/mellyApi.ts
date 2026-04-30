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
  AlertItem,
  AlertsQuery,
  AuditFeed,
  AuditQuery,
  HealthInfo,
  ReportItem,
  RiskConfig,
  SignalSummary,
  SignalsQuery,
} from "../types/melly";

const RAW_BASE = (import.meta.env.VITE_MELLY_API_BASE_URL ??
  "/melly-api") as string;
const MELLY_BASE = RAW_BASE.replace(/\/+$/, "");
const MELLY_KEY = (import.meta.env.VITE_MELLY_API_KEY ?? "") as string;
const REQUEST_TIMEOUT_MS = 10_000;

export interface MellyClientConfig {
  baseUrl: string;
  hasApiKey: boolean;
  timeoutMs: number;
}

export function getMellyClientConfig(): MellyClientConfig {
  return {
    baseUrl: MELLY_BASE,
    hasApiKey: MELLY_KEY.trim().length > 0,
    timeoutMs: REQUEST_TIMEOUT_MS,
  };
}

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

function nestedDetail(value: unknown): string | null {
  if (typeof value === "string" && value.length > 0) {
    return value;
  }
  if (value && typeof value === "object" && "detail" in value) {
    return nestedDetail((value as { detail?: unknown }).detail);
  }
  return null;
}

function apiErrorMessage(payload: unknown): string | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }
  const body = payload as { detail?: unknown; reason?: unknown };
  return nestedDetail(body.detail) ?? nestedDetail(body.reason);
}

async function parseError(response: Response): Promise<string> {
  const fallback = `${response.status} ${response.statusText}`;
  try {
    const text = await response.text();
    if (!text) {
      return fallback;
    }
    try {
      const message = apiErrorMessage(JSON.parse(text));
      if (message) {
        return message;
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
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(joinUrl(path), {
      method: "GET",
      headers,
      credentials: "same-origin",
      signal: controller.signal,
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error(
          MELLY_KEY
            ? "Unauthorized: VITE_MELLY_API_KEY was rejected by the backend"
            : "Unauthorized: configure VITE_MELLY_API_KEY for protected read-only endpoints",
        );
      }
      throw new Error(await parseError(response));
    }
    if (response.status === 204) {
      return undefined as unknown as T;
    }
    return (await response.json()) as T;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error(`Request timed out after ${REQUEST_TIMEOUT_MS / 1000}s`);
    }
    if (err instanceof TypeError) {
      throw new Error("Backend offline or unreachable");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
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

export function getAlerts(query: AlertsQuery = {}): Promise<AlertItem[]> {
  const params = new URLSearchParams();
  appendParam(params, "limit", query.limit);
  const qs = params.toString();
  return mellyGet<AlertItem[]>(`/alerts${qs ? `?${qs}` : ""}`);
}

export function getDailyReport(): Promise<ReportItem> {
  return mellyGet<ReportItem>("/reports/daily");
}

export function getWeeklyReport(): Promise<ReportItem> {
  return mellyGet<ReportItem>("/reports/weekly");
}
