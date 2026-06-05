// MOBILE-AI-007C — screenshot preview API client.
//
// Posts raw image bytes to the analysis-only endpoint
// `POST /api/mobile/ai/screenshot/preview` and returns a paper-only preview.
//
// Display/analysis only: this client never places an order, never sends
// broker/account data, and never sends an AI provider key. The selected
// image is sent once for analysis and is not stored anywhere (the backend
// validates and discards it).

const RAW_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api") as string;
const API_BASE = RAW_BASE.replace(/\/+$/, "");

export const PREVIEW_PATH = "/mobile/ai/screenshot/preview";

// Mirror the backend constraints (MOBILE-AI-007A/007B).
export const ALLOWED_TYPES = ["image/png", "image/jpeg", "image/webp"] as const;
export const MAX_UPLOAD_BYTES = 5 * 1024 * 1024; // 5 MB

export type AllowedType = (typeof ALLOWED_TYPES)[number];

export interface ChartAnalysis {
  instrument: string;
  timeframe: string;
  trading_style: string;
  market_bias: string;
  trend: string;
  key_levels: string[];
  momentum: string;
  volatility: string;
  pattern: string;
  confirmation_checklist: string[];
  analysis_only: boolean;
  not_financial_advice: boolean;
  disclaimer: string;
}

export interface PaperGamePlan {
  scenario: string;
  entry_zone: string;
  invalidation: string;
  take_profit_1: string;
  take_profit_2: string | null;
  max_risk_per_trade_pct: number;
  status: string;
  paper_only: boolean;
  live_orders_blocked: boolean;
  broker_execution: boolean;
  requires_human_review: boolean;
}

export interface RiskAssessment {
  safety_score: number;
  risk_per_trade_pct: number;
  stop_loss_present: boolean;
  take_profit_present: boolean;
  overtrading_risk: string;
  news_risk: string;
  human_review_required: boolean;
  paper_only: boolean;
}

export interface ScreenshotAnalysisPreview {
  chart_analysis: ChartAnalysis;
  paper_game_plan: PaperGamePlan;
  risk_assessment: RiskAssessment;
  analysis_only: boolean;
  paper_only: boolean;
  live_orders_blocked: boolean;
  broker_execution: boolean;
  requires_human_review: boolean;
  stored: boolean;
  provider_used: boolean;
  disclaimer: string;
}

/** A client-side validation problem (before any network call). */
export class ClientValidationError extends Error {}

function joinUrl(path: string): string {
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${suffix}`;
}

/** Validate a selected file against the backend allowlist + size cap. */
export function validateFile(file: File): void {
  if (!ALLOWED_TYPES.includes(file.type as AllowedType)) {
    throw new ClientValidationError(
      "Unsupported file type. Use a PNG, JPEG, or WebP image.",
    );
  }
  if (file.size > MAX_UPLOAD_BYTES) {
    throw new ClientValidationError("File is too large. Maximum size is 5 MB.");
  }
  if (file.size === 0) {
    throw new ClientValidationError("File is empty.");
  }
}

async function parseDetail(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (data && typeof data.detail === "string") {
      return data.detail;
    }
  } catch {
    // ignore non-JSON
  }
  return `${response.status} ${response.statusText}`;
}

/**
 * Send the image for analysis and return a paper-only preview.
 *
 * Validates client-side first, then POSTs raw bytes with the image content
 * type. No multipart form, no extra fields, no broker/account data.
 */
export async function analyzeScreenshot(
  file: File,
): Promise<ScreenshotAnalysisPreview> {
  validateFile(file);

  const response = await fetch(joinUrl(PREVIEW_PATH), {
    method: "POST",
    headers: { "Content-Type": file.type, Accept: "application/json" },
    body: file,
    credentials: "same-origin",
  });

  if (!response.ok) {
    throw new Error(await parseDetail(response));
  }
  return (await response.json()) as ScreenshotAnalysisPreview;
}
