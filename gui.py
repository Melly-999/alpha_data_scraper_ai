from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

# ── Grid visualiser helpers ───────────────────────────────────────────────────

_GRID_COLORS = {
    "current": "#ffffff",
    "vwap": "#f1c40f",
    "resistance": "#e74c3c",
    "support": "#2ecc71",
    "default": "#4a5568",
}


def _draw_grid(canvas: tk.Canvas, levels: list[dict[str, Any]], signal: str, conf: float) -> None:
    """Render price grid levels on a Tkinter Canvas widget."""
    canvas.delete("all")
    if not levels:
        canvas.create_text(10, 80, anchor="nw", text="No grid data", fill="#8b9bb2",
                           font=("Consolas", 10))
        return

    w = int(canvas["width"])
    h = int(canvas["height"])
    pad = 22
    prices = [lv["price"] for lv in levels]
    hi, lo = max(prices), min(prices)
    price_range = hi - lo or 1e-9

    def to_y(price: float) -> float:
        return pad + (1.0 - (price - lo) / price_range) * (h - 2 * pad)

    for lv in levels:
        y = to_y(lv["price"])
        color = _GRID_COLORS.get(lv["type"], _GRID_COLORS["default"])
        is_cur = lv["type"] == "current"
        dash = () if is_cur else (4, 4)
        width = 2 if is_cur else 1

        canvas.create_line(44, y, w - 64, y, fill=color, width=width, dash=dash)

        if is_cur:
            canvas.create_oval(40, y - 5, 50, y + 5, fill=color, outline="")

        canvas.create_text(40, y, anchor="e", text=lv["label"], fill=color,
                           font=("Consolas", 8))
        price_str = f"{lv['price']:.2f}" if lv["price"] > 100 else f"{lv['price']:.5f}"
        canvas.create_text(w - 62, y, anchor="w", text=price_str, fill=color,
                           font=("Consolas", 8))

    sig_color = {"BUY": "#2ecc71", "SELL": "#e74c3c"}.get(signal, "#f1c40f")
    canvas.create_text(w // 2, h - 8, text=f"{signal}  {conf:.1f}%",
                       fill=sig_color, font=("Consolas", 11, "bold"))


_SIGNAL_COLOR = {"BUY": "\033[92m", "SELL": "\033[91m", "HOLD": "\033[93m"}
_RESET = "\033[0m"


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


def run_live_gui(get_payload: Any, interval_seconds: float = 2.0) -> None:
    root = tk.Tk()
    root.title("Alpha AI Control Deck")
    root.geometry("1200x760")
    root.minsize(1000, 620)

    colors = {
        "bg": "#0b1018",
        "panel": "#131c2a",
        "panel_alt": "#0f1724",
        "text": "#e7ecf3",
        "muted": "#8b9bb2",
        "line": "#283447",
        "buy": "#2ecc71",
        "sell": "#e74c3c",
        "hold": "#f1c40f",
    }

    root.configure(bg=colors["bg"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Deck.TFrame", background=colors["bg"])
    style.configure("Panel.TFrame", background=colors["panel"])
    style.configure("PanelAlt.TFrame", background=colors["panel_alt"])
    style.configure("Deck.TLabel", background=colors["bg"], foreground=colors["text"])
    style.configure("Muted.TLabel", background=colors["bg"], foreground=colors["muted"])
    style.configure("Panel.TLabel", background=colors["panel"], foreground=colors["text"])
    style.configure("CardLabel.TLabel", background=colors["panel_alt"], foreground=colors["muted"])
    style.configure("CardValue.TLabel", background=colors["panel_alt"], foreground=colors["text"], font=("Segoe UI Semibold", 17))
    style.configure("Deck.TButton", background=colors["panel_alt"], foreground=colors["text"], borderwidth=1)
    style.map("Deck.TButton", background=[("active", "#1b2940"), ("pressed", "#22334f")])
    style.configure("Deck.TEntry", fieldbackground=colors["panel_alt"], foreground=colors["text"])

    style.configure(
        "Deck.Treeview",
        background=colors["panel"],
        fieldbackground=colors["panel"],
        foreground=colors["text"],
        rowheight=26,
        borderwidth=0,
    )
    style.configure("Deck.Treeview.Heading", background="#1a2638", foreground="#d6deea", relief="flat")
    style.map("Deck.Treeview.Heading", background=[("active", "#22324a")])

    layout = ttk.Frame(root, style="Deck.TFrame", padding=12)
    layout.pack(fill=tk.BOTH, expand=True)
    layout.grid_columnconfigure(0, weight=5)
    layout.grid_columnconfigure(1, weight=3)
    layout.grid_rowconfigure(2, weight=1)

    title = ttk.Label(layout, text="Alpha AI Live Control Deck", style="Deck.TLabel", font=("Segoe UI Semibold", 20))
    title.grid(row=0, column=0, sticky="w")
    subtitle = ttk.Label(layout, text="Multi-instrument stream, signal intensity, and autotrade status", style="Muted.TLabel")
    subtitle.grid(row=1, column=0, sticky="w", pady=(0, 8))

    controls = ttk.Frame(layout, style="Deck.TFrame")
    controls.grid(row=0, column=1, rowspan=2, sticky="e")

    ttk.Label(controls, text="Interval (s)", style="Muted.TLabel").pack(side=tk.LEFT, padx=(0, 6))
    interval_var = tk.StringVar(value=f"{interval_seconds:.1f}")
    ttk.Entry(controls, textvariable=interval_var, width=6, style="Deck.TEntry").pack(side=tk.LEFT, padx=(0, 10))
    running_var = tk.StringVar(value="RUNNING")
    ttk.Label(controls, textvariable=running_var, style="Deck.TLabel").pack(side=tk.LEFT, padx=(0, 10))

    cards = ttk.Frame(layout, style="Deck.TFrame")
    cards.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
    cards.grid_columnconfigure(0, weight=1)
    cards.grid_columnconfigure(1, weight=1)
    cards.grid_columnconfigure(2, weight=1)
    cards.grid_columnconfigure(3, weight=1)

    def _card(parent: Any, title_text: str, col: int) -> tk.StringVar:
        box = ttk.Frame(parent, style="PanelAlt.TFrame", padding=12)
        box.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 8, 0))
        ttk.Label(box, text=title_text, style="CardLabel.TLabel").pack(anchor="w")
        val = tk.StringVar(value="0")
        ttk.Label(box, textvariable=val, style="CardValue.TLabel").pack(anchor="w")
        return val

    count_var = _card(cards, "Instruments", 0)
    buy_var = _card(cards, "BUY", 1)
    sell_var = _card(cards, "SELL", 2)
    hold_var = _card(cards, "HOLD", 3)

    left = ttk.Frame(layout, style="Panel.TFrame", padding=10)
    left.grid(row=3, column=0, sticky="nsew", padx=(0, 10))
    left.grid_rowconfigure(1, weight=1)
    left.grid_columnconfigure(0, weight=1)

    ttk.Label(left, text="Live Market Table", style="Panel.TLabel", font=("Segoe UI Semibold", 12)).grid(row=0, column=0, sticky="w", pady=(0, 8))

    columns = ("symbol", "close", "signal", "conf", "score", "delta", "autotrade")
    table = ttk.Treeview(left, columns=columns, show="headings", style="Deck.Treeview", selectmode="browse")
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

    table.tag_configure("BUY", foreground=colors["buy"])
    table.tag_configure("SELL", foreground=colors["sell"])
    table.tag_configure("HOLD", foreground=colors["hold"])
    table.tag_configure("ERROR", foreground=colors["sell"])

    yscroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=table.yview)
    table.configure(yscrollcommand=yscroll.set)
    yscroll.grid(row=1, column=1, sticky="ns")

    right = ttk.Frame(layout, style="Panel.TFrame", padding=10)
    right.grid(row=3, column=1, sticky="nsew")
    right.grid_rowconfigure(3, weight=1)
    right.grid_columnconfigure(0, weight=1)

    ttk.Label(right, text="Selected Instrument", style="Panel.TLabel", font=("Segoe UI Semibold", 12)).grid(row=0, column=0, sticky="w")
    selected_var = tk.StringVar(value="-")
    ttk.Label(right, textvariable=selected_var, style="Panel.TLabel", font=("Segoe UI", 16)).grid(row=1, column=0, sticky="w", pady=(0, 8))

    status_var = tk.StringVar(value="Waiting for first update...")
    ttk.Label(right, textvariable=status_var, style="Muted.TLabel", wraplength=360).grid(row=2, column=0, sticky="w", pady=(0, 8))

    reasons = tk.Text(
        right,
        height=7,
        bg=colors["panel_alt"],
        fg=colors["text"],
        insertbackground=colors["text"],
        highlightthickness=0,
        relief=tk.FLAT,
        wrap=tk.WORD,
        font=("Consolas", 10),
    )
    reasons.grid(row=3, column=0, sticky="nsew")

    # Feature 4: grid visualiser canvas
    right.grid_rowconfigure(4, weight=2)
    ttk.Label(right, text="Grid Levels", style="Panel.TLabel",
              font=("Segoe UI Semibold", 10)).grid(row=4, column=0, sticky="w", pady=(8, 2))
    grid_canvas = tk.Canvas(
        right, bg=colors["panel_alt"], highlightthickness=0,
        width=320, height=180,
    )
    grid_canvas.grid(row=5, column=0, sticky="nsew")

    buttons = ttk.Frame(right, style="Panel.TFrame")
    buttons.grid(row=6, column=0, sticky="e", pady=(8, 0))

    state: dict[str, Any] = {
        "running": True,
        "after_id": None,
        "last_payload": [],
        "by_symbol": {},
    }

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
            grid_canvas.delete("all")
            return
        if snap.get("error"):
            reasons.insert(tk.END, f"Error: {snap['error']}")
            grid_canvas.delete("all")
            return
        sig_data = snap.get("signal", {})
        lines = [
            f"Signal: {sig_data.get('signal', 'HOLD')}",
            f"Confidence: {sig_data.get('confidence', 0.0)}%",
            f"Score: {sig_data.get('score', 0)}",
            f"Regime: {sig_data.get('regime', 'N/A')}",
            f"Autotrade: {_fmt_autotrade(snap.get('autotrade', {}))}",
            "",
            "Reasons:",
        ]
        for idx, reason in enumerate(sig_data.get("reasons", []), start=1):
            lines.append(f"{idx}. {reason}")
        reasons.insert(tk.END, "\n".join(lines))

        # Feature 4: update grid visualiser for selected symbol
        grid_levels = snap.get("grid_levels", [])
        sig = str(sig_data.get("signal", "HOLD")).upper()
        conf = float(sig_data.get("confidence", 0.0))
        _draw_grid(grid_canvas, grid_levels, sig, conf)

    def _on_table_select(_: Any) -> None:
        selection = table.selection()
        if not selection:
            return
        symbol = table.item(selection[0], "values")[0]
        selected_var.set(symbol)
        _update_reasons(symbol)

    table.bind("<<TreeviewSelect>>", _on_table_select)

    def _render_payload(payload: Any) -> None:
        snapshots = _normalize(payload)
        state["last_payload"] = snapshots
        state["by_symbol"] = {str(s.get("symbol", "?")): s for s in snapshots}

        for item in table.get_children():
            table.delete(item)

        buy_count = 0
        sell_count = 0
        hold_count = 0

        for snap in snapshots:
            symbol = str(snap.get("symbol", "?"))
            if snap.get("error"):
                table.insert("", tk.END, values=(symbol, "-", "ERR", "-", "-", "-", snap.get("error")), tags=("ERROR",))
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

        count_var.set(str(len(snapshots)))
        buy_var.set(str(buy_count))
        sell_var.set(str(sell_count))
        hold_var.set(str(hold_count))

        selected = selected_var.get()
        if selected in state["by_symbol"]:
            _update_reasons(selected)
        elif snapshots:
            first_symbol = str(snapshots[0].get("symbol", "-"))
            selected_var.set(first_symbol)
            _update_reasons(first_symbol)

    def _refresh_once() -> None:
        try:
            payload = get_payload()
            _render_payload(payload)
            next_interval = _current_interval()
            status_var.set(f"Live updates every {next_interval:.1f}s. Last refresh successful.")
        except Exception as exc:
            status_var.set(f"Update error: {exc}")

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
        status_var.set("Resumed live updates")
        _refresh_loop()

    def _stop() -> None:
        state["running"] = False
        running_var.set("PAUSED")
        status_var.set("Paused")
        if state["after_id"] is not None:
            root.after_cancel(state["after_id"])
            state["after_id"] = None

    ttk.Button(buttons, text="Start", command=_start, style="Deck.TButton").pack(side=tk.LEFT, padx=(0, 6))
    ttk.Button(buttons, text="Pause", command=_stop, style="Deck.TButton").pack(side=tk.LEFT, padx=(0, 6))
    ttk.Button(buttons, text="Refresh Now", command=_refresh_once, style="Deck.TButton").pack(side=tk.LEFT)

    _refresh_loop()
    root.mainloop()
