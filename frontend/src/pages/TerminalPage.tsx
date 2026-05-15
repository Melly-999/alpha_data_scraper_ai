import { useEffect, useState } from "react";

import {
  fallbackIBKRStatus,
  getBacktestSummary,
  getIBKRBrokerStatus,
  getMarketOverview,
  getMT5Status,
  getNewsSentiment,
  getPositions,
  getRiskPolicy,
  getRiskStatus,
  getSignalFeed,
  getTerminalEvents,
  getTerminalSummary,
  getWatchlist,
} from "../lib/terminalApi";
import {
  DEFAULT_SCANNER_PREVIEW_SYMBOLS,
  createScannerPreviewFallback,
  getScannerPreview,
} from "../lib/scannerPreviewApi";
import { TerminalShell, type TerminalShellData } from "../components/terminal";
import { TerminalBootScreen } from "../components/terminal/TerminalBootScreen";
import "../components/terminal/terminal.css";
import { useLocation } from "react-router-dom";

const initialData: TerminalShellData = {
  summary: {
    terminal: "MellyTrade V1 Terminal",
    mode: "read-only",
    backend: "fallback",
    safety: {
      read_only: true,
      dry_run: true,
      auto_trade: false,
      live_orders_blocked: true,
    },
    broker: fallbackIBKRStatus,
    updated_at: new Date().toISOString(),
  },
  markets: [],
  watchlist: [],
  signals: [],
  scannerPreview: createScannerPreviewFallback(),
  riskStatus: {
    max_risk_per_trade_pct: 1,
    dry_run: true,
    auto_trade: false,
    read_only: true,
    stop_loss_required: true,
    take_profit_required: true,
    live_orders_blocked: true,
  },
  riskPolicy: {
    min_confidence: 70,
    daily_loss_cap_pct: 3,
    open_position_cap: 3,
    execution_enabled: false,
  },
  backtest: {
    win_rate: 0,
    max_drawdown_pct: 0,
    profit_factor: 0,
    sample_size: 0,
  },
  news: [],
  positions: [],
  mt5: {
    connected: false,
    mode: "synthetic",
    data_freshness: "fallback",
  },
  events: [],
  broker: fallbackIBKRStatus,
};

export function TerminalPage() {
  const location = useLocation();
  const [data, setData] = useState<TerminalShellData>(initialData);
  const [loading, setLoading] = useState(true);
  const [bootVisible, setBootVisible] = useState(true);

  useEffect(() => {
    let active = true;
    const bootTimer = window.setTimeout(() => {
      if (active) {
        setBootVisible(false);
      }
    }, 1350);

    async function loadTerminal() {
      const [
        summary,
        markets,
        watchlist,
        signals,
        riskStatus,
        riskPolicy,
        backtest,
        news,
        positions,
        mt5,
        events,
        broker,
        scannerPreview,
      ] = await Promise.all([
        getTerminalSummary(),
        getMarketOverview(),
        getWatchlist(),
        getSignalFeed(),
        getRiskStatus(),
        getRiskPolicy(),
        getBacktestSummary(),
        getNewsSentiment(),
        getPositions(),
        getMT5Status(),
        getTerminalEvents(),
        getIBKRBrokerStatus(),
        getScannerPreview(DEFAULT_SCANNER_PREVIEW_SYMBOLS),
      ]);

      if (!active) {
        return;
      }

      setData({
        summary,
        markets: markets.length > 0 ? markets : watchlist,
        watchlist,
        signals,
        riskStatus,
        riskPolicy,
        backtest,
        news,
        positions,
        mt5,
        events,
        broker,
        scannerPreview,
      });
      window.setTimeout(() => {
        if (active) {
          setLoading(false);
        }
      }, 500);
    }

    void loadTerminal();

    return () => {
      active = false;
      window.clearTimeout(bootTimer);
    };
  }, []);

  if (bootVisible) {
    return <TerminalBootScreen />;
  }

  return (
    <TerminalShell
      data={data}
      loading={loading}
      pathname={location.pathname}
    />
  );
}
