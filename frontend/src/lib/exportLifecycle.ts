import type { SignalLifecycleRecord } from "../types/api";

export interface SignalLifecycleExportFilters {
  symbol: string;
  decision: string;
  riskStatus: string;
  blockedOnly: boolean;
}

interface ExportOptions {
  generatedAt: string;
  filters: SignalLifecycleExportFilters;
}

const CSV_COLUMNS = [
  "id",
  "signal_id",
  "symbol",
  "direction",
  "confidence",
  "decision",
  "risk_status",
  "blocked_reason",
  "dry_run",
  "auto_trade",
  "read_only",
  "supports_live_orders",
  "order_placed",
  "max_risk_per_trade",
  "audit_event_type",
  "generated_at",
  "step_ids",
  "step_statuses",
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
  return `mellytrade-signal-lifecycle-${timestampForFilename()}.${extension}`;
}

function safeRecord(record: SignalLifecycleRecord) {
  return {
    id: record.id,
    signal_id: record.signal_id,
    symbol: record.symbol,
    direction: record.direction,
    confidence: record.confidence,
    decision: record.decision,
    risk_status: record.risk_status,
    blocked_reason: record.blocked_reason,
    dry_run: record.dry_run,
    auto_trade: record.auto_trade,
    read_only: record.read_only,
    supports_live_orders: record.supports_live_orders,
    order_placed: record.order_placed,
    max_risk_per_trade: record.max_risk_per_trade,
    audit_event_type: record.audit_event_id,
    timestamp: record.timestamp,
    steps: record.steps.map((step) => ({
      id: step.key,
      label: step.label,
      status: step.status,
      message: step.detail,
      source: step.audit_event_id ?? record.audit_event_id,
      timestamp: record.timestamp,
    })),
  };
}

export function exportSignalLifecycleCsv(
  records: SignalLifecycleRecord[],
  { generatedAt }: ExportOptions,
) {
  const rows = records.map((record) => [
    record.id,
    record.signal_id,
    record.symbol,
    record.direction,
    record.confidence,
    record.decision,
    record.risk_status,
    record.blocked_reason ?? "",
    record.dry_run,
    record.auto_trade,
    record.read_only,
    record.supports_live_orders,
    record.order_placed,
    record.max_risk_per_trade,
    record.audit_event_id,
    generatedAt,
    record.steps.map((step) => step.key).join("|"),
    record.steps.map((step) => step.status).join("|"),
  ]);
  const csv = [
    CSV_COLUMNS.map(csvValue).join(","),
    ...rows.map((row) => row.map(csvValue).join(",")),
  ].join("\n");
  downloadFile(filename("csv"), csv, "text/csv;charset=utf-8");
}

export function exportSignalLifecycleJson(
  records: SignalLifecycleRecord[],
  { generatedAt, filters }: ExportOptions,
) {
  const payload = {
    generated_at: generatedAt,
    record_count: records.length,
    filters,
    read_only: true,
    dry_run: true,
    records: records.map(safeRecord),
  };
  downloadFile(
    filename("json"),
    JSON.stringify(payload, null, 2),
    "application/json;charset=utf-8",
  );
}
