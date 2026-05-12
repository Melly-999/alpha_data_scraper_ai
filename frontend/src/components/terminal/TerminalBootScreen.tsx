import { useEffect, useMemo, useState } from "react";

import { SafetyBadges } from "./SafetyBadges";

const bootLines = [
  "MELLYTRADE TERMINAL V1",
  "INSTITUTIONAL READ-ONLY WORKSTATION",
  "INITIALIZING MARKET DATA LAYER...",
  "LOADING AI WORKSPACE...",
  "STARTING AGENT ROSTER...",
  "CHECKING BROKER REGISTRY...",
  "SAFE-DISCONNECTED: ONLINE",
  "IBKR-PAPER: READ-ONLY",
  "RISK POLICY: MAX 1%",
  "READ ONLY ENABLED",
  "DRY RUN ACTIVE",
  "AUTO TRADE OFF",
  "LIVE ORDERS BLOCKED",
  "ORDER ROUTING: DISABLED",
  "EXECUTION SURFACE: NOT LOADED",
];

export function TerminalBootScreen() {
  const [progress, setProgress] = useState(10);

  useEffect(() => {
    const start = Date.now();
    const timer = window.setInterval(() => {
      const elapsed = Date.now() - start;
      const pct = Math.min(100, Math.round((elapsed / 1350) * 100));
      setProgress(pct);
      if (pct >= 100) {
        window.clearInterval(timer);
      }
    }, 60);

    return () => window.clearInterval(timer);
  }, []);

  const activeIndex = useMemo(() => {
    const ratio = progress / 100;
    return Math.min(bootLines.length - 1, Math.floor(ratio * bootLines.length));
  }, [progress]);

  return (
    <section
      className="terminal-boot-screen"
      aria-label="Terminal boot screen"
      aria-busy="true"
    >
      <div className="terminal-boot-panel">
        <div className="boot-hero">
          <p className="terminal-eyebrow">MellyTrade V1 Terminal</p>
          <h1>Institutional read-only workstation</h1>
          <p>
            Booting the AI workspace, broker registry, and safety overlays in
            read-only mode.
          </p>
        </div>

        <div className="boot-body">
          <div className="boot-lines" aria-label="Boot sequence">
            {bootLines.map((line, index) => (
              <div
                key={line}
                className={`boot-line ${
                  index < activeIndex
                    ? "done"
                    : index === activeIndex
                      ? "active"
                      : ""
                }`}
              >
                <span className="boot-dot" />
                <span>{line}</span>
              </div>
            ))}
          </div>

          <div className="boot-progress-card">
            <div className="boot-progress-head">
              <span>Boot progress</span>
              <strong>{progress}%</strong>
            </div>
            <p className="sr-only" aria-live="polite" role="status">
              Boot progress {progress} percent
            </p>
            <div className="boot-progress-track" aria-hidden="true">
              <span style={{ width: `${progress}%` }} />
            </div>
            <div className="boot-status-stack">
              <span>READ ONLY</span>
              <span>DRY RUN</span>
              <span>AUTO TRADE OFF</span>
              <span>LIVE ORDERS BLOCKED</span>
            </div>
          </div>
        </div>

        <SafetyBadges />
      </div>
    </section>
  );
}
