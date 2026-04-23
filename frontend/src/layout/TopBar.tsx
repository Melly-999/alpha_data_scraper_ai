import { Badge } from "../components/shared/Badge";
import type { HealthResponse, RiskConfig, SystemStatus } from "../types/api";

interface TopBarProps {
  health: HealthResponse | null;
  systemStatus: SystemStatus | null;
  riskConfig: RiskConfig | null;
}

export function TopBar({ health, systemStatus, riskConfig }: TopBarProps) {
  return (
    <header className="topbar">
      <div>
        <div className="eyebrow">SYSTEM STATUS</div>
        <div className="topbar-title">
          {systemStatus?.symbol ?? "EURUSD"} · {systemStatus?.mode ?? "DRY_RUN"}
        </div>
      </div>
      <div className="topbar-meta">
        <Badge tone={health?.fallback_mode ? "amber" : "green"}>
          {health?.fallback_mode ? "Fallback Mode" : "Live Dependencies"}
        </Badge>
        <Badge tone={riskConfig?.emergency_pause ? "red" : "green"}>
          {riskConfig?.emergency_pause ? "Emergency Stop" : "Safe Dry Run"}
        </Badge>
      </div>
    </header>
  );
}

