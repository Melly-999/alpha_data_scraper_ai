import type { RiskPolicy, RiskStatus } from "../../lib/terminalApi";

type RiskGuardrailsCardProps = {
  policy: RiskPolicy;
  status: RiskStatus;
};

export function RiskGuardrailsCard({ policy, status }: RiskGuardrailsCardProps) {
  const rows = [
    ["Max risk per trade", `${status.max_risk_per_trade_pct}%`],
    ["dry_run", String(status.dry_run)],
    ["auto_trade", String(status.auto_trade)],
    ["read_only", String(status.read_only)],
    ["Stop loss required", String(status.stop_loss_required)],
    ["Take profit required", String(status.take_profit_required)],
    ["Live orders blocked", String(status.live_orders_blocked)],
    ["Min confidence", `${policy.min_confidence}%`],
    ["Execution enabled", String(policy.execution_enabled)],
  ];

  return (
    <section id="risk" className="terminal-panel">
      <div className="panel-header">
        <span>Risk guardrails</span>
        <span>enforced</span>
      </div>
      <div className="guardrail-list">
        {rows.map(([label, value]) => (
          <div key={label} className="guardrail-row">
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
