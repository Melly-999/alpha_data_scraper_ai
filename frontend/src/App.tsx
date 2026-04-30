import { Navigate, Route, Routes } from "react-router-dom";

import { useDashboard } from "./hooks/useDashboard";
import { useHealth } from "./hooks/useHealth";
import { useRiskConfig } from "./hooks/useRisk";
import { AppShell } from "./layout/AppShell";
import { AlertsPage } from "./pages/AlertsPage";
import { AuditTrailPage } from "./pages/AuditTrailPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LogsPage } from "./pages/LogsPage";
import { MT5BridgePage } from "./pages/MT5BridgePage";
import { PositionsPage } from "./pages/PositionsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { RiskManagerPage } from "./pages/RiskManagerPage";
import { SettingsPage } from "./pages/SettingsPage";
import { SignalsPage } from "./pages/SignalsPage";
import { TradeBlotterPage } from "./pages/TradeBlotterPage";
import { WatchlistPage } from "./pages/WatchlistPage";

export default function App() {
  const health = useHealth();
  const dashboard = useDashboard();
  const riskConfig = useRiskConfig();

  return (
    <AppShell
      health={health.data}
      systemStatus={dashboard.data?.system_status ?? null}
      riskConfig={riskConfig.data ?? null}
    >
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/watchlist" element={<WatchlistPage />} />
        <Route path="/signals" element={<SignalsPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/audit" element={<AuditTrailPage />} />
        <Route path="/positions" element={<PositionsPage />} />
        <Route path="/blotter" element={<TradeBlotterPage />} />
        <Route path="/risk" element={<RiskManagerPage />} />
        <Route path="/mt5" element={<MT5BridgePage />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </AppShell>
  );
}

