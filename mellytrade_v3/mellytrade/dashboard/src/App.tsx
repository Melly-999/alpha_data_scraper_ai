import { useEffect, useState } from "react";

type Signal = {
  id: number;
  created_at: string;
  symbol: string;
  action: "BUY" | "SELL" | "HOLD";
  confidence: number;
  risk_percent: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  status: string;
  reason: string;
};

const REFRESH_MS = 5000;

export default function App() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const resp = await fetch("/api/signals");
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const body = (await resp.json()) as { signals?: Signal[] };
        if (!cancelled) {
          setSignals(body.signals ?? []);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      }
    }

    load();
    const id = setInterval(load, REFRESH_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem" }}>
      <h1>MellyTrade Signals</h1>
      <p style={{ color: "#666" }}>
        Live feed from the Cloudflare worker hub. Risk rules enforced by the
        API: max 1% risk, min 70 confidence, SL/TP required, cooldown 60s.
      </p>
      {error && <p style={{ color: "crimson" }}>Error: {error}</p>}
      <table border={1} cellPadding={6} style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Time</th>
            <th>Symbol</th>
            <th>Action</th>
            <th>Conf</th>
            <th>Risk %</th>
            <th>Entry</th>
            <th>SL</th>
            <th>TP</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {signals.map((s) => (
            <tr key={s.id}>
              <td>{new Date(s.created_at).toLocaleTimeString()}</td>
              <td>{s.symbol}</td>
              <td>{s.action}</td>
              <td>{s.confidence.toFixed(1)}</td>
              <td>{s.risk_percent.toFixed(2)}</td>
              <td>{s.entry_price}</td>
              <td>{s.stop_loss}</td>
              <td>{s.take_profit}</td>
              <td>{s.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
