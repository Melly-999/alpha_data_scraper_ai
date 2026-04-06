"""WebSocket-based real-time trading dashboard.

Usage
-----
from dashboard import start_dashboard, push_state

controller = TradingController()
start_dashboard(controller=controller, port=8050)

# after each trading cycle:
push_state(snapshots)
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from typing import Any

from core.logger import get_logger

logger = get_logger(__name__)

# ── Shared state (written by trading loop, read by WebSocket server) ──────────

_state_lock = threading.Lock()
_shared_state: dict[str, Any] = {
    "snapshots": [],
    "last_update": 0.0,
    "alerts": [],
    "alerts_update": 0.0,
}


def push_state(snapshots: list[dict[str, Any]]) -> None:
    """Thread-safe update called by the trading loop after each analysis cycle."""
    with _state_lock:
        _shared_state["snapshots"] = list(snapshots)
        _shared_state["last_update"] = time.monotonic()


def push_alerts(alerts: list[dict[str, Any]]) -> None:
    """Thread-safe alert push called by AlertManager on signal changes."""
    with _state_lock:
        _shared_state["alerts"].extend(alerts)
        _shared_state["alerts"] = _shared_state["alerts"][-100:]
        _shared_state["alerts_update"] = time.monotonic()


# ── Quick backtest (no MT5 required) ─────────────────────────────────────────

def _run_quick_backtest(
    symbol: str,
    bars: int = 500,
    initial_balance: float = 10_000.0,
) -> dict[str, Any]:
    """Run a rolling-window backtest using the strategy signal pipeline.

    Uses ``batch_fetch()`` (synthetic fallback when MT5 unavailable) so this
    works in CI and without a live broker connection.  LSTM is skipped for
    speed; signal generation uses indicator scoring only (``lstm_delta=0``).
    """
    try:
        from mt5_fetcher import batch_fetch
        from strategy.indicators import add_indicators
        from strategy.signal_generator import generate_signal
    except ImportError as exc:
        return {"error": f"Missing dependency: {exc}"}

    raw_data = batch_fetch(symbols=[symbol], timeframe="M5", bars=bars)
    df = raw_data.get(symbol)
    if df is None or len(df) < 60:
        return {"error": "Insufficient data", "symbol": symbol}

    data = add_indicators(df)
    lookback = 50
    balance = initial_balance
    trades: list[dict[str, Any]] = []
    open_pos: dict[str, Any] | None = None

    for i in range(lookback, len(data)):
        row = data.iloc[i]
        result = generate_signal(row, lstm_delta=0.0)
        sig = result.signal
        conf = result.confidence
        close = float(row["close"])

        if open_pos is None:
            if sig in ("BUY", "SELL") and conf >= 60:
                open_pos = {"signal": sig, "entry": close, "idx": i}
        else:
            bars_held = i - open_pos["idx"]
            reversal = (
                (open_pos["signal"] == "BUY" and sig == "SELL") or
                (open_pos["signal"] == "SELL" and sig == "BUY")
            )
            if bars_held >= 20 or reversal:
                if open_pos["signal"] == "BUY":
                    pnl_pct = (close - open_pos["entry"]) / open_pos["entry"] * 100
                else:
                    pnl_pct = (open_pos["entry"] - close) / open_pos["entry"] * 100
                balance *= 1 + pnl_pct / 100
                trades.append({"pnl_pct": round(pnl_pct, 4), "signal": open_pos["signal"]})
                open_pos = None

    if not trades:
        return {
            "symbol": symbol, "bars": bars,
            "total_trades": 0, "message": "No trades generated",
        }

    wins = [t for t in trades if t["pnl_pct"] > 0]
    losses = [t for t in trades if t["pnl_pct"] < 0]
    total_return = (balance - initial_balance) / initial_balance * 100
    gross_profit = sum(t["pnl_pct"] for t in wins) if wins else 0.0
    gross_loss = abs(sum(t["pnl_pct"] for t in losses)) if losses else 1e-9

    return {
        "symbol": symbol,
        "bars": bars,
        "total_trades": len(trades),
        "winning_trades": len(wins),
        "losing_trades": len(losses),
        "win_rate": round(len(wins) / len(trades) * 100, 1),
        "total_return": round(total_return, 2),
        "profit_factor": round(gross_profit / gross_loss, 2),
        "avg_win": round(sum(t["pnl_pct"] for t in wins) / max(len(wins), 1), 3),
        "avg_loss": round(sum(t["pnl_pct"] for t in losses) / max(len(losses), 1), 3),
        "final_balance": round(balance, 2),
        "initial_balance": initial_balance,
    }


# ── Dashboard HTML ────────────────────────────────────────────────────────────

_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Alpha AI Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0b1018;color:#e7ecf3;font-family:Consolas,monospace;height:100vh;display:flex;flex-direction:column}
header{display:flex;align-items:center;justify-content:space-between;padding:10px 18px;background:#131c2a;border-bottom:1px solid #283447;flex-shrink:0}
header h1{font-size:1.1em;letter-spacing:.04em}
#status{font-size:.78em;color:#8b9bb2;margin-top:2px}
.hdr-right{display:flex;gap:10px;align-items:center}
.tabs{display:flex;gap:4px}
.tab{padding:5px 12px;background:#0f1724;color:#8b9bb2;border:1px solid #283447;border-radius:3px;cursor:pointer;font-family:inherit;font-size:.82em}
.tab.active{background:#1b2940;color:#e7ecf3;border-color:#4a7fa5}
.btns{display:flex;gap:5px}
button{padding:5px 12px;background:#1b2940;color:#e7ecf3;border:1px solid #283447;border-radius:3px;cursor:pointer;font-family:inherit;font-size:.82em}
button:hover{background:#22334f}
.panel{display:none;flex:1;overflow:hidden}
.panel.active{display:grid}
#live-panel{grid-template-columns:1fr 320px}
.left{overflow-y:auto;padding:14px}
.right{border-left:1px solid #283447;padding:14px;display:flex;flex-direction:column;overflow:hidden}
.stats{display:flex;gap:8px;margin-bottom:12px}
.stat{flex:1;background:#131c2a;border-radius:4px;padding:9px 8px;text-align:center}
.sv{font-size:1.35em;font-weight:bold}
.sl{font-size:.72em;color:#8b9bb2;margin-top:2px}
table{width:100%;border-collapse:collapse;font-size:.84em}
th{background:#1a2638;color:#d6deea;padding:7px 9px;text-align:left;position:sticky;top:0;z-index:1}
td{padding:7px 9px;border-bottom:1px solid #1a2638;cursor:pointer;white-space:nowrap}
tr:hover td{background:#111820}
.buy{color:#2ecc71}.sell{color:#e74c3c}.hold{color:#f1c40f}
.regime{font-size:.73em;color:#8b9bb2}
.grid-hdr{font-size:.85em;color:#8b9bb2;margin-bottom:8px;flex-shrink:0}
canvas{display:block;background:#0f1724;border-radius:4px;width:100%;flex:1}
/* backtest panel */
#bt-panel{flex-direction:column;padding:20px;overflow-y:auto}
.bt-form{display:flex;gap:10px;align-items:flex-end;margin-bottom:20px;flex-wrap:wrap}
.bt-field{display:flex;flex-direction:column;gap:4px}
.bt-field label{font-size:.78em;color:#8b9bb2}
.bt-field input{background:#131c2a;border:1px solid #283447;color:#e7ecf3;padding:5px 10px;border-radius:3px;font-family:inherit;font-size:.88em;width:130px}
.bt-results{background:#131c2a;border-radius:6px;padding:16px;display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.bt-metric{padding:10px;background:#0f1724;border-radius:4px}
.bt-metric .val{font-size:1.3em;font-weight:bold;margin-bottom:4px}
.bt-metric .lbl{font-size:.73em;color:#8b9bb2}
.pos{color:#2ecc71}.neg{color:#e74c3c}
/* alert toasts */
#toasts{position:fixed;bottom:16px;right:16px;display:flex;flex-direction:column-reverse;gap:8px;z-index:100}
.toast{background:#1b2940;border:1px solid #283447;border-radius:5px;padding:10px 14px;font-size:.82em;max-width:280px;animation:fadein .3s ease}
.toast .sym{font-weight:bold;margin-right:6px}
@keyframes fadein{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>
<header>
  <div>
    <h1>&#9655; Alpha AI Dashboard</h1>
    <div id="status">Connecting&hellip;</div>
  </div>
  <div class="hdr-right">
    <div class="tabs">
      <button class="tab active" onclick="showTab('live')">Live</button>
      <button class="tab" onclick="showTab('bt')">Backtest</button>
    </div>
    <div class="btns">
      <button onclick="ctrl('resume')">&#9654; Resume</button>
      <button onclick="ctrl('pause')">&#9646;&#9646; Pause</button>
      <button onclick="ctrl('stop')">&#9632; Stop</button>
    </div>
  </div>
</header>

<!-- Live tab -->
<div id="live-panel" class="panel active">
  <div class="left">
    <div class="stats">
      <div class="stat"><div class="sv" id="cnt">0</div><div class="sl">Instruments</div></div>
      <div class="stat"><div class="sv buy" id="buys">0</div><div class="sl">BUY</div></div>
      <div class="stat"><div class="sv sell" id="sells">0</div><div class="sl">SELL</div></div>
      <div class="stat"><div class="sv hold" id="holds">0</div><div class="sl">HOLD</div></div>
    </div>
    <table>
      <thead><tr>
        <th>Symbol</th><th>Price</th><th>Signal</th>
        <th>Conf%</th><th>Score</th><th>MTF</th><th>Regime</th><th>Status</th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <div class="right">
    <div class="grid-hdr" id="ghdr">Grid Visualiser &mdash; select a symbol</div>
    <canvas id="gc"></canvas>
  </div>
</div>

<!-- Backtest tab -->
<div id="bt-panel" class="panel">
  <div class="bt-form">
    <div class="bt-field"><label>Symbol</label><input id="bt-sym" value="EURUSD"></div>
    <div class="bt-field"><label>Bars</label><input id="bt-bars" type="number" value="500" min="60" max="2000"></div>
    <div class="bt-field"><label>Balance</label><input id="bt-bal" type="number" value="10000"></div>
    <button onclick="runBacktest()" style="align-self:flex-end">&#9654; Run Backtest</button>
    <span id="bt-status" style="align-self:flex-end;font-size:.8em;color:#8b9bb2"></span>
  </div>
  <div class="bt-results" id="bt-results">
    <div style="color:#8b9bb2;font-size:.88em">Configure above and click Run Backtest.</div>
  </div>
</div>

<!-- Toast container -->
<div id="toasts"></div>

<script>
'use strict';
let snaps=[], sel=null;

function showTab(t){
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));
  document.getElementById(t==='live'?'live-panel':'bt-panel').classList.add('active');
  document.querySelectorAll('.tab')[t==='live'?0:1].classList.add('active');
}

function fp(v){return v>100?v.toFixed(2):v.toFixed(5)}
function fat(a){
  if(!a||typeof a!=='object') return String(a||'');
  const s=a.status||'?';
  if(s==='cooldown') return 'cooldown ('+a.seconds_left+'s)';
  if(s==='dry_run'||s==='placed') return s+' '+(a.request?.side||'');
  return s;
}

function render(data){
  snaps=data;
  let b=0,s=0,h=0;
  const rows=data.map(d=>{
    const sig=(d.signal?.signal||'HOLD').toUpperCase();
    const conf=(d.signal?.confidence||0).toFixed(1);
    const score=d.signal?.score??0;
    const mtf=d.mtf?.weighted_signal||'';
    const regime=(d.signal?.regime||'').replace('_',' ');
    if(sig==='BUY') b++; else if(sig==='SELL') s++; else h++;
    const mtfCls=mtf==='BUY'?'buy':mtf==='SELL'?'sell':'hold';
    return `<tr onclick="pick('${d.symbol}')">
      <td>${d.symbol}</td>
      <td>${fp(d.last_close||0)}</td>
      <td class="${sig.toLowerCase()}">${sig}</td>
      <td>${conf}</td><td>${score}</td>
      <td class="${mtfCls}" style="font-size:.78em">${mtf||'&mdash;'}</td>
      <td class="regime">${regime}</td>
      <td>${fat(d.autotrade)}</td>
    </tr>`;
  }).join('');
  document.getElementById('tbody').innerHTML=rows;
  document.getElementById('cnt').textContent=data.length;
  document.getElementById('buys').textContent=b;
  document.getElementById('sells').textContent=s;
  document.getElementById('holds').textContent=h;
  if(!sel&&data.length) pick(data[0].symbol);
  else if(sel) drawGrid(sel);
}

function showAlerts(alerts){
  const container=document.getElementById('toasts');
  alerts.forEach(a=>{
    const div=document.createElement('div');
    div.className='toast';
    const sc=a.from_signal==='BUY'?'buy':a.from_signal==='SELL'?'sell':'hold';
    const tc=a.to_signal==='BUY'?'buy':a.to_signal==='SELL'?'sell':'hold';
    div.innerHTML=`<span class="sym">${a.symbol}</span>`+
      `<span class="${sc}">${a.from_signal}</span> &rarr; `+
      `<span class="${tc}">${a.to_signal}</span>`+
      ` <span style="color:#8b9bb2">(${(a.confidence||0).toFixed(1)}%)</span>`;
    container.appendChild(div);
    setTimeout(()=>div.remove(), 6000);
  });
}

function pick(sym){ sel=sym; drawGrid(sym); }

function drawGrid(sym){
  const snap=snaps.find(s=>s.symbol===sym);
  if(!snap) return;
  const canvas=document.getElementById('gc');
  const ctx=canvas.getContext('2d');
  const W=canvas.clientWidth||288, H=canvas.clientHeight||480;
  canvas.width=W; canvas.height=H;
  ctx.clearRect(0,0,W,H);
  const levels=snap.grid_levels||[];
  document.getElementById('ghdr').textContent='Grid \u2014 '+sym+' @ '+fp(snap.last_close||0);
  if(!levels.length){ctx.fillStyle='#8b9bb2';ctx.font='12px Consolas';ctx.fillText('Waiting\u2026',14,H/2);return;}
  const prices=levels.map(l=>l.price);
  const hi=Math.max(...prices),lo=Math.min(...prices),range=hi-lo||1e-9,pad=28;
  const toY=p=>pad+(1-(p-lo)/range)*(H-2*pad);
  levels.forEach(lv=>{
    const y=toY(lv.price);
    const color=lv.type==='current'?'#ffffff':lv.type==='vwap'?'#f1c40f':lv.type==='resistance'?'#e74c3c':'#2ecc71';
    const isCur=lv.type==='current';
    ctx.save();
    ctx.strokeStyle=color+(isCur?'':'99');ctx.lineWidth=isCur?2:1;
    if(!isCur)ctx.setLineDash([4,4]);
    ctx.beginPath();ctx.moveTo(52,y);ctx.lineTo(W-70,y);ctx.stroke();
    ctx.restore();
    if(isCur){ctx.beginPath();ctx.fillStyle='#ffffff';ctx.arc(52,y,5,0,Math.PI*2);ctx.fill();}
    ctx.fillStyle=color;ctx.font='10px Consolas';
    ctx.textAlign='right';ctx.fillText(lv.label.split(' ')[0],48,y+4);
    ctx.textAlign='left';ctx.fillText(fp(lv.price),W-68,y+4);
  });
  const sig=(snap.signal?.signal||'HOLD').toUpperCase(),conf=snap.signal?.confidence||0;
  ctx.textAlign='center';ctx.font='bold 13px Consolas';
  ctx.fillStyle=sig==='BUY'?'#2ecc71':sig==='SELL'?'#e74c3c':'#f1c40f';
  ctx.fillText(sig+' '+conf.toFixed(1)+'%',W/2,H-10);
}

// WebSocket — receives {type, data} envelopes or raw snapshot arrays
function connect(){
  const ws=new WebSocket('ws://'+location.host+'/ws');
  ws.onopen=()=>{document.getElementById('status').textContent='Connected \u2014 live updates active'};
  ws.onclose=()=>{document.getElementById('status').textContent='Disconnected \u2014 reconnecting\u2026';setTimeout(connect,3000)};
  ws.onerror=()=>ws.close();
  ws.onmessage=e=>{
    try{
      const msg=JSON.parse(e.data);
      if(Array.isArray(msg)){render(msg);}
      else if(msg.type==='snapshots'){render(msg.data);}
      else if(msg.type==='alerts'){showAlerts(msg.data);}
    }catch(_){}
  };
}
connect();

function ctrl(action){
  fetch('/api/control',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action})})
    .then(r=>r.json())
    .then(d=>{document.getElementById('status').textContent='Command: '+action+' \u2192 '+d.status});
}

function runBacktest(){
  const sym=document.getElementById('bt-sym').value.trim()||'EURUSD';
  const bars=parseInt(document.getElementById('bt-bars').value)||500;
  const bal=parseFloat(document.getElementById('bt-bal').value)||10000;
  document.getElementById('bt-status').textContent='Running\u2026';
  document.getElementById('bt-results').innerHTML='<div style="color:#8b9bb2">Running backtest\u2026</div>';
  fetch('/api/backtest',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({symbol:sym,bars,initial_balance:bal})})
  .then(r=>r.json())
  .then(d=>{
    document.getElementById('bt-status').textContent='';
    if(d.error){document.getElementById('bt-results').innerHTML='<div style="color:#e74c3c">'+d.error+'</div>';return;}
    const pct=c=>c>=0?`<span class="pos">+${c}%</span>`:`<span class="neg">${c}%</span>`;
    const metrics=[
      {l:'Symbol',v:d.symbol},
      {l:'Bars Analysed',v:d.bars},
      {l:'Total Trades',v:d.total_trades},
      {l:'Win Rate',v:d.win_rate+'%'},
      {l:'Total Return',v:pct(d.total_return)},
      {l:'Profit Factor',v:d.profit_factor+'x'},
      {l:'Avg Win',v:pct(d.avg_win)},
      {l:'Avg Loss',v:pct(d.avg_loss)},
      {l:'Final Balance',v:'$'+d.final_balance},
    ];
    document.getElementById('bt-results').innerHTML=metrics.map(m=>
      `<div class="bt-metric"><div class="val">${m.v}</div><div class="lbl">${m.l}</div></div>`
    ).join('');
  })
  .catch(e=>{document.getElementById('bt-status').textContent='Error: '+e;});
}

window.addEventListener('resize',()=>{if(sel)drawGrid(sel)});
</script>
</body>
</html>"""


# ── FastAPI app factory ───────────────────────────────────────────────────────

def _build_app(controller: Any = None) -> Any:
    try:
        from fastapi import FastAPI, WebSocket, WebSocketDisconnect
        from fastapi.responses import HTMLResponse
    except ImportError as exc:
        raise RuntimeError(
            "fastapi is required for the dashboard: pip install fastapi uvicorn"
        ) from exc

    app = FastAPI(title="Alpha AI Dashboard")

    @app.get("/", response_class=HTMLResponse)
    async def root() -> str:
        return _HTML

    @app.websocket("/ws")
    async def ws_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        last_snap = 0.0
        last_alert = 0.0
        try:
            while True:
                lu = _shared_state["last_update"]
                if lu > last_snap:
                    with _state_lock:
                        payload = json.dumps(
                            {"type": "snapshots", "data": _shared_state["snapshots"]}
                        )
                    await websocket.send_text(payload)
                    last_snap = lu

                au = _shared_state["alerts_update"]
                if au > last_alert:
                    with _state_lock:
                        alerts = list(_shared_state["alerts"])
                    new_alerts = [a for a in alerts if a.get("ts", 0) > last_alert]
                    if new_alerts:
                        await websocket.send_text(
                            json.dumps({"type": "alerts", "data": new_alerts})
                        )
                    last_alert = au

                await asyncio.sleep(0.4)
        except WebSocketDisconnect:
            pass
        except Exception:
            pass

    @app.post("/api/control")
    async def api_control(body: dict[str, Any]) -> dict[str, str]:
        action = str(body.get("action", ""))
        if controller is not None:
            if action == "stop":
                controller.stop()
            elif action == "pause":
                controller.pause()
            elif action in {"resume", "start"}:
                controller.resume()
        return {"status": "ok", "action": action}

    @app.get("/api/status")
    async def api_status() -> dict[str, Any]:
        if controller is not None:
            return controller.status()
        return {"running": False, "stopped": True, "paused": False}

    @app.post("/api/backtest")
    async def api_backtest(body: dict[str, Any]) -> dict[str, Any]:
        """Run a quick rolling-window backtest (no MT5 required)."""
        symbol = str(body.get("symbol", "EURUSD")).upper()
        bars = min(int(body.get("bars", 500)), 2000)
        initial_balance = float(body.get("initial_balance", 10_000.0))
        return _run_quick_backtest(symbol, bars=bars, initial_balance=initial_balance)

    @app.get("/api/alerts")
    async def api_alerts() -> list[dict[str, Any]]:
        with _state_lock:
            return list(_shared_state["alerts"][-50:])

    return app


# ── Public entry point ────────────────────────────────────────────────────────

def start_dashboard(
    controller: Any = None,
    host: str = "0.0.0.0",
    port: int = 8050,
) -> threading.Thread:
    """Start the dashboard WebSocket server in a daemon thread.

    Args:
        controller: Optional ``TradingController`` for start/stop/pause via API.
        host:       Bind address (default: all interfaces).
        port:       HTTP port (default: 8050).

    Returns:
        The daemon thread running the uvicorn server.
    """
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError(
            "uvicorn is required for the dashboard: pip install uvicorn"
        ) from exc

    app = _build_app(controller)
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True, name="alpha-dashboard")
    thread.start()
    logger.info("Dashboard started at http://%s:%d", host, port)
    print(f"Dashboard → http://localhost:{port}")
    return thread
