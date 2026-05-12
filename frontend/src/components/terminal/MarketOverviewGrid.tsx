import type { MarketItem } from "../../lib/terminalApi";

type MarketOverviewGridProps = {
  markets: MarketItem[];
};

export function MarketOverviewGrid({ markets }: MarketOverviewGridProps) {
  return (
    <section id="markets" className="terminal-panel">
      <div className="panel-header">
        <span>Market overview</span>
        <span>GET /api/market/overview</span>
      </div>
      <div className="market-grid">
        {markets.map((market) => (
          <article key={market.symbol} className="market-card">
            <div className="market-card-top">
              <strong>{market.symbol}</strong>
              <span>{market.signal}</span>
            </div>
            <div className="market-price">
              {market.price.toFixed(market.price > 10 ? 2 : 4)}
            </div>
            <div className={market.change_pct >= 0 ? "value-positive" : "value-negative"}>
              {market.change_pct >= 0 ? "+" : ""}
              {market.change_pct.toFixed(2)}%
            </div>
            <div className="confidence-track">
              <span style={{ width: `${market.confidence}%` }} />
            </div>
            <small>{market.confidence}% confidence</small>
          </article>
        ))}
      </div>
    </section>
  );
}
