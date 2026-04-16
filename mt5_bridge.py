"""
mt5_bridge.py  (v3 — Optimized)
─────────────────────────────────────────────────────────────────────
Flow per symbol per cycle:
  1. Pull OHLCV bars from MT5
  2. Compute technical indicators (EMA, RSI, ATR, Stoch, MACD, BB)
  3. Run LSTM pipeline (alpha_data_scraper_ai)
  4. Combine signals via EnsembleCombiner
  5. POST final signal → FastAPI → CF Hub → Dashboard

Changes from v2:
  - FIX #1:  account_info() None guard
  - FIX #8:  single-worker ThreadPoolExecutor for TF/Keras safety
  - FIX #10: fail-fast on missing secrets
  - FIX #13: single timestamp per poll cycle
  - Perf:    pre-allocate indicator defaults; lazy httpx client
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import httpx
import pandas as pd

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None  # type: ignore[assignment]

try:
    import pandas_ta as ta
except ImportError:
    ta = None  # type: ignore[assignment]

from ensemble_combiner import CombinedSignal, EnsembleCombiner, TechnicalSignal
from lstm_signal_adapter import LSTMSignalAdapter

# ─── Config (fail-fast at bridge startup, not module import) ─────────


def _require_env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        raise SystemExit(f"Missing required env var: {key}")
    return val


SYMBOLS: list[str] = os.getenv("SYMBOLS", "EURUSD,GBPUSD,XAUUSD,USDJPY").split(",")
TIMEFRAME = mt5.TIMEFRAME_M5 if mt5 is not None else None
BARS = 150
POLL_INTERVAL = 10
RISK_PERCENT = 0.8
ATR_SL_MULT = 1.5
ATR_TP_MULT = 3.0
LSTM_ENSEMBLE = 2

# ─── EMA-spread confidence thresholds (ATR-normalised) ───────────────
SPREAD_ATR_MINOR = 0.5  # +5 confidence
SPREAD_ATR_MAJOR = 1.0  # +5 more confidence

_log_handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
_log_file = os.getenv("MT5_BRIDGE_LOG_FILE")
if _log_file:
    _log_handlers.append(logging.FileHandler(_log_file))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=_log_handlers,
)
log = logging.getLogger("MT5Bridge")


class MT5Bridge:

    def __init__(self) -> None:
        self.fastapi_url = os.getenv("FASTAPI_URL", "http://localhost:8000")
        self.fastapi_key = _require_env("FASTAPI_KEY")
        self.mt5_login = int(_require_env("MT5_LOGIN"))
        self.mt5_password = _require_env("MT5_PASSWORD")
        self.mt5_server = _require_env("MT5_SERVER")
        self.running = False
        self._client: httpx.AsyncClient | None = None  # lazy init
        self._combiner = EnsembleCombiner()
        # Single-worker executor serialises Keras/TF graph access (fix #8)
        self._lstm_executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="lstm"
        )
        self._lstm: dict[str, LSTMSignalAdapter] = {
            sym: LSTMSignalAdapter(sym, ensemble_size=LSTM_ENSEMBLE) for sym in SYMBOLS
        }

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self._client

    # ─── Connection ──────────────────────────────────────────────────

    def connect(self) -> bool:
        if mt5 is None:
            log.error("MetaTrader5 dependency is not installed")
            return False
        if not mt5.initialize(
            login=self.mt5_login, password=self.mt5_password, server=self.mt5_server
        ):
            log.error(f"MT5 init failed: {mt5.last_error()}")
            return False

        info = mt5.account_info()
        if info is None:
            log.error(f"MT5 account_info() returned None: {mt5.last_error()}")
            mt5.shutdown()
            return False

        log.info(
            f"MT5 connected | Account:{info.login} "
            f"Balance:{info.balance:.2f} {info.currency}"
        )
        return True

    def disconnect(self) -> None:
        if mt5 is not None:
            mt5.shutdown()

    # ─── Data ────────────────────────────────────────────────────────

    def _get_df(self, symbol: str) -> pd.DataFrame | None:
        if mt5 is None:
            log.error("MetaTrader5 dependency is not installed")
            return None
        if ta is None:
            log.error("pandas_ta dependency is not installed")
            return None
        if TIMEFRAME is None:
            log.error("MT5 timeframe is unavailable")
            return None

        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, BARS)
        if rates is None or len(rates) == 0:
            return None

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)

        df["ema_fast"] = ta.ema(df["close"], length=9)
        df["ema_slow"] = ta.ema(df["close"], length=21)
        df["rsi"] = ta.rsi(df["close"], length=14)
        df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)

        stoch = ta.stoch(df["high"], df["low"], df["close"])
        if stoch is not None:
            df["stoch_k"] = stoch.get("STOCHk_14_3_3", pd.Series(50.0, index=df.index))
            df["stoch_d"] = stoch.get("STOCHd_14_3_3", pd.Series(50.0, index=df.index))
        else:
            df["stoch_k"] = 50.0
            df["stoch_d"] = 50.0

        macd = ta.macd(df["close"])
        df["macd_hist"] = (
            macd.get("MACDh_12_26_9", pd.Series(0.0, index=df.index))
            if macd is not None
            else 0.0
        )

        bb = ta.bbands(df["close"])
        if bb is not None:
            bb_up = bb.get("BBU_5_2.0", df["close"])
            bb_lo = bb.get("BBL_5_2.0", df["close"])
            rng = (bb_up - bb_lo).replace(0, 1)
            df["bb_pos"] = (df["close"] - bb_lo) / rng
        else:
            df["bb_pos"] = 0.5

        return df.dropna()

    # ─── Technical signal ────────────────────────────────────────────

    @staticmethod
    def _tech_signal(df: pd.DataFrame) -> TechnicalSignal | None:
        if len(df) < 3:
            return None

        lat, prv = df.iloc[-1], df.iloc[-2]
        price = float(lat["close"])
        atr = float(lat["atr"])
        rsi = float(lat["rsi"])
        ef, es = float(lat["ema_fast"]), float(lat["ema_slow"])
        pf, ps = float(prv["ema_fast"]), float(prv["ema_slow"])

        # Crossover detection
        if pf <= ps and ef > es and rsi < 70:
            direction: str = "BUY"
        elif pf >= ps and ef < es and rsi > 30:
            direction = "SELL"
        else:
            return None

        conf = 70.0

        # RSI confirmation zone
        if direction == "BUY" and 45 < rsi < 65:
            conf += 10
        if direction == "SELL" and 35 < rsi < 55:
            conf += 10

        # ATR-normalised EMA spread (fix #15: symbol-agnostic)
        spread_atr = abs(ef - es) / atr if atr > 0 else 0
        if spread_atr > SPREAD_ATR_MINOR:
            conf += 5
        if spread_atr > SPREAD_ATR_MAJOR:
            conf += 5

        sl = (
            price - atr * ATR_SL_MULT
            if direction == "BUY"
            else price + atr * ATR_SL_MULT
        )
        tp = (
            price + atr * ATR_TP_MULT
            if direction == "BUY"
            else price - atr * ATR_TP_MULT
        )

        return TechnicalSignal(
            direction=direction,  # type: ignore[arg-type]
            confidence=min(conf, 95.0),
            sl=round(sl, 5),
            tp=round(tp, 5),
        )

    # ─── Analyse one symbol ──────────────────────────────────────────

    async def _analyse(self, symbol: str, cycle_ts: str) -> dict | None:
        df = self._get_df(symbol)
        if df is None:
            return None

        price = float(df.iloc[-1]["close"])
        tech = self._tech_signal(df)
        if tech is None:
            return None

        loop = asyncio.get_running_loop()
        lstm = await loop.run_in_executor(
            self._lstm_executor, self._lstm[symbol].predict, df
        )

        log.info(
            f"[{symbol}] Tech={tech.direction}({tech.confidence:.0f}%) | "
            f"LSTM={lstm.direction}({lstm.confidence:.0f}%) "
            f"unc={lstm.lstm_uncertainty:.2f} regime={lstm.regime}"
        )
        if not lstm.available:
            log.warning(f"[{symbol}] LSTM unavailable; using technical-only combine")

        combined: CombinedSignal = self._combiner.combine(tech, lstm)

        if combined.blocked:
            log.info(f"[{symbol}] blocked: {combined.block_reason}")
            return None

        return {
            "symbol": symbol,
            "direction": combined.direction,
            "confidence": combined.confidence,
            "price": price,
            "stopLoss": combined.sl,
            "takeProfit": combined.tp,
            "riskPercent": RISK_PERCENT,
            "timestamp": cycle_ts,
            "meta": {
                "regime": combined.regime,
                "lstm_weight": round(combined.lstm_weight, 2),
                "technical_weight": round(combined.technical_weight, 2),
                "reasons": combined.reasons,
            },
        }

    # ─── Push to FastAPI ─────────────────────────────────────────────

    async def _push(self, payload: dict) -> bool:
        sym = payload["symbol"]
        try:
            r = await self.client.post(
                f"{self.fastapi_url}/signal",
                json=payload,
                headers={"X-API-Key": self.fastapi_key},
            )
            if r.status_code == 200:
                delivered = r.json().get("cf_result", {}).get("delivered", 0)
                log.info(
                    f"{payload['direction']} {sym} "
                    f"conf={payload['confidence']}% → {delivered} clients"
                )
                return True
            log.warning(f"[{sym}] FastAPI {r.status_code}: {r.text[:120]}")
        except httpx.RequestError as exc:
            log.error(f"[{sym}] Unreachable: {exc}")
        return False

    # ─── Main Loop ───────────────────────────────────────────────────

    async def run(self) -> None:
        self.running = True
        log.info(
            f"MT5 Bridge v3 | symbols={SYMBOLS} | "
            f"lstm_ensemble={LSTM_ENSEMBLE} | interval={POLL_INTERVAL}s"
        )
        while self.running:
            # Fix #13: one timestamp per cycle
            cycle_ts = datetime.now(timezone.utc).isoformat()

            results = await asyncio.gather(
                *[self._analyse(s, cycle_ts) for s in SYMBOLS],
                return_exceptions=True,
            )
            for sym, res in zip(SYMBOLS, results):
                if isinstance(res, Exception):
                    log.error(f"[{sym}] {res}")
                elif res is not None:
                    await self._push(res)

            await asyncio.sleep(POLL_INTERVAL)

    def stop(self) -> None:
        self.running = False


async def main() -> None:
    bridge = MT5Bridge()

    def _exit(*_: object) -> None:
        bridge.stop()

    signal.signal(signal.SIGINT, _exit)
    signal.signal(signal.SIGTERM, _exit)

    if not bridge.connect():
        sys.exit(1)
    try:
        await bridge.run()
    finally:
        bridge.disconnect()
        if bridge._client is not None:
            await bridge._client.aclose()
        bridge._lstm_executor.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    asyncio.run(main())
