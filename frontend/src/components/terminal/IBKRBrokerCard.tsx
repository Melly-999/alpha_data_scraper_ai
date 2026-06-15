import type { IBKRStatus } from "../../lib/terminalApi";

type IBKRBrokerCardProps = {
  broker: IBKRStatus;
};

export function IBKRBrokerCard({ broker }: IBKRBrokerCardProps) {
  const permissions = [
    ["Market data", broker.permissions.market_data],
    ["Account read", broker.permissions.account_read],
    ["Positions read", broker.permissions.positions_read],
    ["Orders", broker.permissions.orders],
    ["Live execution", broker.permissions.live_execution],
  ];

  return (
    <section id="broker" className="terminal-panel">
      <div className="panel-header">
        <span>IBKR Paper</span>
        <span>{broker.status}</span>
      </div>
      <div className="broker-status-grid">
        <div>
          <span>read_only</span>
          <strong>{String(broker.read_only)}</strong>
        </div>
        <div>
          <span>execution_enabled</span>
          <strong>{String(broker.execution_enabled)}</strong>
        </div>
        <div>
          <span>Data freshness</span>
          <strong>{broker.data_freshness}</strong>
        </div>
        <div>
          <span>Latency</span>
          <strong>{broker.latency_ms}ms</strong>
        </div>
      </div>
      <div className="permission-grid">
        {permissions.map(([label, value]) => (
          <div key={label} className={value === "allowed" ? "allowed" : "denied"}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      <ul className="diagnostics-list">
        {broker.diagnostics.map((diagnostic) => (
          <li key={diagnostic}>{diagnostic}</li>
        ))}
      </ul>
      <p className="panel-note">
        Paper / simulated — read-only preview. No live execution, no credentials,
        not live trading.
      </p>
    </section>
  );
}
