import { useCallback, useEffect, useMemo, useState } from "react";

import {
  getScannerPreview,
  getScannerUniverses,
} from "../../lib/scannerPreviewApi";
import type {
  SignalScannerAction,
  SignalScannerBatch,
  SignalUniversePreset,
} from "../../lib/scannerPreviewApi";
import type { TerminalShellData } from "./TerminalShell";
import { PaperSandboxActivityRail } from "./PaperSandboxActivityRail";
import { PaperSandboxPreviewPanel } from "./PaperSandboxPreviewPanel";
import { PaperTicketPreviewPanel } from "./PaperTicketPreviewPanel";

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

function formatScannerAction(action: SignalScannerAction): string {
  return action.replace(/_/g, " ");
}

function formatScannerConfidence(confidence: number): string {
  return `${Math.round(confidence)}%`;
}

/** Returns the CSS modifier class that color-codes the action chip. */
const SCANNER_ACTION_CLASS: Record<SignalScannerAction, string> = {
  WATCH:       "scanner-action--watch",
  HOLD:        "scanner-action--hold",
  LONG_SETUP:  "scanner-action--long-setup",
  SHORT_SETUP: "scanner-action--short-setup",
  NO_TRADE:    "scanner-action--no-trade",
} as const;

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
  const promptId = "workspace-prompt-draft";

  const activeAgents = useMemo(
    () => agents.filter((agent) => agent.health !== "idle").length,
    [],
  );

  // SIG-UNIVERSE-002 — Universe selector state (read-only, display-only, no execution)
  const [universePresets, setUniversePresets] = useState<SignalUniversePreset[]>([]);
  const [selectedUniverse, setSelectedUniverse] = useState<string>("");
  const [localScannerBatch, setLocalScannerBatch] = useState<SignalScannerBatch>(
    data.scannerPreview,
  );
  const [universeLoading, setUniverseLoading] = useState(false);

  // Fetch available universe presets on mount — GET-only, no side effects
  useEffect(() => {
    let cancelled = false;
    getScannerUniverses().then((response) => {
      if (!cancelled) {
        setUniversePresets(response.universes);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  // Re-fetch scanner preview when the universe selection changes
  const handleUniverseChange = useCallback(
    async (universeName: string) => {
      setSelectedUniverse(universeName);
      if (!universeName) return;
      setUniverseLoading(true);
      try {
        const batch = await getScannerPreview({ universe: universeName });
        setLocalScannerBatch(batch);
      } finally {
        setUniverseLoading(false);
      }
    },
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
          <aside className="workspace-roster" aria-label="AI agent roster">
            <div className="workspace-section-head">
              <span>Agent roster</span>
              <span>9/9 healthy</span>
            </div>
            {agents.map((agent) => (
              <button
                key={agent.name}
                type="button"
                className={`roster-item ${selectedAgent.name === agent.name ? "selected" : ""}`}
                aria-pressed={selectedAgent.name === agent.name}
                aria-label={`Select ${agent.name}, ${agent.role}, ${agent.taskCount} open tasks`}
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

          <div className="workspace-main" aria-label="AI workspace tasks and prompt">
            <div className="workspace-title-row">
              <div>
                <span className="workspace-active-badge">ACTIVE</span>
                <span className="workspace-model-badge">MT-STRATEGIST-V3</span>
              </div>
              <div className="workspace-mini-pill" aria-live="polite">
                Selected: {selectedAgent.name}
              </div>
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
                  aria-label={`${task.title} advisory task`}
                >
                  <div className="workspace-task-top">
                    <span className="workspace-task-glyph">{task.glyph}</span>
                    <span className="workspace-task-category">{task.category}</span>
                  </div>
                  <strong>{task.title}</strong>
                  <p>{task.description}</p>
                  <span className="workspace-task-label">ADVISORY ONLY · NO EXECUTION</span>
                  <button
                    type="button"
                    className="workspace-task-select"
                    aria-pressed={selectedTask.title === task.title}
                    aria-label={`Select ${task.title} advisory task`}
                    onClick={() => setSelectedTask(task)}
                  >
                    Select
                  </button>
                </article>
              ))}
            </div>

            <section className="workspace-rail-section workspace-scanner-preview">
              <div className="workspace-section-head">
                <span>Scanner Preview</span>
                <span>GET-only · advisory only</span>
              </div>
              <p className="workspace-scanner-copy">
                Dry-run only. Human review required. No order routing.
              </p>
              <div className="scanner-badge-row" aria-label="Scanner preview safety notes">
                <span className="workspace-chip">DRY RUN</span>
                <span className="workspace-chip">HUMAN REVIEW</span>
                <span className="workspace-chip">NO ORDER ROUTING</span>
              </div>

              {universePresets.length > 0 && (
                <div className="universe-selector-row" aria-label="Scanner universe selector">
                  <label
                    className="universe-selector-label"
                    htmlFor="scanner-universe-select"
                  >
                    Universe
                  </label>
                  <select
                    id="scanner-universe-select"
                    className="universe-selector-select"
                    value={selectedUniverse}
                    onChange={(e) => { void handleUniverseChange(e.target.value); }}
                    aria-label="Select scanner universe — display only, advisory"
                    disabled={universeLoading}
                  >
                    <option value="">Default symbols</option>
                    {universePresets.map((preset) => (
                      <option key={preset.name} value={preset.name}>
                        {preset.label} ({preset.item_count})
                      </option>
                    ))}
                  </select>
                  {universeLoading && (
                    <span className="universe-selector-loading" aria-live="polite">
                      Loading…
                    </span>
                  )}
                </div>
              )}

              {localScannerBatch.results.length > 0 ? (
                <div className="scanner-preview-grid" aria-label="Scanner preview results">
                  {localScannerBatch.results.map((result) => (
                    <article
                      key={`${result.symbol}-${result.timestamp}`}
                      className={`scanner-preview-card${result.action === "NO_TRADE" ? " scanner-preview-card--no-trade" : ""}`}
                      aria-label={`${result.symbol} advisory setup — ${formatScannerAction(result.action)}`}
                    >
                      <div className="scanner-preview-topline">
                        <div>
                          <p className="terminal-eyebrow">Advisory scanner output</p>
                          <strong>{result.symbol}</strong>
                        </div>
                        <span
                          className={`scanner-preview-action ${SCANNER_ACTION_CLASS[result.action]}`}
                        >
                          {formatScannerAction(result.action)}
                        </span>
                      </div>
                      <div className="scanner-preview-metrics">
                        <span>Confidence</span>
                        <strong>{formatScannerConfidence(result.confidence)}</strong>
                      </div>
                      <div
                        className="scanner-conf-bar"
                        role="meter"
                        aria-valuenow={result.confidence}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-label={`Confidence ${result.confidence}%`}
                      >
                        <span style={{ width: `${result.confidence}%` }} />
                      </div>
                      <p className="scanner-preview-reason">{result.reason}</p>
                      <div className="scanner-preview-badges">
                        <span className="scanner-preview-badge">DRY RUN</span>
                        <span className="scanner-preview-badge">HUMAN REVIEW</span>
                        <span className="scanner-preview-badge">POLICY GATE</span>
                      </div>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="scanner-preview-empty" aria-live="polite">
                  Scanner preview unavailable or empty. Advisory mode remains active.
                </div>
              )}
            </section>

            <PaperSandboxPreviewPanel />

            <PaperSandboxActivityRail />

            <PaperTicketPreviewPanel />

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
              <label className="workspace-prompt-label" htmlFor={promptId}>
                Advisory prompt draft
              </label>
              <p className="workspace-prompt-copy">
                Local draft only. No backend mutation, no order routing, and no
                LLM/API call is sent from this panel yet.
              </p>
              <textarea
                className="workspace-prompt"
                id={promptId}
                aria-label="Advisory prompt draft"
                aria-describedby={`${promptId}-help`}
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                spellCheck={false}
              />
              <p id={`${promptId}-help`} className="workspace-prompt-help">
                Advisory prompt preview. No execution surface is loaded.
              </p>
            </div>
          </div>

          <aside className="workspace-right-rail" aria-label="AI workspace read-only rail">
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
