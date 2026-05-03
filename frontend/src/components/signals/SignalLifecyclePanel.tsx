import { Badge } from "../shared/Badge";
import type {
  SignalLifecycleRecord,
  SignalLifecycleStepStatus,
} from "../../types/api";

function statusTone(
  status: SignalLifecycleStepStatus,
): "green" | "red" | "amber" | "blue" | "muted" {
  if (status === "passed" || status === "allowed") return "green";
  if (status === "blocked") return "red";
  if (status === "received") return "blue";
  if (status === "recorded") return "amber";
  return "muted";
}

function formatTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function SignalLifecyclePanel({
  records,
}: {
  records: SignalLifecycleRecord[];
}) {
  if (records.length === 0) {
    return <div className="state">No lifecycle records available.</div>;
  }

  return (
    <div className="signal-lifecycle-list">
      {records.map((record) => (
        <article className="signal-lifecycle-record" key={record.id}>
          <header className="signal-lifecycle-record-header">
            <div>
              <div className="card-kicker">{formatTime(record.timestamp)}</div>
              <strong>
                {record.symbol} {record.direction}
              </strong>
            </div>
            <div className="signal-lifecycle-badges">
              <Badge tone={record.decision === "dry_run_allowed" ? "green" : "amber"}>
                {record.decision}
              </Badge>
              <Badge tone="muted">{Math.round(record.confidence * 100)}%</Badge>
              <Badge tone="green">dry-run</Badge>
            </div>
          </header>

          <ol className="signal-lifecycle-steps">
            {record.steps.map((step) => (
              <li key={step.key}>
                <div className="signal-lifecycle-step-top">
                  <span>{step.label}</span>
                  <Badge tone={statusTone(step.status)}>{step.status}</Badge>
                </div>
                <p>{step.detail}</p>
              </li>
            ))}
          </ol>

          <footer className="signal-lifecycle-footer">
            <span>Decision {record.decision_id}</span>
            <span>Audit {record.audit_event_id}</span>
            <span>{record.order_placed ? "order placed" : "no order placed"}</span>
          </footer>
        </article>
      ))}
    </div>
  );
}
