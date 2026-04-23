import { Card } from "../components/shared/Card";
import { useHealth } from "../hooks/useHealth";
import { useRiskConfig } from "../hooks/useRisk";
import { Badge } from "../components/shared/Badge";

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
            <div className="detail-row">
              <span>Repo Root</span>
              <strong>{health.data.workspace.repo_root}</strong>
            </div>
            <div className="detail-row">
              <span>Startup Mode</span>
              <strong>{health.data.workspace.startup_mode}</strong>
            </div>
            <div className="detail-row">
              <span>Dependencies</span>
              <div className="topbar-meta">
                <Badge tone={health.data.dependencies.mt5 ? "green" : "amber"}>
                  MT5
                </Badge>
                <Badge tone={health.data.dependencies.claude ? "green" : "muted"}>
                  Claude
                </Badge>
                <Badge tone={health.data.dependencies.news ? "green" : "muted"}>
                  News
                </Badge>
              </div>
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
