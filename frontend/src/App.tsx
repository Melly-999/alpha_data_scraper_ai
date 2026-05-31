import { Navigate, Route, Routes } from "react-router-dom";

import { TerminalPage } from "./pages/TerminalPage";
import { PaperRunPreviewPage } from "./pages/PaperRunPreviewPage";
import { WatchlistPage } from "./pages/WatchlistPage";
import { MobileAppPage } from "./pages/MobileAppPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/terminal" replace />} />
      <Route path="/terminal" element={<TerminalPage />} />
      <Route path="/terminal/open-design-tabs" element={<TerminalPage />} />
      <Route path="/terminal/paper-run-preview" element={<PaperRunPreviewPage />} />
      <Route path="/dashboard" element={<Navigate to="/terminal" replace />} />
      <Route path="/markets" element={<TerminalPage />} />
      <Route path="/global" element={<Navigate to="/markets" replace />} />
      <Route path="/watchlist" element={<WatchlistPage />} />
      <Route path="/workspace" element={<TerminalPage />} />
      <Route path="/signals" element={<TerminalPage />} />
      <Route path="/risk" element={<TerminalPage />} />
      <Route path="/brokers" element={<TerminalPage />} />
      <Route path="/portfolio" element={<TerminalPage />} />
      <Route path="/positions" element={<Navigate to="/portfolio" replace />} />
      <Route path="/audit" element={<TerminalPage />} />
      <Route path="/reports" element={<Navigate to="/audit" replace />} />
      <Route path="/settings" element={<TerminalPage />} />
      <Route path="/mobile" element={<MobileAppPage />} />
      <Route path="*" element={<Navigate to="/terminal" replace />} />
    </Routes>
  );
}
