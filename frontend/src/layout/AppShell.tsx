import type { ReactNode } from "react";

import type { HealthResponse, RiskConfig, SystemStatus } from "../types/api";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

interface AppShellProps {
  children: ReactNode;
  health: HealthResponse | null;
  systemStatus: SystemStatus | null;
  riskConfig: RiskConfig | null;
}

export function AppShell({
  children,
  health,
  systemStatus,
  riskConfig,
}: AppShellProps) {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <TopBar health={health} systemStatus={systemStatus} riskConfig={riskConfig} />
        <main className="page-content">{children}</main>
      </div>
    </div>
  );
}

