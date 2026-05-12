import { useMemo, useState } from "react";

import type { TerminalShellData } from "./TerminalShell";

type Agent = {
  name: string;
  role: string;
  health: "healthy" | "idle" | "watching";
  taskCount: number;
};

type TaskCard = {
  title: string;
  category: string;
  description: string;
  glyph: string;
};

const agents: Agent[] = [
  { name: "PlannerAgent", role: "Session strategist", health: "healthy", taskCount: 4 },
  { name: "MomentumAgent", role: "Trend and impulse review", health: "healthy", taskCount: 3 },
  { name: "MeanRevAgent", role: "Reversal and fade scanner", health: "watching", taskCount: 2 },
  { name: "OptionsAgent", role: "Structure and vol lens", health: "healthy", taskCount: 1 },
  { name: "MacroAgent", role: "Rates and regime context", health: "healthy", taskCount: 3 },
  { name: "EarningsAgent", role: "Event-driven read-throughs", health: "idle", taskCount: 2 },
  { name: "PairsAgent", role: "Relative value and hedges", health: "healthy", taskCount: 2 },
  { name: "SentimentAgent", role: "News and flow overlay", health: "watching", taskCount: 5 },
  { name: "RiskAgent", role: "Guardrail review and sizing", health: "healthy", taskCount: 6 },
];

const tasks: TaskCard[] = [
  {
    title: "Portfolio Stress Test",
    category: "RISK",
    description: "Simulate adverse moves and highlight concentration hotspots.",
    glyph: "RT",
  },
  {
    title: "Fed Path & Fixed Income",
    category: "MACRO",
    description: "Summarize rates, yields, and policy implications for the book.",
    glyph: "MK",
  },
  {
    title: "Nasdaq Momentum Review",
    category: "EQUITY",
    description: "Evaluate trend quality, breadth, and continuation risks.",
    glyph: "EQ",
  },
  {
    title: "Risk Check",
    category: "RISK",
    description: "Confirm the max risk <= 1% posture before any discretionary note.",
    glyph: "RC",
  },
  {
    title: "Signal Review",
    category: "NEWS",
    description: "Review advisory signals and separate setup quality from noise.",
    glyph: "SG",
  },
  {
    title: "Broker Status Check",
    category: "BROKER",
    description: "Read-only broker registry and paper status snapshot.",
    glyph: "BR",
  },
  {
    title: "Daily Market Brief",
    category: "NEWS",
    description: "Generate a session brief for the terminal without side effects.",
    glyph: "DB",
  },
];

const modeChips = ["EQUITY", "MACRO", "NEWS", "RISK", "BROKER", "DRY RUN"];

const tools = [
  "MARKET.SCAN",
  "PRICE.HISTORY",
  "OPTIONS.FLOW",
  "MACRO.CALENDAR",
  "BACKTEST.PREVIEW",
  "PORTFOLIO.READ",
  "RISK.GAUGE",
  "NEWS.SEARCH",
  "SENTIMENT.X",
  "LEVELS.COMPUTE",
  "LEDGER.AUDIT",
];

export function AIWorkspacePanel({ data }: { data: TerminalShellData }) {
  const [selectedAgent, setSelectedAgent] = useState<Agent>(agents[0]);
  const [selectedTask, setSelectedTask] = useState<TaskCard>(tasks[0]);
  const [draft, setDraft] = useState(
    'compare NVDA vs AVGO into earnings, risk-adjusted',
  );

  const activeAgents = useMemo(
    () => agents.filter((agent) => agent.health !== "idle").length,
    [],
  );

  return (
    <section className="terminal-panel ai-workspace-panel">
      <div className="panel-header">
        <span>AI Workspace</span>
        <span>advisory-only cockpit</span>
      </div>

      <div className="workspace-shell">
        <div className="workspace-topline">
          <div>
            <p className="terminal-eyebrow">AI Workspace</p>
            <h2>{selectedAgent.name}</h2>
            <p className="workspace-session">
              Session is open · {activeAgents} agents online · advisory mode
            </p>
          </div>
          <div className="workspace-summary">
            <div>
              <span>Backend</span>
              <strong>{data.summary.backend}</strong>
            </div>
            <div>
              <span>Broker</span>
              <strong>{data.broker.status}</strong>
            </div>
            <div>
              <span>Signals</span>
              <strong>{data.signals.length}</strong>
            </div>
            <div>
              <span>Positions</span>
              <strong>{data.positions.length}</strong>
            </div>
          </div>
        </div>

        <div className="workspace-grid">
          <aside className="workspace-roster">
            <div className="workspace-section-head">
              <span>Agent roster</span>
              <span>9/9 healthy</span>
            </div>
            {agents.map((agent) => (
              <button
                key={agent.name}
                type="button"
                className={`roster-item ${selectedAgent.name === agent.name ? "selected" : ""}`}
                onClick={() => setSelectedAgent(agent)}
              >
                <span className={`health-dot ${agent.health}`} />
                <div>
                  <strong>{agent.name}</strong>
                  <p>{agent.role}</p>
                </div>
                <small>{agent.taskCount}</small>
              </button>
            ))}
          </aside>

          <div className="workspace-main">
            <div className="workspace-title-row">
              <div>
                <span className="workspace-active-badge">ACTIVE</span>
                <span className="workspace-model-badge">MT-STRATEGIST-V3</span>
              </div>
              <div className="workspace-mini-pill">Selected: {selectedAgent.name}</div>
            </div>

            <div className="workspace-chip-row">
              {modeChips.map((chip) => (
                <span key={chip} className="workspace-chip">
                  {chip}
                </span>
              ))}
            </div>

            <div className="workspace-safety-banner">
              DRY RUN - outputs are advisory. No order routing. Human review
              required.
            </div>

            <div className="workspace-task-grid">
              {tasks.map((task) => (
                <article
                  key={task.title}
                  className={`workspace-task-card ${selectedTask.title === task.title ? "selected" : ""}`}
                >
                  <div className="workspace-task-top">
                    <span className="workspace-task-glyph">{task.glyph}</span>
                    <span className="workspace-task-category">{task.category}</span>
                  </div>
                  <strong>{task.title}</strong>
                  <p>{task.description}</p>
                  <span className="workspace-task-label">ADVISORY ONLY · NO EXECUTION</span>
                  <button type="button" className="workspace-task-select" onClick={() => setSelectedTask(task)}>
                    Select
                  </button>
                </article>
              ))}
            </div>

            <div className="workspace-selected-task">
              <div className="workspace-section-head">
                <span>Current task</span>
                <span>local select only</span>
              </div>
              <strong>{selectedTask.title}</strong>
              <p>{selectedTask.description}</p>
            </div>

            <div className="workspace-prompt-shell">
              <div className="workspace-section-head">
                <span>Prompt</span>
                <span>visual only</span>
              </div>
              <textarea
                className="workspace-prompt"
                aria-label="Agent prompt preview"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                spellCheck={false}
              />
            </div>
          </div>

          <aside className="workspace-right-rail">
            <section className="workspace-rail-section">
              <div className="workspace-section-head">
                <span>Backtest Equity Preview</span>
                <span>read-only</span>
              </div>
              <div className="rail-metric">
                <span>Win rate</span>
                <strong>{data.backtest.win_rate}%</strong>
              </div>
              <div className="rail-metric">
                <span>Profit factor</span>
                <strong>{data.backtest.profit_factor.toFixed(2)}</strong>
              </div>
              <div className="rail-metric">
                <span>Drawdown</span>
                <strong>{data.backtest.max_drawdown_pct}%</strong>
              </div>
            </section>

            <section className="workspace-rail-section">
              <div className="workspace-section-head">
                <span>Available Read-Only Tools</span>
                <span>visual labels</span>
              </div>
              <div className="tool-chip-grid">
                {tools.map((tool) => (
                  <span key={tool} className="tool-chip">
                    {tool}
                  </span>
                ))}
              </div>
            </section>

            <section className="workspace-rail-section">
              <div className="workspace-section-head">
                <span>Today's Action Queue</span>
                <span>review only</span>
              </div>
              <div className="action-queue">
                {[
                  "Portfolio Stress Test",
                  "Broker Status Check",
                  "Signal Review",
                  "Daily Market Brief",
                ].map((item) => (
                  <div key={item} className="queue-row">
                    <span>{item}</span>
                    <strong>Review</strong>
                  </div>
                ))}
              </div>
            </section>
          </aside>
        </div>
      </div>
    </section>
  );
}
