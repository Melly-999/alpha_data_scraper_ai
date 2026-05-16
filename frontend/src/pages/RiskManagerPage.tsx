import { useEffect, useState } from "react";

import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { GaugeBar } from "../components/shared/GaugeBar";
import { Table } from "../components/shared/Table";
import { useRiskConfig, useRiskStatus, useRiskViolations } from "../hooks/useRisk";
import type { RiskConfig } from "../types/api";

export function RiskManagerPage() {
  const riskConfig = useRiskConfig();
  const riskStatus = useRiskStatus();
  const violations = useRiskViolations();
  const [form, setForm] = useState<RiskConfig | null>(null);

  useEffect(() => {
    if (riskConfig.data) {
      setForm(riskConfig.data);
    }
  }, [riskConfig.data]);

  return (
    <div className="page-grid passive-page">
      <section className="page-header">
        <div>
          <div className="eyebrow">Risk Manager</div>
          <h1 className="page-title">Execution Guardrails</h1>
          <div className="dashboard-muted">Current backend-enforced risk posture.</div>
        </div>
        <div className="page-header-meta">
          <Badge tone={form?.dry_run ?? true ? "blue" : "red"}>
            {(form?.dry_run ?? true) ? "DRY RUN" : "LIVE"}
          </Badge>
          <Badge tone={form?.auto_trade ? "red" : "muted"}>
            {form?.auto_trade ? "AUTO TRADE ON" : "AUTO TRADE OFF"}
          </Badge>
          <Badge tone={form?.emergency_pause ? "red" : "green"}>
            {form?.emergency_pause ? "EMERGENCY PAUSE" : "PAUSE CLEAR"}
          </Badge>
        </div>
      </section>

      {riskStatus.data ? (
        <div className="passive-metric-grid">
          <div className="passive-status-card">
            <span>Daily loss used</span>
            <strong>
              {riskStatus.data.daily_loss_used.toFixed(2)} /{" "}
              {riskStatus.data.daily_loss_limit.toFixed(2)}
            </strong>
          </div>
          <div className="passive-status-card">
            <span>Drawdown</span>
            <strong>
              {riskStatus.data.drawdown_current.toFixed(2)} /{" "}
              {riskStatus.data.drawdown_limit.toFixed(2)}
            </strong>
          </div>
          <div className="passive-status-card">
            <span>Open positions</span>
            <strong>
              {riskStatus.data.open_positions} /{" "}
              {riskStatus.data.open_positions_limit}
            </strong>
          </div>
          <div className="passive-status-card">
            <span>Blocked / executed</span>
            <strong>
              {riskStatus.data.trades_blocked} / {riskStatus.data.trades_executed}
            </strong>
          </div>
        </div>
      ) : null}

      <Card
        title="Runtime Risk Config"
        right={
          <Badge tone="muted">Read-only from frontend</Badge>
        }
      >
        {form ? (
          <div className="risk-config-layout">
            <div className="form-grid">
              <label>
                Max Risk / Trade
                <input type="number" step="0.1" value={form.max_risk_per_trade} readOnly />
              </label>
              <label>
                Min Confidence
                <input type="number" value={form.min_confidence} readOnly />
              </label>
              <label>
                Cooldown Seconds
                <input type="number" value={form.cooldown_seconds} readOnly />
              </label>
              <label>
                Max Open Positions
                <input type="number" value={form.max_open_positions} readOnly />
              </label>
              <label>
                Auto Trade
                <input type="checkbox" checked={form.auto_trade} disabled />
              </label>
              <label>
                Dry Run
                <input type="checkbox" checked={form.dry_run} disabled />
              </label>
            </div>

            <div className="status-row-list risk-policy-list">
              <div className="status-row">
                <span>Max daily loss</span>
                <strong>{form.max_daily_loss}</strong>
              </div>
              <div className="status-row">
                <span>Max drawdown</span>
                <strong>{form.max_drawdown}</strong>
              </div>
              <div className="status-row">
                <span>Min R:R</span>
                <strong>{form.min_rr}</strong>
              </div>
              <div className="status-row">
                <span>Allow same signal</span>
                <Badge tone={form.allow_same_signal ? "amber" : "green"}>
                  {form.allow_same_signal ? "Allowed" : "Blocked"}
                </Badge>
              </div>
            </div>
          </div>
        ) : null}
      </Card>

      <div className="two-column">
        <Card title="Risk Status">
          {riskStatus.data ? (
            <div className="stack">
              <GaugeBar
                label="Daily Loss"
                value={riskStatus.data.daily_loss_used}
                max={riskStatus.data.daily_loss_limit}
              />
              <GaugeBar
                label="Drawdown"
                value={riskStatus.data.drawdown_current}
                max={riskStatus.data.drawdown_limit}
              />
            </div>
          ) : (
            <div className="state">Risk status unavailable</div>
          )}
        </Card>

        <Card
          title="Risk Violations"
          right={<Badge tone="amber">{violations.data?.length ?? 0} total</Badge>}
        >
          {violations.data ? (
            <Table
              columns={[
                { key: "type", label: "Type", render: (row) => row.type },
                {
                  key: "signal_ref",
                  label: "Signal",
                  render: (row) => row.signal_ref ?? "-",
                },
                { key: "reason", label: "Reason", render: (row) => row.reason },
              ]}
              rows={violations.data}
            />
          ) : null}
        </Card>
      </div>
    </div>
  );
}
