import { useMemo, useState } from "react";

import type { AlertItem, AlertSeverity } from "../types/melly";
import { Badge } from "./shared/Badge";
import { Card } from "./shared/Card";

type AlertFilter = "";

const SEVERITY_OPTIONS: Array<{ value: AlertFilter | AlertSeverity; label: string }> = [
  { value: "", label: "All severities" },
  { value: "success", label: "Success" },
  { value: "info", label: "Info" },
  { value: "warning", label: "Warning" },
  { value: "error", label: "Error" },
];

function severityTone(
  severity: AlertSeverity,
): "green" | "amber" | "red" | "blue" | "muted" {
  switch (severity) {
    case "success":
      return "green";
    case "info":
      return "blue";
    case "warning":
      return "amber";
    case "error":
      return "red";
    default:
      return "muted";
  }
}

function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function categoryLabel(category: string): string {
  return category.replace(/_/g, " ");
}

function formatMetadata(metadata: AlertItem["metadata"]): string | null {
  if (!metadata || Object.keys(metadata).length === 0) {
    return null;
  }
  try {
    return JSON.stringify(metadata);
  } catch {
    return null;
  }
}

interface AlertCenterProps {
  alerts: AlertItem[];
  loading: boolean;
  error: string | null;
}

export function AlertCenter({ alerts, loading, error }: AlertCenterProps) {
  const [severity, setSeverity] = useState<"" | AlertSeverity>("");
  const [category, setCategory] = useState("");

  const categories = useMemo(
    () => Array.from(new Set(alerts.map((alert) => alert.category))).sort(),
    [alerts],
  );

  const visibleAlerts = useMemo(
    () =>
      alerts.filter((alert) => {
        if (severity && alert.severity !== severity) {
          return false;
        }
        if (category && alert.category !== category) {
          return false;
        }
        return true;
      }),
    [alerts, category, severity],
  );

  return (
    <Card
      title="Alert Center"
      right={
        <Badge tone={error ? "amber" : "blue"}>
          {visibleAlerts.length} alerts
        </Badge>
      }
    >
      <div className="alert-center-controls">
        <label>
          <span>Severity</span>
          <select
            value={severity}
            onChange={(event) =>
              setSeverity(event.target.value as "" | AlertSeverity)
            }
          >
            {SEVERITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Category</span>
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          >
            <option value="">All categories</option>
            {categories.map((item) => (
              <option key={item} value={item}>
                {categoryLabel(item)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading && alerts.length === 0 ? (
        <div className="state">Loading alerts...</div>
      ) : null}
      {error && alerts.length === 0 ? (
        <div className="state error">{error}</div>
      ) : null}
      {!loading && !error && visibleAlerts.length === 0 ? (
        <div className="state">No alerts match the selected filters.</div>
      ) : null}

      <div className="alert-center-list">
        {visibleAlerts.map((alert) => {
          const metadata = formatMetadata(alert.metadata);
          return (
            <article key={alert.id} className="alert-center-row">
              <div className="alert-center-time">
                {formatTimestamp(alert.timestamp)}
              </div>
              <div className="alert-center-main">
                <div className="alert-center-heading">
                  <Badge tone={severityTone(alert.severity)}>
                    {alert.severity}
                  </Badge>
                  <Badge tone="muted">{categoryLabel(alert.category)}</Badge>
                  {alert.symbol ? (
                    <span className="dashboard-symbol">{alert.symbol}</span>
                  ) : null}
                </div>
                <div className="alert-center-title">{alert.title}</div>
                <div className="dashboard-muted">{alert.message}</div>
                {metadata ? (
                  <div className="alert-center-metadata">{metadata}</div>
                ) : null}
              </div>
              <div className="alert-center-source">
                <span>{alert.source}</span>
                <Badge tone={alert.read_only ? "green" : "red"}>
                  read_only={String(alert.read_only)}
                </Badge>
              </div>
            </article>
          );
        })}
      </div>
    </Card>
  );
}
