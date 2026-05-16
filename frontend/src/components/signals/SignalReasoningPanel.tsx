import { useState } from "react";

import { Badge } from "../shared/Badge";
import type { RiskGateResult, SignalDetail, SignalReasoning } from "../../types/api";

/**
 * DATA-002 — Explainable AI reasoning panel.
 *
 * Read-only, collapsible. Lays out the "why this signal" narrative,
 * the confidence breakdown, the human-review framing, and the
 * triggered risk gates. Every variant carries a safety badge so the
 * panel cannot be mistaken for an execution surface:
 *
 *   - DRY RUN ONLY       — always present
 *   - READ ONLY          — always present
 *   - HUMAN REVIEW REQUIRED — present whenever confidence < 70% or blocked
 *   - RISK BLOCKED       — present whenever a risk gate failed
 *
 * No buttons execute trades. No mutation. No POST/PUT/PATCH/DELETE.
 */

const REVIEW_THRESHOLD = 70;

function confidenceBand(confidence: number): {
  label: string;
  tone: "green" | "amber" | "red";
} {
  if (confidence >= 80) return { label: "high", tone: "green" };
  if (confidence >= REVIEW_THRESHOLD) return { label: "meets review", tone: "green" };
  if (confidence >= 50) return { label: "below review threshold", tone: "amber" };
  return { label: "low", tone: "red" };
}

function gateTone(passed: boolean): "green" | "red" {
  return passed ? "green" : "red";
}

function GateRow({ gate }: { gate: RiskGateResult }) {
  return (
    <li className="reasoning-gate-row">
      <span className="reasoning-gate-name">{gate.gate}</span>
      <Badge tone={gateTone(gate.passed)}>
        {gate.passed ? "PASS" : "BLOCK"}
      </Badge>
      {gate.detail ? (
        <span className="reasoning-gate-detail">{gate.detail}</span>
      ) : null}
    </li>
  );
}

export function SignalReasoningPanel({
  detail,
  reasoning,
}: {
  detail: SignalDetail;
  reasoning: SignalReasoning | null;
}) {
  const [expanded, setExpanded] = useState(true);
  const blocked = detail.blocked;
  const reviewRequired = detail.confidence < REVIEW_THRESHOLD || blocked;
  const failedGates = (reasoning?.risk_gate_results ?? []).filter(
    (gate) => !gate.passed,
  );
  const passedGates = (reasoning?.risk_gate_results ?? []).filter(
    (gate) => gate.passed,
  );
  const band = confidenceBand(detail.confidence);

  return (
    <section
      className="signal-reasoning-panel"
      aria-label="Signal reasoning (read-only)"
    >
      <header className="signal-reasoning-header">
        <div>
          <strong>AI Reasoning</strong>
          <p className="dashboard-muted">
            Display-only explanation. No order is placed from this panel.
          </p>
        </div>
        <button
          type="button"
          className="signal-reasoning-toggle"
          aria-expanded={expanded}
          onClick={() => setExpanded((current) => !current)}
        >
          {expanded ? "Collapse" : "Expand"}
        </button>
      </header>

      <div className="signal-reasoning-badges">
        <Badge tone="green">DRY RUN ONLY</Badge>
        <Badge tone="green">READ ONLY</Badge>
        {reviewRequired ? (
          <Badge tone="amber">HUMAN REVIEW REQUIRED</Badge>
        ) : null}
        {blocked ? <Badge tone="red">RISK BLOCKED</Badge> : null}
      </div>

      {expanded ? (
        <div className="signal-reasoning-body">
          <div className="signal-reasoning-section">
            <h4>Why this signal?</h4>
            <p>{detail.reasoning || "No narrative reasoning available."}</p>
            {reasoning?.technical_factors?.length ? (
              <ul className="signal-reasoning-list">
                {reasoning.technical_factors.map((factor) => (
                  <li key={factor}>{factor}</li>
                ))}
              </ul>
            ) : null}
          </div>

          <div className="signal-reasoning-section">
            <h4>Confidence breakdown</h4>
            <div className="signal-reasoning-confidence">
              <span className="signal-reasoning-confidence-value">
                {detail.confidence}%
              </span>
              <Badge tone={band.tone}>{band.label}</Badge>
              <span className="dashboard-muted">
                Review threshold {REVIEW_THRESHOLD}%
              </span>
            </div>
            {detail.confidence < REVIEW_THRESHOLD ? (
              <p className="dashboard-muted">
                Confidence sits below the {REVIEW_THRESHOLD}% review threshold.
                Even if all risk gates passed, this signal would require manual
                human review before any hypothetical execution.
              </p>
            ) : (
              <p className="dashboard-muted">
                Confidence meets the {REVIEW_THRESHOLD}% review threshold.
                In live mode this would still require a human-approved order;
                dry-run remains the only path active.
              </p>
            )}
          </div>

          {blocked ? (
            <div className="signal-reasoning-section">
              <h4>Why blocked?</h4>
              <p>
                <Badge tone="red">{detail.blocked_reason ?? "BLOCKED"}</Badge>{" "}
                {detail.blocked_reason
                  ? "The signal was blocked at the named gate; no order was placed."
                  : "The signal was blocked by a risk gate; no order was placed."}
              </p>
            </div>
          ) : null}

          <div className="signal-reasoning-section">
            <h4>Risk gates triggered</h4>
            {failedGates.length === 0 && passedGates.length === 0 ? (
              <p className="dashboard-muted">
                No risk gate results available for this signal.
              </p>
            ) : (
              <>
                {failedGates.length > 0 ? (
                  <ul className="signal-reasoning-gates">
                    {failedGates.map((gate) => (
                      <GateRow key={`fail-${gate.gate}`} gate={gate} />
                    ))}
                  </ul>
                ) : null}
                {passedGates.length > 0 ? (
                  <details className="signal-reasoning-passed">
                    <summary>
                      {passedGates.length} gate
                      {passedGates.length === 1 ? "" : "s"} passed
                    </summary>
                    <ul className="signal-reasoning-gates">
                      {passedGates.map((gate) => (
                        <GateRow key={`pass-${gate.gate}`} gate={gate} />
                      ))}
                    </ul>
                  </details>
                ) : null}
              </>
            )}
          </div>

          <div className="signal-reasoning-section">
            <h4>Human review required</h4>
            <p className="dashboard-muted">
              This terminal never auto-executes. Every signal — even
              dry-run-allowed ones — is surfaced for human review only.
              The execution path is not wired up:{" "}
              <code>autotrade=false</code>, <code>dry_run=true</code>,{" "}
              <code>read_only=true</code>, <code>live_orders_blocked=true</code>.
            </p>
          </div>

          {reasoning?.claude_response ? (
            <div className="signal-reasoning-section">
              <h4>Claude validation</h4>
              <p className="dashboard-muted">{reasoning.claude_response}</p>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
