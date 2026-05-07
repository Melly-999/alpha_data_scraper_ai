import type { SignalItem } from "../../lib/terminalApi";

type AISignalFeedPreviewProps = {
  signals: SignalItem[];
};

export function AISignalFeedPreview({ signals }: AISignalFeedPreviewProps) {
  return (
    <section id="signals" className="terminal-panel">
      <div className="panel-header">
        <span>AI signals preview</span>
        <span>no execution controls</span>
      </div>
      <div className="terminal-table">
        <div className="table-row table-head">
          <span>Symbol</span>
          <span>Signal</span>
          <span>TF</span>
          <span>Conf</span>
        </div>
        {signals.map((signal) => (
          <div key={signal.id} className="table-row">
            <span>{signal.symbol}</span>
            <span>{signal.direction}</span>
            <span>{signal.timeframe}</span>
            <span>{signal.confidence}%</span>
            <p>{signal.reason}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
