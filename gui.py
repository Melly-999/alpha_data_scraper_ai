import logging
import traceback
import tkinter as tk
from tkinter import scrolledtext, messagebox
import queue
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter

from trading_engine import TradingEngine, EngineSnapshot

logger = logging.getLogger("GrokAlpha")


class GrokAlphaGUI:
    def __init__(self, config):
        self.config = config
        self.symbol = config["symbol"]
        self.version = config["version"]
        self.update_ms = config["update_ms"]
        self.conf_threshold = config["conf_threshold"]
        self.seq_length = config["seq_length"]
        self.slope_factor = config.get("slope_factor", 25)
        self.chart_throttle = config.get("chart_throttle", 5)
        self._tick_counter = 0

        self.prices = []
        self.times = []
        self.current_price = None
        self.logs = []
        self.session_start = 706.88

        self._engine_queue: "queue.Queue[EngineSnapshot]" = queue.Queue(maxsize=5)
        self.engine = TradingEngine(config, self._engine_queue)
        try:
            self.engine.start()
        except Exception:
            messagebox.showerror("Błąd", "Nie można zainicjować MT5 / engine")
            raise SystemExit

        self.root = tk.Tk()
        self.root.title(f"Grok Alpha AI Terminal GUI {self.version}")
        self.root.configure(bg="#0a0a0a")
        self.root.geometry("1460x860")
        self.create_ui()
        self.poll_engine()

    def create_ui(self):
        left_frame = tk.Frame(self.root, bg="#0a0a0a", width=740)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        tk.Label(
            left_frame,
            text=f"AI TRADING Terminal Grok Alpha AI [{self.version}]",
            font=("Consolas", 14, "bold"),
            fg="#00ff00",
            bg="#0a0a0a",
        ).pack(anchor="w")
        tk.Label(
            left_frame,
            text=f"Symbol: {self.symbol} | 3-Layer LSTM + RSI Fusion + Stochastic",
            font=("Consolas", 10),
            fg="#00ccff",
            bg="#0a0a0a",
        ).pack(anchor="w")

        self.stats_text = tk.Text(
            left_frame, height=17, bg="#111111", fg="#00ff00", font=("Consolas", 10)
        )
        self.stats_text.pack(fill=tk.X, pady=8)

        self.conf_label = tk.Label(
            left_frame,
            text="AI CONFIDENCE: [####################] 33.0%",
            font=("Consolas", 13, "bold"),
            fg="#ffff00",
            bg="#0a0a0a",
        )
        self.conf_label.pack(anchor="w", pady=6)

        tk.Label(
            left_frame,
            text="[RECENT LOGS] - 3-Layer LSTM + RSI Signals",
            font=("Consolas", 10, "bold"),
            fg="#00ffff",
            bg="#0a0a0a",
        ).pack(anchor="w")
        self.log_area = scrolledtext.ScrolledText(
            left_frame, height=13, bg="#111111", fg="#00ffaa", font=("Consolas", 9)
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)

        self.status_label = tk.Label(
            left_frame,
            text="🔴 Czekam na sygnał | Dynamic Holding Time: NEUTRAL",
            font=("Consolas", 11, "bold"),
            fg="#ff8800",
            bg="#0a0a0a",
        )
        self.status_label.pack(anchor="w", pady=8)

        right_frame = tk.Frame(self.root, bg="#0a0a0a")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.fig, self.ax = plt.subplots(figsize=(7.6, 6.4), facecolor="#0a0a0a")
        self.ax.set_facecolor("#111111")
        self.canvas = FigureCanvasTkAgg(self.fig, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self.root, bg="#0a0a0a")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=8)
        tk.Button(
            btn_frame,
            text="STOP & ZAMKNIJ",
            command=self.shutdown,
            bg="#ff4444",
            fg="white",
            font=("Consolas", 11, "bold"),
        ).pack(side=tk.RIGHT, padx=25)
        tk.Button(
            btn_frame,
            text="Wyczyść logi",
            command=self.clear_logs,
            bg="#333333",
            fg="white",
        ).pack(side=tk.RIGHT, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

    def poll_engine(self):
        try:
            self._tick_counter += 1

            snap = None
            while True:
                try:
                    snap = self._engine_queue.get_nowait()
                except queue.Empty:
                    break

            if snap is None:
                self.root.after(self.update_ms, self.poll_engine)
                return

            self.current_price = snap.price
            self.prices.append(snap.price)
            self.times.append(snap.ts)
            if len(self.prices) > 200:
                self.prices.pop(0)
                self.times.pop(0)

            if snap.signal and snap.confidence >= self.conf_threshold:
                log_msg = (
                    f"[{snap.ts.strftime('%H:%M:%S')}] [AI] {snap.signal} | "
                    f"Conf:{snap.confidence}% | LSTM+RSI:{snap.lstm_dir} | "
                    f"StochK:{snap.stoch_k:.1f} | {snap.hold_mode}"
                )
                self.logs.append(log_msg)
                if len(self.logs) > 15:
                    self.logs.pop(0)

            self.update_terminal_from_snapshot(snap)

            if self._tick_counter % self.chart_throttle == 0:
                self.update_chart()

        except Exception:
            logger.error("Error in update loop: %s", traceback.format_exc())

        self.root.after(self.update_ms, self.poll_engine)

    def update_terminal_from_snapshot(self, snap: EngineSnapshot):
        equity = snap.equity if snap.equity is not None else 706.88
        profit = equity - self.session_start
        stats = f"""EQUITY     : ${equity:.2f}
P/L        : ${profit:.2f}
SLOPE      : {snap.slope:.4f}
Bid/Ask    : {snap.bid:.3f} / {snap.ask:.3f}

RSI 14     : {snap.rsi:.1f}
MACD Hist  : {snap.macd_hist:+.4f}
BB Pos     : {snap.bb_pos:+.1f}%
Stochastic : %K {snap.stoch_k:.1f}  %D {snap.stoch_d:.1f}

LSTM+RSI   : {'↑ BULLISH' if snap.lstm_dir > 0 else '↓ BEARISH' if snap.lstm_dir < 0 else 'NEUTRAL'} (3 layers)
AI CONF    : {snap.confidence}%   REQ: {self.conf_threshold}%
TODAY PROFIT: +{profit:.2f} USD (Goal 15.00)
        """
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)

        bar = "#" * (snap.confidence // 4) + " " * (20 - snap.confidence // 4)
        self.conf_label.config(text=f"AI CONFIDENCE : [{bar}] {snap.confidence}%")

        self.log_area.delete(1.0, tk.END)
        for log in self.logs[-13:]:
            self.log_area.insert(tk.END, log + "\n")

        risk_suffix = "" if snap.risk_ok else f" | RISK: {snap.risk_reason}"
        self.status_label.config(
            text=f"{'🟢' if snap.confidence >= self.conf_threshold else '🔴'} "
            f"Sygnał: {snap.signal or 'BRAK'} | Dynamic Holding Time: {snap.hold_mode}{risk_suffix}",
            fg="#00ff00" if snap.confidence >= self.conf_threshold and snap.risk_ok else "#ff8800",
        )

    def update_chart(self):
        self.ax.clear()
        if len(self.prices) < 5 or len(self.prices) != len(self.times):
            self.canvas.draw()
            return

        df_plot = pd.DataFrame({"time": self.times, "close": self.prices})
        self.ax.plot(df_plot["time"], df_plot["close"], color="#00ffaa", linewidth=2.3)
        self.ax.set_title(
            f"{self.symbol} Live - 3-Layer LSTM + RSI Fusion (Refactored)",
            color="white",
            fontsize=13,
        )
        self.ax.grid(True, alpha=0.3)
        self.ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
        self.ax.tick_params(colors="#aaaaaa")
        for spine in self.ax.spines.values():
            spine.set_color("#555555")
        self.fig.tight_layout()
        self.canvas.draw()

    def clear_logs(self):
        self.logs.clear()
        self.log_area.delete(1.0, tk.END)

    def shutdown(self):
        try:
            self.engine.stop()
        finally:
            self.root.destroy()
