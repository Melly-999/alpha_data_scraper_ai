import { Card } from "../components/shared/Card";
import { useHealth } from "../hooks/useHealth";
import { useRiskConfig } from "../hooks/useRisk";

export function SettingsPage() {
  const health = useHealth();
  const riskConfig = useRiskConfig();

  return (
    <div className="page-grid">
      <Card title="Backend Metadata">
        {health.data ? (
          <div className="stack">
            <div className="detail-row">
              <span>Service</span>
              <strong>{health.data.service}</strong>
            </div>
            <div className="detail-row">
              <span>Version</span>
              <strong>{health.data.version}</strong>
            </div>
            <div className="detail-row">
              <span>Fallback Mode</span>
              <strong>{health.data.fallback_mode ? "Yes" : "No"}</strong>
            </div>
          </div>
        ) : null}
      </Card>
      <Card title="Effective Safety Config">
        {riskConfig.data ? (
          <pre className="config-dump">
            {JSON.stringify(riskConfig.data, null, 2)}
          </pre>
        ) : null}
      </Card>
    </div>
  );
}

