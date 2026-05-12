import { useEffect, useState } from "react";

import type { IBKRStatus, TerminalSummary } from "../../lib/terminalApi";

type AgentStatusBarProps = {
  summary: TerminalSummary;
  broker: IBKRStatus;
  agentCount: number;
  healthyAgents: number;
};

function formatClock(date: Date) {
  return {
    local: date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }),
    utc: date.toLocaleTimeString("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
      timeZone: "UTC",
    }),
  };
}

export function AgentStatusBar({
  summary,
  broker,
  agentCount,
  healthyAgents,
}: AgentStatusBarProps) {
  const [now, setNow] = useState(() => formatClock(new Date()));

  useEffect(() => {
    const timer = window.setInterval(() => {
      setNow(formatClock(new Date()));
    }, 30_000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <footer className="terminal-statusbar agent-statusbar" aria-label="Terminal status bar">
      <span className="agent-status-item">SESSION</span>
      <span className="agent-status-item">
        {now.local} / UTC {now.utc}
      </span>
      <span className="agent-status-item">FEED {summary.backend.toUpperCase()}</span>
      <span className="agent-status-item">BROKER: IBKR-PAPER READ-ONLY</span>
      <span className="agent-status-item">AGENTS: {healthyAgents}/{agentCount} HEALTHY</span>
      <span className="agent-status-item">CPU 18% · MEM 41%</span>
      <span className="agent-status-item">v0.1.0</span>
      <span className="agent-status-item">{broker.status.toUpperCase()}</span>
    </footer>
  );
}
