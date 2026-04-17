import { useEffect, useMemo, useState } from "react"

type Signal = {
  id?: string | number
  symbol?: string
  direction?: string
  confidence?: number
  price?: number
  stopLoss?: number
  takeProfit?: number
  riskPercent?: number
  timestamp?: string
  status?: string
}

const wsUrl = () => {
  const configured = import.meta.env.VITE_WS_URL as string | undefined
  if (configured) return configured

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
  return `${protocol}//${window.location.host}/ws`
}

const formatValue = (value: number | undefined, digits = 5) => {
  if (typeof value !== "number" || Number.isNaN(value)) return "-"
  return value.toFixed(digits)
}

export default function App() {
  const [signals, setSignals] = useState<Signal[]>([])
  const [status, setStatus] = useState("connecting")
  const [lastError, setLastError] = useState("")

  useEffect(() => {
    let socket: WebSocket | null = null
    let reconnectTimer: number | undefined
    let closedByApp = false

    const connect = () => {
      socket = new WebSocket(wsUrl())
      setStatus("connecting")

      socket.onopen = () => {
        setStatus("live")
        setLastError("")
      }

      socket.onmessage = event => {
        try {
          const data = JSON.parse(event.data) as Signal
          if ((data as { type?: string }).type === "pong") return
          setSignals(prev => [{ ...data, id: data.id ?? crypto.randomUUID() }, ...prev].slice(0, 20))
        } catch {
          setLastError("Received unreadable signal payload")
        }
      }

      socket.onerror = () => {
        setStatus("error")
        setLastError("WebSocket connection failed")
      }

      socket.onclose = () => {
        if (closedByApp) return
        setStatus("reconnecting")
        reconnectTimer = window.setTimeout(connect, 3000)
      }
    }

    connect()

    return () => {
      closedByApp = true
      if (reconnectTimer) window.clearTimeout(reconnectTimer)
      socket?.close()
    }
  }, [])

  const summary = useMemo(() => {
    const accepted = signals.filter(signal => signal.status !== "blocked").length
    const blocked = signals.length - accepted
    const maxRisk = signals.reduce((max, signal) => Math.max(max, signal.riskPercent ?? 0), 0)
    const averageConfidence = signals.length
      ? signals.reduce((sum, signal) => sum + (signal.confidence ?? 0), 0) / signals.length
      : 0
    return { total: signals.length, accepted, blocked, maxRisk, averageConfidence }
  }, [signals])

  return (
    <main style={{ minHeight: "100vh", background: "#f7f7f2", color: "#161616", padding: 24, fontFamily: "Inter, system-ui, sans-serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", marginBottom: 22 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 26 }}>MellyTrade</h1>
          <p style={{ margin: "6px 0 0", color: "#5f625d" }}>Live signal feed</p>
        </div>
        <span style={{ border: "1px solid #b8b8ad", borderRadius: 8, padding: "7px 12px", background: status === "live" ? "#dff2df" : "#fff4cf" }}>
          {status.toUpperCase()}
        </span>
      </header>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 22 }}>
        <Metric label="Signals" value={summary.total.toString()} />
        <Metric label="Accepted" value={summary.accepted.toString()} />
        <Metric label="Blocked" value={summary.blocked.toString()} />
        <Metric label="Max risk" value={`${summary.maxRisk.toFixed(2)}%`} />
        <Metric label="Avg confidence" value={`${summary.averageConfidence.toFixed(1)}%`} />
      </section>

      {lastError ? <p style={{ color: "#9f1d1d", marginBottom: 14 }}>{lastError}</p> : null}

      <section style={{ display: "grid", gap: 10 }}>
        {signals.length === 0 ? (
          <div style={{ border: "1px solid #d6d6ca", borderRadius: 8, padding: 18, background: "#ffffff" }}>
            Waiting for published signals.
          </div>
        ) : (
          signals.map(signal => <SignalRow key={signal.id} signal={signal} />)
        )}
      </section>
    </main>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ border: "1px solid #d6d6ca", borderRadius: 8, padding: 14, background: "#ffffff" }}>
      <div style={{ color: "#5f625d", fontSize: 12, textTransform: "uppercase" }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700 }}>{value}</div>
    </div>
  )
}

function SignalRow({ signal }: { signal: Signal }) {
  const direction = signal.direction ?? "UNKNOWN"
  const directionColor = direction === "BUY" ? "#116b38" : direction === "SELL" ? "#9f1d1d" : "#5f625d"

  return (
    <article style={{ border: "1px solid #d6d6ca", borderLeft: `4px solid ${directionColor}`, borderRadius: 8, padding: 14, background: "#ffffff" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <strong>{signal.symbol ?? "UNKNOWN"}</strong>
          <span style={{ color: directionColor, fontWeight: 700 }}>{direction}</span>
          {signal.status ? <span>{signal.status}</span> : null}
        </div>
        <strong>{formatValue(signal.confidence, 1)}%</strong>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(110px, 1fr))", gap: 8, marginTop: 12, fontSize: 14 }}>
        <Field label="Entry" value={formatValue(signal.price)} />
        <Field label="SL" value={formatValue(signal.stopLoss)} />
        <Field label="TP" value={formatValue(signal.takeProfit)} />
        <Field label="Risk" value={`${formatValue(signal.riskPercent, 2)}%`} />
      </div>
    </article>
  )
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div style={{ color: "#5f625d", fontSize: 12 }}>{label}</div>
      <div>{value}</div>
    </div>
  )
}
