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
_shared_state: dict[str, Any] = {"snapshots": [], "last_update": 0.0}


def push_state(snapshots: list[dict[str, Any]]) -> None:
    """Thread-safe update called by the trading loop after each analysis cycle."""
    with _state_lock:
        _shared_state["snapshots"] = list(snapshots)
        _shared_state["last_update"] = time.monotonic()


# ── Dashboard HTML ────────────────────────────────────────────────────────────

_HTML = """<!DOCTYPE html>
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
.btns{display:flex;gap:6px}
button{padding:5px 12px;background:#1b2940;color:#e7ecf3;border:1px solid #283447;border-radius:3px;cursor:pointer;font-family:inherit;font-size:.82em}
button:hover{background:#22334f}
.body{display:grid;grid-template-columns:1fr 320px;flex:1;overflow:hidden}
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
</style>
</head>
<body>
<header>
  <div>
    <h1>&#9655; Alpha AI Live Dashboard</h1>
    <div id="status">Connecting&hellip;</div>
  </div>
  <div class="btns">
    <button onclick="ctrl('resume')">&#9654; Resume</button>
    <button onclick="ctrl('pause')">&#9646;&#9646; Pause</button>
    <button onclick="ctrl('stop')">&#9632; Stop</button>
  </div>
</header>
<div class="body">
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
        <th>Conf%</th><th>Score</th><th>Regime</th><th>Status</th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <div class="right">
    <div class="grid-hdr" id="ghdr">Grid Visualiser &mdash; select a symbol</div>
    <canvas id="gc"></canvas>
  </div>
</div>
<script>
'use strict';
let snaps=[], sel=null;

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
    const regime=(d.signal?.regime||'').replace('_',' ');
    if(sig==='BUY') b++; else if(sig==='SELL') s++; else h++;
    return `<tr onclick="pick('${d.symbol}')">
      <td>${d.symbol}</td>
      <td>${fp(d.last_close||0)}</td>
      <td class="${sig.toLowerCase()}">${sig}</td>
      <td>${conf}</td><td>${score}</td>
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

function pick(sym){
  sel=sym;
  drawGrid(sym);
}

function drawGrid(sym){
  const snap=snaps.find(s=>s.symbol===sym);
  if(!snap) return;
  const canvas=document.getElementById('gc');
  const ctx=canvas.getContext('2d');
  const W=canvas.clientWidth||288, H=canvas.clientHeight||480;
  canvas.width=W; canvas.height=H;
  ctx.clearRect(0,0,W,H);

  const levels=snap.grid_levels||[];
  document.getElementById('ghdr').textContent=
    'Grid \u2014 '+sym+' @ '+fp(snap.last_close||0);

  if(!levels.length){
    ctx.fillStyle='#8b9bb2'; ctx.font='12px Consolas';
    ctx.fillText('Waiting for grid data\u2026',14,H/2); return;
  }

  const prices=levels.map(l=>l.price);
  const hi=Math.max(...prices), lo=Math.min(...prices);
  const range=hi-lo||1e-9;
  const pad=28;
  function toY(p){return pad+(1-(p-lo)/range)*(H-2*pad)}

  levels.forEach(lv=>{
    const y=toY(lv.price);
    const color=lv.type==='current'?'#ffffff':
                lv.type==='vwap'?'#f1c40f':
                lv.type==='resistance'?'#e74c3c':'#2ecc71';
    const isCur=lv.type==='current';

    ctx.save();
    ctx.strokeStyle=color+(isCur?'':'99');
    ctx.lineWidth=isCur?2:1;
    if(!isCur) ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.moveTo(52,y); ctx.lineTo(W-70,y); ctx.stroke();
    ctx.restore();

    if(isCur){
      ctx.beginPath(); ctx.fillStyle='#ffffff';
      ctx.arc(52,y,5,0,Math.PI*2); ctx.fill();
    }

    ctx.fillStyle=color; ctx.font='10px Consolas';
    ctx.textAlign='right'; ctx.fillText(lv.label.split(' ')[0],48,y+4);
    ctx.textAlign='left'; ctx.fillText(fp(lv.price),W-68,y+4);
  });

  const sig=(snap.signal?.signal||'HOLD').toUpperCase();
  const conf=snap.signal?.confidence||0;
  ctx.textAlign='center';
  ctx.font='bold 13px Consolas';
  ctx.fillStyle=sig==='BUY'?'#2ecc71':sig==='SELL'?'#e74c3c':'#f1c40f';
  ctx.fillText(sig+' '+conf.toFixed(1)+'%', W/2, H-10);
}

// WebSocket with auto-reconnect
function connect(){
  const ws=new WebSocket('ws://'+location.host+'/ws');
  ws.onopen=()=>{document.getElementById('status').textContent='Connected \u2014 live updates active'};
  ws.onclose=()=>{document.getElementById('status').textContent='Disconnected \u2014 reconnecting\u2026'; setTimeout(connect,3000)};
  ws.onerror=()=>{ws.close()};
  ws.onmessage=e=>{try{render(JSON.parse(e.data))}catch(_){}};
}
connect();

function ctrl(action){
  fetch('/api/control',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action})})
    .then(r=>r.json())
    .then(d=>{ document.getElementById('status').textContent='Command: '+action+' \u2192 '+d.status });
}

window.addEventListener('resize',()=>{ if(sel) drawGrid(sel) });
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
        last_sent = 0.0
        try:
            while True:
                lu = _shared_state["last_update"]
                if lu > last_sent:
                    with _state_lock:
                        payload = json.dumps(_shared_state["snapshots"])
                    await websocket.send_text(payload)
                    last_sent = lu
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
