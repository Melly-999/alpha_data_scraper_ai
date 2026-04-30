import { AlertCenter } from "../components/AlertCenter";
import { Badge } from "../components/shared/Badge";
import { useAlerts } from "../hooks/useAlerts";

export function AlertsPage() {
  const { data, loading, error } = useAlerts({ limit: 200 });
  const alerts = data ?? [];
  const safetyAlerts = alerts.filter((alert) => alert.category === "safety");
  const riskAlerts = alerts.filter(
    (alert) =>
      alert.category === "risk_gate_failed" ||
      alert.category === "cooldown_active",
  );

  return (
    <div className="page-grid passive-page">
      <div className="passive-main">
        <section className="page-header">
          <div>
            <div className="eyebrow">Alert Center</div>
            <h1 className="page-title">Read-only trader alerts</h1>
            <div className="dashboard-muted">
              Safety posture, risk gate, cooldown, and placeholder market-event
              alerts derived from existing backend state.
            </div>
          </div>
          <div className="page-header-meta">
            <Badge tone="green">{safetyAlerts.length} safety</Badge>
            <Badge tone={riskAlerts.length > 0 ? "amber" : "muted"}>
              {riskAlerts.length} risk/cooldown
            </Badge>
            <Badge tone="green">read-only</Badge>
          </div>
        </section>

        <AlertCenter alerts={alerts} loading={loading} error={error} />
      </div>
    </div>
  );
}
