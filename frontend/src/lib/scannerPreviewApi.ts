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

// ---------------------------------------------------------------------------
// SIG-UNIVERSE-002 — Universe types
// ---------------------------------------------------------------------------

export type SignalUniversePreset = {
  name: string;
  label: string;
  symbols: string[];
  item_count: number;
  asset_classes: string[];
  tags: string[];
  read_only: true;
  execution_mode: "dry_run_only";
  requires_human_review: true;
};

export type SignalUniverseListResponse = {
  read_only: true;
  execution_mode: "dry_run_only";
  requires_human_review: true;
  universes: SignalUniversePreset[];
};

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

function demoRow(
  symbol: string,
  action: SignalScannerAction,
  confidence: number,
  reason: string,
  now: string,
): SignalScannerResult {
  return {
    symbol,
    action,
    confidence,
    reason,
    risk_allowed: false,
    execution_mode: "dry_run_only",
    requires_human_review: true,
    source: "scanner",
    timestamp: now,
  };
}

function createFallbackScannerBatch(): SignalScannerBatch {
  const now = new Date().toISOString();
  return {
    generated_at: now,
    results: [
      demoRow("AAPL", "WATCH", 62,
        "Trend above EMA50 — monitoring for breakout above resistance. Below 70% floor. Advisory only.",
        now),
      demoRow("NVDA", "LONG_SETUP", 74,
        "Bullish H1 momentum with RSI 58 and MACD cross. Dry-run-only — human review required.",
        now),
      demoRow("MSFT", "HOLD", 55,
        "Mixed timeframe signals — H4 bearish, D1 neutral. No edge identified.",
        now),
      demoRow("EURUSD", "WATCH", 61,
        "Ranging session; awaiting momentum confirmation. Below confidence floor.",
        now),
      demoRow("XAUUSD", "SHORT_SETUP", 71,
        "Stalling at resistance with bearish MACD divergence. Dry-run-eligible — review only.",
        now),
    ],
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

// ---------------------------------------------------------------------------
// SIG-UNIVERSE-002 — Universe list fallback and fetch
// ---------------------------------------------------------------------------

function createFallbackUniverseListResponse(): SignalUniverseListResponse {
  return {
    read_only: true,
    execution_mode: "dry_run_only",
    requires_human_review: true,
    universes: [
      {
        name: "ai_mega_caps",
        label: "AI Mega Caps",
        symbols: ["NVDA", "GOOGL", "AMZN", "MSFT", "AAPL", "META", "TSLA", "AMD", "AVGO", "ORCL"],
        item_count: 10,
        asset_classes: ["equity"],
        tags: ["ai", "mega-cap", "us-equity"],
        read_only: true,
        execution_mode: "dry_run_only",
        requires_human_review: true,
      },
      {
        name: "xtb_cfd_watchlist",
        label: "XTB / CFD Watchlist",
        symbols: ["US100", "US500", "XAUUSD", "NATGAS", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD"],
        item_count: 8,
        asset_classes: ["index", "commodity", "fx", "crypto"],
        tags: ["cfd", "xtb", "macro"],
        read_only: true,
        execution_mode: "dry_run_only",
        requires_human_review: true,
      },
      {
        name: "core_macro",
        label: "Core Macro",
        symbols: ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "OIL.WTI", "BTCUSD", "ETHUSD"],
        item_count: 7,
        asset_classes: ["fx", "commodity", "crypto"],
        tags: ["macro", "fx", "commodities"],
        read_only: true,
        execution_mode: "dry_run_only",
        requires_human_review: true,
      },
      {
        name: "polish_eu_watchlist",
        label: "Polish / EU Watchlist",
        symbols: ["PKN", "CDR", "DAX", "EURPLN", "USDPLN"],
        item_count: 5,
        asset_classes: ["equity", "index", "fx"],
        tags: ["polish", "eu", "regional"],
        read_only: true,
        execution_mode: "dry_run_only",
        requires_human_review: true,
      },
      {
        name: "default_demo",
        label: "Default Demo",
        symbols: ["AAPL", "NVDA", "MSFT", "EURUSD", "XAUUSD", "BTCUSD"],
        item_count: 6,
        asset_classes: ["equity", "fx", "commodity", "crypto"],
        tags: ["demo", "default"],
        read_only: true,
        execution_mode: "dry_run_only",
        requires_human_review: true,
      },
    ],
  };
}

export async function getScannerUniverses(): Promise<SignalUniverseListResponse> {
  try {
    const response = await fetch(joinUrl("/signals/scanner/universes"), {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      return createFallbackUniverseListResponse();
    }

    const payload = (await response.json()) as Partial<SignalUniverseListResponse>;
    if (
      payload?.read_only !== true ||
      payload?.execution_mode !== "dry_run_only" ||
      !Array.isArray(payload?.universes)
    ) {
      return createFallbackUniverseListResponse();
    }

    return payload as SignalUniverseListResponse;
  } catch {
    return createFallbackUniverseListResponse();
  }
}

// ---------------------------------------------------------------------------
// Scanner preview — updated to accept optional universe param
// ---------------------------------------------------------------------------

export type ScannerPreviewOptions = {
  symbols?: readonly string[];
  universe?: string;
};

export async function getScannerPreview(
  options?: ScannerPreviewOptions | readonly string[],
): Promise<SignalScannerBatch> {
  // Backward-compatible: if called with a plain array, treat it as { symbols }
  let resolved: ScannerPreviewOptions;
  if (Array.isArray(options)) {
    resolved = { symbols: options as readonly string[] };
  } else {
    resolved = (options as ScannerPreviewOptions | undefined) ?? {};
  }

  const filteredSymbols = (resolved.symbols ?? [])
    .map((symbol) => symbol.trim())
    .filter(Boolean);
  const query = new URLSearchParams();

  if (filteredSymbols.length > 0) {
    query.set("symbols", filteredSymbols.join(","));
  } else if (resolved.universe && resolved.universe.trim()) {
    query.set("universe", resolved.universe.trim());
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
