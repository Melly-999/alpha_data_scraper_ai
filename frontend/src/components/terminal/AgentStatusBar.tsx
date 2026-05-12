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
    <footer className="terminal-statusbar agent-statusbar">
      <span>SESSION</span>
      <span>
        {now.local} / UTC {now.utc}
      </span>
      <span>FEED {summary.backend.toUpperCase()}</span>
      <span>BROKER: IBKR-PAPER READ-ONLY</span>
      <span>AGENTS: {healthyAgents}/{agentCount} HEALTHY</span>
      <span>CPU 18% · MEM 41%</span>
      <span>v0.1.0</span>
      <span>{broker.status.toUpperCase()}</span>
    </footer>
  );
}
