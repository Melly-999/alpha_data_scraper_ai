import { useEffect, useState } from "react";

import { Button } from "../components/shared/Button";
import { Card } from "../components/shared/Card";
import { GaugeBar } from "../components/shared/GaugeBar";
import { Table } from "../components/shared/Table";
import { useRiskConfig, useRiskStatus, useRiskViolations } from "../hooks/useRisk";
import { apiPost, apiPut } from "../lib/api";
import type { EmergencyStopResponse, RiskConfig, RiskConfigUpdate } from "../types/api";

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

  async function saveConfig() {
    if (!form) {
      return;
    }
    const payload: RiskConfigUpdate = {
      max_risk_per_trade: form.max_risk_per_trade,
      min_confidence: form.min_confidence,
      cooldown_seconds: form.cooldown_seconds,
      max_open_positions: form.max_open_positions,
      auto_trade: form.auto_trade,
      dry_run: form.dry_run,
      allow_same_signal: form.allow_same_signal,
    };
    const next = await apiPut<RiskConfig, RiskConfigUpdate>("/risk/config", payload);
    setForm(next);
  }

  async function emergencyStop() {
    const response = await apiPost<EmergencyStopResponse>("/risk/emergency-stop");
    setForm(response.config);
  }

  return (
    <div className="page-grid">
      <Card
        title="Runtime Risk Config"
        right={
          <div className="header-actions">
            <Button onClick={saveConfig}>Save</Button>
            <Button tone="danger" onClick={emergencyStop}>
              Emergency Stop
            </Button>
          </div>
        }
      >
        {form ? (
          <div className="form-grid">
            <label>
              Max Risk / Trade
              <input
                type="number"
                step="0.1"
                value={form.max_risk_per_trade}
                onChange={(event) =>
                  setForm({ ...form, max_risk_per_trade: Number(event.target.value) })
                }
              />
            </label>
            <label>
              Min Confidence
              <input
                type="number"
                value={form.min_confidence}
                onChange={(event) =>
                  setForm({ ...form, min_confidence: Number(event.target.value) })
                }
              />
            </label>
            <label>
              Cooldown Seconds
              <input
                type="number"
                value={form.cooldown_seconds}
                onChange={(event) =>
                  setForm({ ...form, cooldown_seconds: Number(event.target.value) })
                }
              />
            </label>
            <label>
              Max Open Positions
              <input
                type="number"
                value={form.max_open_positions}
                onChange={(event) =>
                  setForm({ ...form, max_open_positions: Number(event.target.value) })
                }
              />
            </label>
            <label>
              Auto Trade
              <input
                type="checkbox"
                checked={form.auto_trade}
                disabled
                onChange={(event) =>
                  setForm({ ...form, auto_trade: event.target.checked })
                }
              />
            </label>
            <label>
              Dry Run
              <input
                type="checkbox"
                checked={form.dry_run}
                disabled
                onChange={(event) =>
                  setForm({ ...form, dry_run: event.target.checked })
                }
              />
            </label>
          </div>
        ) : null}
        <div className="stat-subtle">
          auto_trade stays off and dry_run stays on in Phase 2.
        </div>
      </Card>

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
        ) : null}
      </Card>

      <Card title="Risk Violations">
        {violations.data ? (
          <Table
            columns={[
              { key: "type", label: "Type", render: (row) => row.type },
              { key: "signal_ref", label: "Signal", render: (row) => row.signal_ref ?? "—" },
              { key: "reason", label: "Reason", render: (row) => row.reason },
            ]}
            rows={violations.data}
          />
        ) : null}
      </Card>
    </div>
  );
}
