import { Navigate, Route, Routes } from "react-router-dom";

import { TerminalPage } from "./pages/TerminalPage";
import { WatchlistPage } from "./pages/WatchlistPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/terminal" replace />} />
      <Route path="/terminal" element={<TerminalPage />} />
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
      <Route path="*" element={<Navigate to="/terminal" replace />} />
    </Routes>
  );
}
