import type { SignalDecisionRecord } from "../types/api";

export interface SignalDecisionExportFilters {
  symbol: string;
  decision: string;
  riskStatus: string;
  direction: string;
  blockedOnly: boolean;
}

interface ExportOptions {
  generatedAt: string;
  filters: SignalDecisionExportFilters;
}

const CSV_COLUMNS = [
  "id",
  "timestamp",
  "symbol",
  "direction",
  "confidence",
  "source",
  "strategy",
  "risk_status",
  "decision",
  "blocked_reason",
  "dry_run",
  "auto_trade",
  "read_only",
  "stop_loss_required",
  "take_profit_required",
  "max_risk_per_trade",
];

function timestampForFilename(date = new Date()) {
  const pad = (value: number) => value.toString().padStart(2, "0");
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    "-",
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join("");
}

function csvValue(value: string | number | boolean | null | undefined) {
  const text = value == null ? "" : String(value);
  return `"${text.replace(/"/g, '""')}"`;
}

function downloadFile(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function filename(extension: "csv" | "json") {
  return `mellytrade-dry-run-journal-${timestampForFilename()}.${extension}`;
}

function safeRecord(record: SignalDecisionRecord) {
  return {
    id: record.id,
    timestamp: record.timestamp,
    symbol: record.symbol,
    direction: record.direction,
    confidence: record.confidence,
    source: record.source,
    strategy: record.strategy,
    risk_status: record.risk_status,
    decision: record.decision,
    blocked_reason: record.blocked_reason,
    dry_run: record.dry_run,
    auto_trade: record.auto_trade,
    read_only: record.read_only,
    stop_loss_required: record.stop_loss_required,
    take_profit_required: record.take_profit_required,
    max_risk_per_trade: record.max_risk_per_trade,
  };
}

export function exportSignalDecisionsCsv(
  records: SignalDecisionRecord[],
  _options: ExportOptions,
) {
  const rows = records.map((record) => [
    record.id,
    record.timestamp,
    record.symbol,
    record.direction,
    record.confidence,
    record.source,
    record.strategy,
    record.risk_status,
    record.decision,
    record.blocked_reason ?? "",
    record.dry_run,
    record.auto_trade,
    record.read_only,
    record.stop_loss_required,
    record.take_profit_required,
    record.max_risk_per_trade,
  ]);
  const csv = [
    CSV_COLUMNS.map(csvValue).join(","),
    ...rows.map((row) => row.map(csvValue).join(",")),
  ].join("\n");
  downloadFile(filename("csv"), csv, "text/csv;charset=utf-8");
}

export function exportSignalDecisionsJson(
  records: SignalDecisionRecord[],
  { generatedAt, filters }: ExportOptions,
) {
  const payload = {
    generated_at: generatedAt,
    record_count: records.length,
    filters,
    read_only: true,
    dry_run: true,
    auto_trade: false,
    records: records.map(safeRecord),
  };
  downloadFile(
    filename("json"),
    JSON.stringify(payload, null, 2),
    "application/json;charset=utf-8",
  );
}
