import type { MarketItem } from "../../lib/terminalApi";
import { SafetyBadges } from "./SafetyBadges";

type TopTickerBarProps = {
  markets: MarketItem[];
};

export function TopTickerBar({ markets }: TopTickerBarProps) {
  return (
    <header className="top-ticker-bar">
      <div className="ticker-brand">
        <span className="brand-mark">MT</span>
        <span>MellyTrade V1</span>
      </div>
      <div className="ticker-strip">
        {markets.map((market) => (
          <div key={market.symbol} className="ticker-item">
            <span className="ticker-symbol">{market.symbol}</span>
            <span>{market.price.toFixed(market.price > 10 ? 2 : 4)}</span>
            <span className={market.change_pct >= 0 ? "value-positive" : "value-negative"}>
              {market.change_pct >= 0 ? "+" : ""}
              {market.change_pct.toFixed(2)}%
            </span>
          </div>
        ))}
      </div>
      <SafetyBadges />
    </header>
  );
}
