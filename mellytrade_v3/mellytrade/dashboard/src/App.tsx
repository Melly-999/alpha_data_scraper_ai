import { useEffect, useMemo, useRef, useState } from 'react'

type Signal = {
  id: string
  symbol: string
  direction: string
  confidence: number
  price: number
  stopLoss: number
  takeProfit: number
  riskPercent: number
  timestamp?: string
}

function makeDemoSignal(): Signal {
  const buy = Math.random() > 0.5
  const price = Number((1.05 + Math.random() * 0.1).toFixed(5))
  return {
    id: crypto.randomUUID(),
    symbol: ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY'][Math.floor(Math.random() * 4)],
    direction: buy ? 'BUY' : 'SELL',
    confidence: Number((70 + Math.random() * 25).toFixed(1)),
    price,
    stopLoss: buy ? Number((price - 0.003).toFixed(5)) : Number((price + 0.003).toFixed(5)),
    takeProfit: buy ? Number((price + 0.006).toFixed(5)) : Number((price - 0.006).toFixed(5)),
    riskPercent: Number((0.3 + Math.random() * 0.7).toFixed(2)),
    timestamp: new Date().toISOString(),
  }
}

export default function App() {
  const [signals, setSignals] = useState<Signal[]>([])
  const [status, setStatus] = useState('demo')
  const timer = useRef<number | null>(null)

  useEffect(() => {
    setSignals([makeDemoSignal(), makeDemoSignal()])
    timer.current = window.setInterval(() => {
      setSignals(prev => [makeDemoSignal(), ...prev].slice(0, 12))
    }, 3500)
    return () => {
      if (timer.current) window.clearInterval(timer.current)
    }
  }, [])

  const summary = useMemo(() => {
    const buys = signals.filter(s => s.direction === 'BUY').length
    const sells = signals.filter(s => s.direction === 'SELL').length
    return { total: signals.length, buys, sells }
  }, [signals])

  return (
    <div style={{ minHeight: '100vh', background: '#060d1a', color: '#f1f5f9', padding: 24, fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 24 }}>MellyTrade Dashboard</h1>
          <div style={{ color: '#94a3b8', marginTop: 6 }}>Live signal feed starter</div>
        </div>
        <div style={{ padding: '6px 12px', border: '1px solid #1e293b', borderRadius: 8, color: '#22c55e' }}>{status.toUpperCase()}</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 12, marginBottom: 20 }}>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 12, padding: 16 }}>
          <div style={{ color: '#94a3b8', fontSize: 12 }}>TOTAL SIGNALS</div>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{summary.total}</div>
        </div>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 12, padding: 16 }}>
          <div style={{ color: '#94a3b8', fontSize: 12 }}>BUY</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#22c55e' }}>{summary.buys}</div>
        </div>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 12, padding: 16 }}>
          <div style={{ color: '#94a3b8', fontSize: 12 }}>SELL</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#ef4444' }}>{summary.sells}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gap: 10 }}>
        {signals.map(signal => (
          <div key={signal.id} style={{ background: '#0f172a', border: '1px solid #1e293b', borderLeft: `4px solid ${signal.direction === 'BUY' ? '#22c55e' : '#ef4444'}`, borderRadius: 12, padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                <strong>{signal.symbol}</strong>
                <span style={{ color: signal.direction === 'BUY' ? '#22c55e' : '#ef4444' }}>{signal.direction}</span>
              </div>
              <div>{signal.confidence}%</div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 8, marginTop: 10, fontSize: 14 }}>
              <div><div style={{ color: '#94a3b8', fontSize: 12 }}>Entry</div><div>{signal.price}</div></div>
              <div><div style={{ color: '#94a3b8', fontSize: 12 }}>SL</div><div>{signal.stopLoss}</div></div>
              <div><div style={{ color: '#94a3b8', fontSize: 12 }}>TP</div><div>{signal.takeProfit}</div></div>
              <div><div style={{ color: '#94a3b8', fontSize: 12 }}>Risk</div><div>{signal.riskPercent}%</div></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
