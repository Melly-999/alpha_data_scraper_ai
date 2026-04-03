from __future__ import annotations

import datetime
import logging
import os
import tkinter as tk
from tkinter import ttk
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import mplfinance as mpf

    _MPF_OK = True
except ImportError:  # pragma: no cover
    _MPF_OK = False

import numpy as np
import pandas as pd

_SIGNAL_COLOR = {"BUY": "\033[92m", "SELL": "\033[91m", "HOLD": "\033[93m"}
_RESET = "\033[0m"

# ── Logging bridge ────────────────────────────────────────────────────────────
_gui_log_handler: "_GuiLogHandler | None" = None


class _GuiLogHandler(logging.Handler):
    """Capture log records and forward them to the GUI logs pane."""

    def __init__(self) -> None:
        super().__init__()
        self._widget: tk.Text | None = None

    def attach(self, widget: tk.Text) -> None:
        self._widget = widget

    def emit(self, record: logging.LogRecord) -> None:
        if self._widget is None:
            return
        try:
            msg = self.format(record) + "\n"
            self._widget.configure(state=tk.NORMAL)
            self._widget.insert(tk.END, msg)
            self._widget.see(tk.END)
            self._widget.configure(state=tk.DISABLED)
        except Exception:
            pass


def _fmt_autotrade(at: Any) -> str:
    if not isinstance(at, dict):
        return str(at)
    status = at.get("status", "?")
    extra = ""
    if status == "cooldown":
        extra = f" ({at.get('seconds_left', '?')}s left)"
    elif status in {"placed", "dry_run"}:
        req = at.get("request", {})
        extra = f" {req.get('side', '?')} {req.get('volume', '?')}lot @ {req.get('price', '?')}"
    return status + extra


def _fmt_close(close: float) -> str:
    return f"{close:.2f}" if close > 100 else f"{close:.5f}"


def _normalize(payload: Any) -> list[dict[str, Any]]:
    return payload if isinstance(payload, list) else [payload]


def render_console(payload: Any) -> None:
    """Render snapshot(s) to console.

    Accepts either a list of symbol dicts (multi-symbol) or a single dict
    (backward compat).
    """
    snapshots = _normalize(payload)
    col_sym = 8
    col_close = 10
    col_sig = 6
    col_conf = 7
    col_score = 6

    header = (
        f"{'SYMBOL':<{col_sym}} | "
        f"{'CLOSE':>{col_close}} | "
        f"{'SIGNAL':<{col_sig}} | "
        f"{'CONF%':>{col_conf}} | "
        f"{'SCORE':>{col_score}} | "
        "AUTOTRADE"
    )
    sep = "-" * len(header)
    print(f"=== Alpha AI Live Snapshot ({len(snapshots)} instruments) ===")
    print(header)
    print(sep)

    for snap in snapshots:
        sym = str(snap.get("symbol", "?"))
        sig_data = snap.get("signal", {})
        sig = str(sig_data.get("signal", "HOLD")).upper()
        conf = float(sig_data.get("confidence", 0.0))
        score = int(sig_data.get("score", 0))
        at_str = _fmt_autotrade(snap.get("autotrade", {}))
        err = snap.get("error")

        if err:
            print(f"{sym:<{col_sym}} | ERROR: {err}")
            continue

        color = _SIGNAL_COLOR.get(sig, "")
        close = float(snap.get("last_close", 0.0))
        close_str = _fmt_close(close)

        print(
            f"{sym:<{col_sym}} | "
            f"{close_str:>{col_close}} | "
            f"{color}{sig:<{col_sig}}{_RESET} | "
            f"{conf:>{col_conf}.1f} | "
            f"{score:>{col_score}} | "
            f"{at_str}"
        )
    print()


def run_live_gui(get_payload: Any, interval_seconds: float = 2.0) -> None:  # noqa: C901
    """Launch the Alpha AI Live Control Deck GUI.

    The window contains a sidebar navigator (Dashboard | Signals | Backtest |
    Settings | Logs) and a status bar at the bottom.  Dark mode is used by
    default and *icon.ico* is set as the window icon when present.
    """
    root = tk.Tk()
    root.title("Alpha AI Control Deck")
    root.geometry("1280x800")
    root.minsize(1100, 680)

    # ── Window icon ───────────────────────────────────────────────────────────
    try:
        root.iconbitmap("icon.ico")
    except Exception:
        pass

    # ── Colour palette ────────────────────────────────────────────────────────
    C = {
        "bg": "#0b1018",
        "sidebar": "#0d1520",
        "panel": "#131c2a",
        "panel_alt": "#0f1724",
        "text": "#e7ecf3",
        "muted": "#8b9bb2",
        "line": "#283447",
        "buy": "#2ecc71",
        "sell": "#e74c3c",
        "hold": "#f1c40f",
        "nav_active": "#1a2d45",
        "nav_hover": "#16253a",
    }

    root.configure(bg=C["bg"])

    # ── ttk styles ────────────────────────────────────────────────────────────
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Deck.TFrame", background=C["bg"])
    style.configure("Sidebar.TFrame", background=C["sidebar"])
    style.configure("Panel.TFrame", background=C["panel"])
    style.configure("PanelAlt.TFrame", background=C["panel_alt"])
    style.configure("Deck.TLabel", background=C["bg"], foreground=C["text"])
    style.configure("Muted.TLabel", background=C["bg"], foreground=C["muted"])
    style.configure("Panel.TLabel", background=C["panel"], foreground=C["text"])
    style.configure("PanelAlt.TLabel", background=C["panel_alt"], foreground=C["text"])
    style.configure("PanelAlt.Muted.TLabel", background=C["panel_alt"], foreground=C["muted"])
    style.configure("Sidebar.TLabel", background=C["sidebar"], foreground=C["muted"])
    style.configure(
        "CardLabel.TLabel", background=C["panel_alt"], foreground=C["muted"]
    )
    style.configure(
        "CardValue.TLabel",
        background=C["panel_alt"],
        foreground=C["text"],
        font=("Segoe UI Semibold", 17),
    )
    style.configure(
        "Deck.TButton",
        background=C["panel_alt"],
        foreground=C["text"],
        borderwidth=1,
    )
    style.map(
        "Deck.TButton",
        background=[("active", "#1b2940"), ("pressed", "#22334f")],
    )
    style.configure(
        "Nav.TButton",
        background=C["sidebar"],
        foreground=C["muted"],
        borderwidth=0,
        relief="flat",
        anchor="w",
        padding=(12, 10),
        font=("Segoe UI", 11),
    )
    style.map(
        "Nav.TButton",
        background=[("active", C["nav_hover"]), ("pressed", C["nav_active"])],
        foreground=[("active", C["text"])],
    )
    style.configure(
        "NavActive.TButton",
        background=C["nav_active"],
        foreground=C["text"],
        borderwidth=0,
        relief="flat",
        anchor="w",
        padding=(12, 10),
        font=("Segoe UI Semibold", 11),
    )
    style.configure("Deck.TEntry", fieldbackground=C["panel_alt"], foreground=C["text"])
    style.configure(
        "Deck.Treeview",
        background=C["panel"],
        fieldbackground=C["panel"],
        foreground=C["text"],
        rowheight=26,
        borderwidth=0,
    )
    style.configure(
        "Deck.Treeview.Heading",
        background="#1a2638",
        foreground="#d6deea",
        relief="flat",
    )
    style.map("Deck.Treeview.Heading", background=[("active", "#22324a")])
    style.configure(
        "Status.TLabel",
        background="#080f18",
        foreground=C["muted"],
        font=("Segoe UI", 9),
        padding=(6, 3),
    )

    # ── Root layout: sidebar | content ────────────────────────────────────────
    outer = ttk.Frame(root, style="Deck.TFrame")
    outer.pack(fill=tk.BOTH, expand=True)
    outer.grid_columnconfigure(1, weight=1)
    outer.grid_rowconfigure(0, weight=1)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    sidebar = ttk.Frame(outer, style="Sidebar.TFrame", width=160)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_propagate(False)

    ttk.Label(
        sidebar,
        text="α ALPHA AI",
        style="Sidebar.TLabel",
        font=("Segoe UI Semibold", 13),
    ).pack(fill=tk.X, padx=12, pady=(18, 20))

    # ── Content area ──────────────────────────────────────────────────────────
    content = ttk.Frame(outer, style="Deck.TFrame")
    content.grid(row=0, column=1, sticky="nsew")
    content.grid_rowconfigure(0, weight=1)
    content.grid_columnconfigure(0, weight=1)

    # ── Status bar ────────────────────────────────────────────────────────────
    statusbar = tk.Frame(root, bg="#080f18", height=24)
    statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    mt5_status_var = tk.StringVar(value="MT5: Disconnected")
    symbol_status_var = tk.StringVar(value="Symbol: —")
    tick_status_var = tk.StringVar(value="Last tick: —")

    for var, anchor in (
        (mt5_status_var, tk.W),
        (symbol_status_var, tk.CENTER),
        (tick_status_var, tk.E),
    ):
        tk.Label(
            statusbar,
            textvariable=var,
            bg="#080f18",
            fg=C["muted"],
            font=("Segoe UI", 9),
            anchor=anchor,
        ).pack(side=tk.LEFT, padx=10)

    # ── Shared state ──────────────────────────────────────────────────────────
    state: dict[str, Any] = {
        "running": True,
        "after_id": None,
        "last_payload": [],
        "by_symbol": {},
        "signal_history": [],  # list of (time, symbol, signal, conf)
        "open_positions": [],  # list of dicts
    }

    # ═════════════════════════════════════════════════════════════════════════
    # PAGE FRAMES
    # Each page is a full-size frame that is raised/lowered for navigation.
    # ═════════════════════════════════════════════════════════════════════════

    pages: dict[str, ttk.Frame] = {}

    def _make_page(name: str) -> ttk.Frame:
        f = ttk.Frame(content, style="Deck.TFrame", padding=14)
        f.grid(row=0, column=0, sticky="nsew")
        pages[name] = f
        return f

    # ── 1. DASHBOARD page ─────────────────────────────────────────────────────
    dash_page = _make_page("Dashboard")
    dash_page.grid_columnconfigure(0, weight=3)
    dash_page.grid_columnconfigure(1, weight=2)
    dash_page.grid_rowconfigure(1, weight=1)
    dash_page.grid_rowconfigure(2, weight=2)

    # Title row
    ttk.Label(
        dash_page,
        text="Alpha AI Live Control Deck",
        style="Deck.TLabel",
        font=("Segoe UI Semibold", 18),
    ).grid(row=0, column=0, sticky="w")
    ttk.Label(
        dash_page,
        text="Multi-instrument stream · signal intensity · autotrade status",
        style="Muted.TLabel",
    ).grid(row=0, column=1, sticky="e")

    # Summary cards
    cards_frame = ttk.Frame(dash_page, style="Deck.TFrame")
    cards_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    for i in range(4):
        cards_frame.grid_columnconfigure(i, weight=1)

    def _card(parent: Any, title_text: str, col: int) -> tk.StringVar:
        box = ttk.Frame(parent, style="PanelAlt.TFrame", padding=12)
        box.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 8, 0))
        ttk.Label(box, text=title_text, style="CardLabel.TLabel").pack(anchor="w")
        val = tk.StringVar(value="0")
        ttk.Label(box, textvariable=val, style="CardValue.TLabel").pack(anchor="w")
        return val

    count_var = _card(cards_frame, "Instruments", 0)
    buy_var = _card(cards_frame, "BUY", 1)
    sell_var = _card(cards_frame, "SELL", 2)
    hold_var = _card(cards_frame, "HOLD", 3)

    # Bottom row: chart (left) + signal panel + detail (right)
    chart_outer = ttk.Frame(dash_page, style="Panel.TFrame", padding=8)
    chart_outer.grid(row=2, column=0, sticky="nsew", padx=(0, 8), pady=(10, 0))
    chart_outer.grid_rowconfigure(1, weight=1)
    chart_outer.grid_columnconfigure(0, weight=1)

    ttk.Label(
        chart_outer,
        text="Candlestick Chart",
        style="Panel.TLabel",
        font=("Segoe UI Semibold", 11),
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    # Matplotlib / mplfinance canvas
    _chart_fig: plt.Figure
    _chart_canvas: FigureCanvasTkAgg

    if _MPF_OK:
        _chart_fig = plt.Figure(figsize=(5, 3), dpi=96, facecolor=C["panel"])
    else:
        _chart_fig = plt.Figure(figsize=(5, 3), dpi=96, facecolor=C["panel"])

    _chart_canvas = FigureCanvasTkAgg(_chart_fig, master=chart_outer)
    _chart_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

    def _draw_chart(ohlcv: pd.DataFrame | None) -> None:
        """Redraw candlestick chart with *ohlcv* data (or a placeholder)."""
        _chart_fig.clear()
        ax = _chart_fig.add_subplot(111)
        ax.set_facecolor(C["panel"])
        _chart_fig.patch.set_facecolor(C["panel"])
        ax.tick_params(colors=C["muted"], labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(C["line"])

        if ohlcv is not None and len(ohlcv) >= 2 and _MPF_OK:
            try:
                df = ohlcv.copy()
                df.index = pd.DatetimeIndex(df.index)
                _mc = mpf.make_marketcolors(
                    up=C["buy"], down=C["sell"], wick="inherit", edge="inherit"
                )
                _sty = mpf.make_mpf_style(
                    marketcolors=_mc,
                    facecolor=C["panel"],
                    figcolor=C["panel"],
                    gridcolor=C["line"],
                    gridstyle="--",
                )
                mpf.plot(
                    df.tail(60),
                    type="candle",
                    style=_sty,
                    ax=ax,
                    volume=False,
                )
            except Exception:
                ax.text(
                    0.5,
                    0.5,
                    "Chart unavailable",
                    color=C["muted"],
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
        elif ohlcv is not None and len(ohlcv) >= 2:
            # fallback: plain close-price line
            try:
                closes = ohlcv["close"].tail(60)
                ax.plot(closes.values, color=C["buy"], linewidth=1.2)
                ax.set_ylabel("Close", color=C["muted"], fontsize=8)
            except Exception:
                pass
        else:
            ax.text(
                0.5,
                0.5,
                "Waiting for data…",
                color=C["muted"],
                ha="center",
                va="center",
                transform=ax.transAxes,
            )

        _chart_canvas.draw()

    _draw_chart(None)

    # Right panel: signal panel + instrument detail
    right_panel = ttk.Frame(dash_page, style="Panel.TFrame", padding=10)
    right_panel.grid(row=2, column=1, sticky="nsew", pady=(10, 0))
    right_panel.grid_rowconfigure(1, weight=1)
    right_panel.grid_columnconfigure(0, weight=1)

    # ── Large signal panel ────────────────────────────────────────────────────
    sig_outer = tk.Frame(right_panel, bg=C["panel_alt"], pady=10)
    sig_outer.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    sig_outer.grid_columnconfigure(0, weight=1)

    signal_label_var = tk.StringVar(value="—")
    conf_label_var = tk.StringVar(value="Confidence: —")

    signal_big = tk.Label(
        sig_outer,
        textvariable=signal_label_var,
        bg=C["panel_alt"],
        fg=C["muted"],
        font=("Segoe UI Black", 38),
        anchor="center",
    )
    signal_big.grid(row=0, column=0, sticky="ew")

    conf_big = tk.Label(
        sig_outer,
        textvariable=conf_label_var,
        bg=C["panel_alt"],
        fg=C["muted"],
        font=("Segoe UI", 16),
        anchor="center",
    )
    conf_big.grid(row=1, column=0, sticky="ew")

    # ── Instrument detail / reasons ───────────────────────────────────────────
    detail_frame = ttk.Frame(right_panel, style="Panel.TFrame")
    detail_frame.grid(row=1, column=0, sticky="nsew")
    detail_frame.grid_rowconfigure(2, weight=1)
    detail_frame.grid_columnconfigure(0, weight=1)

    ttk.Label(
        detail_frame,
        text="Selected Instrument",
        style="Panel.TLabel",
        font=("Segoe UI Semibold", 11),
    ).grid(row=0, column=0, sticky="w")

    selected_var = tk.StringVar(value="-")
    ttk.Label(
        detail_frame,
        textvariable=selected_var,
        style="Panel.TLabel",
        font=("Segoe UI", 15),
    ).grid(row=1, column=0, sticky="w", pady=(0, 6))

    reasons = tk.Text(
        detail_frame,
        height=8,
        bg=C["panel_alt"],
        fg=C["text"],
        insertbackground=C["text"],
        highlightthickness=0,
        relief=tk.FLAT,
        wrap=tk.WORD,
        font=("Consolas", 10),
    )
    reasons.grid(row=2, column=0, sticky="nsew")

    # Interval controls + run state (top-right of dashboard)
    ctrl_bar = ttk.Frame(dash_page, style="Deck.TFrame")
    ctrl_bar.grid(row=0, column=1, sticky="e", padx=(0, 0))

    ttk.Label(ctrl_bar, text="Interval (s)", style="Muted.TLabel").pack(
        side=tk.LEFT, padx=(0, 6)
    )
    interval_var = tk.StringVar(value=f"{interval_seconds:.1f}")
    ttk.Entry(ctrl_bar, textvariable=interval_var, width=6, style="Deck.TEntry").pack(
        side=tk.LEFT, padx=(0, 8)
    )
    running_var = tk.StringVar(value="RUNNING")
    ttk.Label(ctrl_bar, textvariable=running_var, style="Deck.TLabel").pack(
        side=tk.LEFT, padx=(0, 8)
    )

    def _current_interval() -> float:
        try:
            v = float(interval_var.get())
            if v <= 0:
                raise ValueError
            return v
        except Exception:
            return max(interval_seconds, 0.1)

    def _update_reasons(symbol: str) -> None:
        snap = state["by_symbol"].get(symbol)
        reasons.delete("1.0", tk.END)
        if not snap:
            reasons.insert(tk.END, "No details available.")
            return
        if snap.get("error"):
            reasons.insert(tk.END, f"Error: {snap['error']}")
            return
        sig_data = snap.get("signal", {})
        lines = [
            f"Signal: {sig_data.get('signal', 'HOLD')}",
            f"Confidence: {sig_data.get('confidence', 0.0)}%",
            f"Score: {sig_data.get('score', 0)}",
            f"Autotrade: {_fmt_autotrade(snap.get('autotrade', {}))}",
            "",
            "Reasons:",
        ]
        for idx, reason in enumerate(sig_data.get("reasons", []), start=1):
            lines.append(f"{idx}. {reason}")
        reasons.insert(tk.END, "\n".join(lines))

    # ═════════════════════════════════════════════════════════════════════════
    # 2. SIGNALS page
    # ═════════════════════════════════════════════════════════════════════════
    sig_page = _make_page("Signals")
    sig_page.grid_columnconfigure(0, weight=1)
    sig_page.grid_columnconfigure(1, weight=1)
    sig_page.grid_rowconfigure(1, weight=1)

    ttk.Label(
        sig_page,
        text="Signals",
        style="Deck.TLabel",
        font=("Segoe UI Semibold", 18),
    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

    # Open positions table
    pos_frame = ttk.Frame(sig_page, style="Panel.TFrame", padding=10)
    pos_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
    pos_frame.grid_rowconfigure(1, weight=1)
    pos_frame.grid_columnconfigure(0, weight=1)

    ttk.Label(
        pos_frame,
        text="Open Positions",
        style="Panel.TLabel",
        font=("Segoe UI Semibold", 11),
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    pos_cols = ("symbol", "side", "volume", "open_price", "current", "pnl")
    pos_table = ttk.Treeview(
        pos_frame, columns=pos_cols, show="headings", style="Deck.Treeview"
    )
    pos_table.grid(row=1, column=0, sticky="nsew")
    _pos_headings = {
        "symbol": "Symbol",
        "side": "Side",
        "volume": "Vol",
        "open_price": "Open",
        "current": "Current",
        "pnl": "P&L",
    }
    _pos_widths = {"symbol": 80, "side": 55, "volume": 50, "open_price": 90, "current": 90, "pnl": 80}
    for c in pos_cols:
        pos_table.heading(c, text=_pos_headings[c])
        pos_table.column(c, width=_pos_widths[c], anchor="center")
    pos_table.tag_configure("BUY", foreground="#2ecc71")
    pos_table.tag_configure("SELL", foreground="#e74c3c")
    _pos_yscroll = ttk.Scrollbar(pos_frame, orient=tk.VERTICAL, command=pos_table.yview)
    _pos_yscroll.grid(row=1, column=1, sticky="ns")
    pos_table.configure(yscrollcommand=_pos_yscroll.set)

    # Signal history table
    hist_frame = ttk.Frame(sig_page, style="Panel.TFrame", padding=10)
    hist_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 0))
    hist_frame.grid_rowconfigure(1, weight=1)
    hist_frame.grid_columnconfigure(0, weight=1)

    ttk.Label(
        hist_frame,
        text="Signal History",
        style="Panel.TLabel",
        font=("Segoe UI Semibold", 11),
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    hist_cols = ("time", "symbol", "signal", "conf", "score")
    hist_table = ttk.Treeview(
        hist_frame, columns=hist_cols, show="headings", style="Deck.Treeview"
    )
    hist_table.grid(row=1, column=0, sticky="nsew")
    _hist_headings = {"time": "Time", "symbol": "Symbol", "signal": "Signal", "conf": "Conf %", "score": "Score"}
    _hist_widths = {"time": 110, "symbol": 80, "signal": 70, "conf": 70, "score": 60}
    for c in hist_cols:
        hist_table.heading(c, text=_hist_headings[c])
        hist_table.column(c, width=_hist_widths[c], anchor="center")
    hist_table.tag_configure("BUY", foreground="#2ecc71")
    hist_table.tag_configure("SELL", foreground="#e74c3c")
    hist_table.tag_configure("HOLD", foreground="#f1c40f")
    ttk.Scrollbar(hist_frame, orient=tk.VERTICAL, command=hist_table.yview).grid(
        row=1, column=1, sticky="ns"
    )

    # ═════════════════════════════════════════════════════════════════════════
    # 3. BACKTEST page (placeholder)
    # ═════════════════════════════════════════════════════════════════════════
    bt_page = _make_page("Backtest")
    bt_page.grid_rowconfigure(1, weight=1)
    bt_page.grid_columnconfigure(0, weight=1)

    ttk.Label(
        bt_page,
        text="Backtest",
        style="Deck.TLabel",
        font=("Segoe UI Semibold", 18),
    ).grid(row=0, column=0, sticky="w", pady=(0, 10))

    bt_inner = ttk.Frame(bt_page, style="Panel.TFrame", padding=30)
    bt_inner.grid(row=1, column=0, sticky="nsew")
    bt_inner.grid_rowconfigure(0, weight=1)
    bt_inner.grid_columnconfigure(0, weight=1)

    ttk.Label(
        bt_inner,
        text="Backtest engine — coming soon",
        style="Panel.TLabel",
        font=("Segoe UI", 14),
    ).grid(row=0, column=0)
    ttk.Label(
        bt_inner,
        text=(
            "Configure a date range and strategy parameters here.\n"
            "Results will be displayed as equity curves and trade logs."
        ),
        style="Panel.TLabel",
        font=("Segoe UI", 10),
        justify="center",
    ).grid(row=1, column=0, pady=(8, 0))

    # ═════════════════════════════════════════════════════════════════════════
    # 4. SETTINGS page
    # ═════════════════════════════════════════════════════════════════════════
    set_page = _make_page("Settings")
    set_page.grid_columnconfigure(0, weight=1)
    set_page.grid_rowconfigure(1, weight=1)

    ttk.Label(
        set_page,
        text="Settings",
        style="Deck.TLabel",
        font=("Segoe UI Semibold", 18),
    ).grid(row=0, column=0, sticky="w", pady=(0, 10))

    set_inner = ttk.Frame(set_page, style="Panel.TFrame", padding=20)
    set_inner.grid(row=1, column=0, sticky="nsew")
    set_inner.grid_columnconfigure(1, weight=1)

    # Switch row helper
    def _switch_row(parent: ttk.Frame, row: int, label: str, default: bool = False) -> tk.BooleanVar:
        var = tk.BooleanVar(value=default)
        ttk.Label(parent, text=label, style="Panel.TLabel", font=("Segoe UI", 11)).grid(
            row=row, column=0, sticky="w", pady=8, padx=(0, 20)
        )
        ttk.Checkbutton(parent, variable=var, style="TCheckbutton").grid(
            row=row, column=1, sticky="w"
        )
        return var

    autotrade_var = _switch_row(set_inner, 0, "Auto-trade", default=False)
    dryrun_var = _switch_row(set_inner, 1, "Dry-run mode", default=True)

    # Profile selector
    ttk.Label(
        set_inner, text="Profile", style="Panel.TLabel", font=("Segoe UI", 11)
    ).grid(row=2, column=0, sticky="w", pady=8)

    _profiles_dir = os.path.join(os.path.dirname(__file__) or ".", "profiles")
    _profile_names: list[str] = []
    try:
        _profile_names = [
            os.path.splitext(f)[0]
            for f in sorted(os.listdir(_profiles_dir))
            if f.endswith(".json")
        ]
    except OSError:
        _profile_names = ["default"]

    profile_var = tk.StringVar(value=_profile_names[0] if _profile_names else "default")
    profile_menu = ttk.Combobox(
        set_inner,
        textvariable=profile_var,
        values=_profile_names,
        state="readonly",
        width=24,
    )
    profile_menu.grid(row=2, column=1, sticky="w", pady=8)

    # Apply button
    apply_status_var = tk.StringVar(value="")

    def _apply_settings() -> None:
        apply_status_var.set(
            f"Saved — Auto-trade: {'ON' if autotrade_var.get() else 'OFF'}  "
            f"Dry-run: {'ON' if dryrun_var.get() else 'OFF'}  "
            f"Profile: {profile_var.get()}"
        )
        logging.getLogger(__name__).info(
            "Settings applied: autotrade=%s dry_run=%s profile=%s",
            autotrade_var.get(),
            dryrun_var.get(),
            profile_var.get(),
        )

    ttk.Button(
        set_inner, text="Apply", command=_apply_settings, style="Deck.TButton"
    ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(16, 0))

    ttk.Label(
        set_inner,
        textvariable=apply_status_var,
        style="Panel.TLabel",
        font=("Segoe UI", 9),
    ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 0))

    # ═════════════════════════════════════════════════════════════════════════
    # 5. LOGS page
    # ═════════════════════════════════════════════════════════════════════════
    log_page = _make_page("Logs")
    log_page.grid_columnconfigure(0, weight=1)
    log_page.grid_rowconfigure(1, weight=1)

    ttk.Label(
        log_page,
        text="Logs",
        style="Deck.TLabel",
        font=("Segoe UI Semibold", 18),
    ).grid(row=0, column=0, sticky="w", pady=(0, 10))

    log_frame = ttk.Frame(log_page, style="Panel.TFrame", padding=6)
    log_frame.grid(row=1, column=0, sticky="nsew")
    log_frame.grid_rowconfigure(0, weight=1)
    log_frame.grid_columnconfigure(0, weight=1)

    log_text = tk.Text(
        log_frame,
        bg=C["panel_alt"],
        fg=C["text"],
        insertbackground=C["text"],
        highlightthickness=0,
        relief=tk.FLAT,
        font=("Consolas", 10),
        wrap=tk.WORD,
        state=tk.DISABLED,
    )
    log_text.grid(row=0, column=0, sticky="nsew")
    log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
    log_scroll.grid(row=0, column=1, sticky="ns")
    log_text.configure(yscrollcommand=log_scroll.set)

    ttk.Button(
        log_page,
        text="Clear",
        command=lambda: (
            log_text.configure(state=tk.NORMAL),
            log_text.delete("1.0", tk.END),
            log_text.configure(state=tk.DISABLED),
        ),
        style="Deck.TButton",
    ).grid(row=2, column=0, sticky="w", pady=(6, 0))

    # Attach GUI log handler
    global _gui_log_handler
    _gui_log_handler = _GuiLogHandler()
    _gui_log_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
    )
    _gui_log_handler.attach(log_text)
    logging.getLogger().addHandler(_gui_log_handler)

    # ═════════════════════════════════════════════════════════════════════════
    # LIVE MARKET TABLE  (inside Dashboard)
    # ═════════════════════════════════════════════════════════════════════════
    # Placed inside a sub-frame below the chart area in Dashboard
    table_frame = ttk.Frame(dash_page, style="Panel.TFrame", padding=8)
    table_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
    table_frame.grid_rowconfigure(1, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    dash_page.grid_rowconfigure(3, weight=1)

    ttk.Label(
        table_frame,
        text="Live Market Table",
        style="Panel.TLabel",
        font=("Segoe UI Semibold", 11),
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    columns = ("symbol", "close", "signal", "conf", "score", "delta", "autotrade")
    table = ttk.Treeview(
        table_frame, columns=columns, show="headings", style="Deck.Treeview", selectmode="browse"
    )
    table.grid(row=1, column=0, sticky="nsew")

    headings = {
        "symbol": "Symbol",
        "close": "Close",
        "signal": "Signal",
        "conf": "Conf %",
        "score": "Score",
        "delta": "LSTM Δ",
        "autotrade": "Autotrade",
    }
    widths = {
        "symbol": 90,
        "close": 110,
        "signal": 80,
        "conf": 80,
        "score": 70,
        "delta": 100,
        "autotrade": 340,
    }
    for col in columns:
        table.heading(col, text=headings[col])
        table.column(col, width=widths[col], anchor="center")

    table.tag_configure("BUY", foreground=C["buy"])
    table.tag_configure("SELL", foreground=C["sell"])
    table.tag_configure("HOLD", foreground=C["hold"])
    table.tag_configure("ERROR", foreground=C["sell"])

    yscroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
    table.configure(yscrollcommand=yscroll.set)
    yscroll.grid(row=1, column=1, sticky="ns")

    def _on_table_select(_: Any) -> None:
        selection = table.selection()
        if not selection:
            return
        symbol = table.item(selection[0], "values")[0]
        selected_var.set(symbol)
        _update_reasons(symbol)
        # Update signal panel
        snap = state["by_symbol"].get(symbol, {})
        sig_data = snap.get("signal", {}) if snap else {}
        sig = str(sig_data.get("signal", "HOLD")).upper()
        conf = float(sig_data.get("confidence", 0.0))
        _refresh_signal_panel(sig, conf)

    table.bind("<<TreeviewSelect>>", _on_table_select)

    # ═════════════════════════════════════════════════════════════════════════
    # SIDEBAR NAVIGATION
    # ═════════════════════════════════════════════════════════════════════════
    _nav_buttons: dict[str, ttk.Button] = {}
    _active_page = tk.StringVar(value="Dashboard")

    def _show_page(name: str) -> None:
        _active_page.set(name)
        pages[name].tkraise()
        for n, btn in _nav_buttons.items():
            btn.configure(style="NavActive.TButton" if n == name else "Nav.TButton")

    _nav_labels = ["Dashboard", "Signals", "Backtest", "Settings", "Logs"]
    _nav_icons = {
        "Dashboard": "⬛",
        "Signals": "📊",
        "Backtest": "🔄",
        "Settings": "⚙",
        "Logs": "📋",
    }
    for _n in _nav_labels:
        _btn = ttk.Button(
            sidebar,
            text=f"  {_nav_icons.get(_n, '')} {_n}",
            style="Nav.TButton",
            command=lambda name=_n: _show_page(name),
        )
        _btn.pack(fill=tk.X, pady=1)
        _nav_buttons[_n] = _btn

    _show_page("Dashboard")

    # ═════════════════════════════════════════════════════════════════════════
    # DATA / RENDER HELPERS
    # ═════════════════════════════════════════════════════════════════════════

    def _refresh_signal_panel(sig: str, conf: float) -> None:
        """Update the large signal panel colours and text."""
        color_map = {"BUY": C["buy"], "SELL": C["sell"], "HOLD": C["hold"]}
        color = color_map.get(sig, C["muted"])
        signal_label_var.set(sig)
        conf_label_var.set(f"Confidence: {conf:.1f}%")
        signal_big.configure(fg=color)
        conf_big.configure(fg=color)

    def _render_payload(payload: Any) -> None:
        snapshots = _normalize(payload)
        state["last_payload"] = snapshots
        state["by_symbol"] = {str(s.get("symbol", "?")): s for s in snapshots}

        for item in table.get_children():
            table.delete(item)

        buy_count = 0
        sell_count = 0
        hold_count = 0
        now_str = datetime.datetime.now().strftime("%H:%M:%S")

        for snap in snapshots:
            symbol = str(snap.get("symbol", "?"))
            if snap.get("error"):
                table.insert(
                    "", tk.END,
                    values=(symbol, "-", "ERR", "-", "-", "-", snap.get("error")),
                    tags=("ERROR",),
                )
                continue

            sig_data = snap.get("signal", {})
            signal = str(sig_data.get("signal", "HOLD")).upper()
            conf = float(sig_data.get("confidence", 0.0))
            score = int(sig_data.get("score", 0))
            close = float(snap.get("last_close", 0.0))
            delta = float(snap.get("lstm_delta", 0.0))

            if signal == "BUY":
                buy_count += 1
            elif signal == "SELL":
                sell_count += 1
            else:
                hold_count += 1

            row = (
                symbol,
                _fmt_close(close),
                signal,
                f"{conf:.1f}",
                str(score),
                f"{delta:+.5f}" if abs(delta) < 100 else f"{delta:+.3f}",
                _fmt_autotrade(snap.get("autotrade", {})),
            )
            table.insert("", tk.END, values=row, tags=(signal,))

            # Append to signal history (keep last 200)
            state["signal_history"].append((now_str, symbol, signal, f"{conf:.1f}", str(score)))
            if len(state["signal_history"]) > 200:
                state["signal_history"].pop(0)

        count_var.set(str(len(snapshots)))
        buy_var.set(str(buy_count))
        sell_var.set(str(sell_count))
        hold_var.set(str(hold_count))

        # Update selected instrument
        selected = selected_var.get()
        if selected in state["by_symbol"]:
            _update_reasons(selected)
            snap = state["by_symbol"][selected]
            sig_data = snap.get("signal", {})
            sig = str(sig_data.get("signal", "HOLD")).upper()
            conf_val = float(sig_data.get("confidence", 0.0))
            _refresh_signal_panel(sig, conf_val)
        elif snapshots:
            first_symbol = str(snapshots[0].get("symbol", "-"))
            selected_var.set(first_symbol)
            _update_reasons(first_symbol)
            snap0 = snapshots[0]
            sig_data0 = snap0.get("signal", {})
            sig0 = str(sig_data0.get("signal", "HOLD")).upper()
            conf0 = float(sig_data0.get("confidence", 0.0))
            _refresh_signal_panel(sig0, conf0)

        # Update signal history table
        for item in hist_table.get_children():
            hist_table.delete(item)
        for entry in reversed(state["signal_history"][-50:]):
            hist_table.insert("", tk.END, values=entry, tags=(entry[2],))

        # Update open positions table (use payload positions if provided)
        if snapshots and snapshots[0].get("open_positions") is not None:
            for item in pos_table.get_children():
                pos_table.delete(item)
            for pos in snapshots[0]["open_positions"]:
                pos_table.insert(
                    "", tk.END,
                    values=(
                        pos.get("symbol", "?"),
                        pos.get("side", "?"),
                        pos.get("volume", "?"),
                        pos.get("open_price", "?"),
                        pos.get("current", "?"),
                        pos.get("pnl", "?"),
                    ),
                    tags=(str(pos.get("side", "")).upper(),),
                )

        # Update status bar
        first_sym = str(snapshots[0].get("symbol", "—")) if snapshots else "—"
        symbol_status_var.set(f"Symbol: {first_sym}")
        tick_status_var.set(f"Last tick: {now_str}")
        mt5_status_var.set("MT5: Connected" if snapshots else "MT5: Disconnected")

        # Redraw chart with OHLCV if available
        ohlcv_raw = snapshots[0].get("ohlcv") if snapshots else None
        if ohlcv_raw is not None:
            try:
                _draw_chart(pd.DataFrame(ohlcv_raw).set_index("time"))
            except Exception:
                pass

    def _refresh_once() -> None:
        try:
            payload = get_payload()
            _render_payload(payload)
            next_interval = _current_interval()
            logging.getLogger(__name__).debug(
                "Refreshed — interval %.1fs", next_interval
            )
        except Exception as exc:
            mt5_status_var.set(f"MT5: Error — {exc}")
            logging.getLogger(__name__).warning("Update error: %s", exc)

    def _refresh_loop() -> None:
        if not state["running"]:
            return
        _refresh_once()
        state["after_id"] = root.after(int(_current_interval() * 1000), _refresh_loop)

    def _start() -> None:
        if state["running"]:
            return
        state["running"] = True
        running_var.set("RUNNING")
        _refresh_loop()

    def _stop() -> None:
        state["running"] = False
        running_var.set("PAUSED")
        if state["after_id"] is not None:
            root.after_cancel(state["after_id"])
            state["after_id"] = None

    ttk.Button(ctrl_bar, text="Start", command=_start, style="Deck.TButton").pack(
        side=tk.LEFT, padx=(0, 4)
    )
    ttk.Button(ctrl_bar, text="Pause", command=_stop, style="Deck.TButton").pack(
        side=tk.LEFT, padx=(0, 4)
    )
    ttk.Button(ctrl_bar, text="⟳", command=_refresh_once, style="Deck.TButton").pack(
        side=tk.LEFT
    )

    _refresh_loop()
    root.mainloop()
