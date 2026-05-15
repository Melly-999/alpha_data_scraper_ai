const RAW_API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api") as string;
const API_BASE = RAW_API_BASE.replace(/\/+$/, "");

export const DEFAULT_SCANNER_PREVIEW_SYMBOLS = [
  "AAPL",
  "NVDA",
  "MSFT",
  "EURUSD",
  "XAUUSD",
] as const;

export type SignalScannerAction =
  | "HOLD"
  | "WATCH"
  | "LONG_SETUP"
  | "SHORT_SETUP"
  | "NO_TRADE";

export type SignalScannerResult = {
  symbol: string;
  action: SignalScannerAction;
  confidence: number;
  reason: string;
  risk_allowed: false;
  execution_mode: "dry_run_only";
  requires_human_review: true;
  source: "scanner";
  timestamp: string;
};

export type SignalScannerBatch = {
  generated_at: string;
  results: SignalScannerResult[];
  read_only: true;
  execution_mode: "dry_run_only";
};

function joinUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${suffix}`;
}

function createFallbackScannerBatch(): SignalScannerBatch {
  return {
    generated_at: new Date().toISOString(),
    results: [],
    read_only: true,
    execution_mode: "dry_run_only",
  };
}

function normalizeScannerBatch(
  batch: Partial<SignalScannerBatch> | null | undefined,
): SignalScannerBatch {
  if (!batch || batch.read_only !== true || batch.execution_mode !== "dry_run_only") {
    return createFallbackScannerBatch();
  }

  return {
    generated_at:
      typeof batch.generated_at === "string"
        ? batch.generated_at
        : new Date().toISOString(),
    results: Array.isArray(batch.results)
      ? batch.results
          .map((result) => ({
            symbol: String(result?.symbol ?? "").trim(),
            action: result?.action,
            confidence: Number(result?.confidence ?? 0),
            reason: String(result?.reason ?? "").trim(),
            risk_allowed: false as const,
            execution_mode: "dry_run_only" as const,
            requires_human_review: true as const,
            source: "scanner" as const,
            timestamp:
              typeof result?.timestamp === "string"
                ? result.timestamp
                : new Date().toISOString(),
          }))
          .filter((result) => result.symbol && result.reason)
      : [],
    read_only: true,
    execution_mode: "dry_run_only",
  };
}

export async function getScannerPreview(
  symbols?: readonly string[],
): Promise<SignalScannerBatch> {
  const filteredSymbols = (symbols ?? [])
    .map((symbol) => symbol.trim())
    .filter(Boolean);
  const query = new URLSearchParams();

  if (filteredSymbols.length > 0) {
    query.set("symbols", filteredSymbols.join(","));
  }

  const path = query.toString()
    ? `/signals/scanner/preview?${query.toString()}`
    : "/signals/scanner/preview";

  try {
    const response = await fetch(joinUrl(path), {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      return createFallbackScannerBatch();
    }

    return normalizeScannerBatch(
      (await response.json()) as Partial<SignalScannerBatch>,
    );
  } catch {
    return createFallbackScannerBatch();
  }
}

export function createScannerPreviewFallback(): SignalScannerBatch {
  return createFallbackScannerBatch();
}
