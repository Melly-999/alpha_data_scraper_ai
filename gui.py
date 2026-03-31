# Copyright 2025-2026 Mati (Melly-999)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk
from typing import Any


_SIGNAL_COLOR = {"BUY": "\033[92m", "SELL": "\033[91m", "HOLD": "\033[93m"}
_RESET = "\033[0m"


def _fmt_autotrade(at: Any) -> str:
    if not isinstance(at, dict):
        return str(at)
    status = at.get("status", "?")
    extra = ""
    if status == "cooldown":
        extra = f" ({at.get('seconds_left', '?')}s left)"
    elif status in ("placed", "dry_run"):
        req = at.get("request", {})
        extra = f" {req.get('side','?')} {req.get('volume','?')}lot @ {req.get('price','?')}"
    return status + extra


def render_console(payload: Any) -> None:
    """Render snapshot(s) to console.

    Accepts either a list of symbol dicts (multi-symbol) or a single dict
    (backward compat).
    """
    snapshots: list[dict[str, Any]] = payload if isinstance(payload, list) else [payload]

    col_sym = 8
    col_close = 10
    col_sig = 6
    col_conf = 7
    col_score = 6
    col_dt = 22

    header = (
        f"{'SYMBOL':<{col_sym}} | "
        f"{'CLOSE':>{col_close}} | "
        f"{'SIGNAL':<{col_sig}} | "
        f"{'CONF%':>{col_conf}} | "
        f"{'SCORE':>{col_score}} | "
        f"AUTOTRADE"
    )
    sep = "-" * len(header)
    count = len(snapshots)
    print(f"=== Alpha AI Live Snapshot ({count} instrument{'s' if count != 1 else ''}) ===")
    print(header)
    print(sep)

    for snap in snapshots:
        sym = str(snap.get("symbol", "?"))
        close = snap.get("last_close", 0.0)
        sig_data = snap.get("signal", {})
        sig = str(sig_data.get("signal", "HOLD")).upper()
        conf = float(sig_data.get("confidence", 0.0))
        score = int(sig_data.get("score", 0))
        at_str = _fmt_autotrade(snap.get("autotrade", {}))
        err = snap.get("error")

        color = _SIGNAL_COLOR.get(sig, "")

        if err:
            print(f"{sym:<{col_sym}} | ERROR: {err}")
            continue

        # Format close price: more decimals for FX, fewer for gold/JPY
        close_str = (
            f"{close:.2f}" if close > 100 else f"{close:.5f}"
        )

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
    bg = "#000000"
    fg = "#ffffff"
    panel = "#111111"
    green = "#00ff88"
    red = "#ff4444"
    yellow = "#ffcc00"

    root = tk.Tk()
    root.title("Alpha AI Live")
    root.geometry("960x580")
    root.configure(bg=bg)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Dark.TFrame", background=bg)
    style.configure("Dark.TLabel", background=bg, foreground=fg)
    style.configure(
        "Dark.TButton",
        background=panel,
        foreground=fg,
        borderwidth=1,
    )
    style.map(
        "Dark.TButton",
        background=[("active", "#222222"), ("pressed", "#2a2a2a")],
    )
    style.configure("Dark.TEntry", fieldbackground=panel, foreground=fg)

    frame = ttk.Frame(root, padding=12, style="Dark.TFrame")
    frame.pack(fill=tk.BOTH, expand=True)

    title = ttk.Label(frame, text="Alpha AI Live Snapshot", style="Dark.TLabel")
    title.pack(anchor=tk.W, pady=(0, 8))

    status_var = tk.StringVar(value="Starting...")
    status = ttk.Label(frame, textvariable=status_var, style="Dark.TLabel")
    status.pack(anchor=tk.W, pady=(0, 8))

    controls = ttk.Frame(frame, style="Dark.TFrame")
    controls.pack(fill=tk.X, pady=(0, 8))

    ttk.Label(controls, text="Interval (s):", style="Dark.TLabel").pack(side=tk.LEFT)
    interval_var = tk.StringVar(value=f"{interval_seconds:.1f}")
    interval_entry = ttk.Entry(
        controls, textvariable=interval_var, width=8, style="Dark.TEntry"
    )
    interval_entry.pack(side=tk.LEFT, padx=(6, 10))

    running_var = tk.StringVar(value="RUNNING")
    running_label = ttk.Label(controls, textvariable=running_var, style="Dark.TLabel")
    running_label.pack(side=tk.LEFT, padx=(0, 12))

    state: dict[str, Any] = {"running": True, "after_id": None}

    text = tk.Text(
        frame,
        wrap=tk.NONE,
        bg=bg,
        fg=fg,
        insertbackground=fg,
        selectbackground="#333333",
        selectforeground=fg,
        highlightthickness=0,
        relief=tk.FLAT,
        font=("Courier New", 10),
    )
    text.pack(fill=tk.BOTH, expand=True)

    # Configure signal tags
    text.tag_configure("BUY", foreground=green)
    text.tag_configure("SELL", foreground=red)
    text.tag_configure("HOLD", foreground=yellow)
    text.tag_configure("header", foreground="#aaaaaa")
    text.tag_configure("error", foreground=red)

    text_any: Any = text

    yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_any.yview)
    text.configure(yscrollcommand=yscroll.set)
    yscroll.pack(side=tk.RIGHT, fill=tk.Y)

    xscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text_any.xview)
    text.configure(xscrollcommand=xscroll.set)
    xscroll.pack(side=tk.BOTTOM, fill=tk.X)

    def _current_interval() -> float:
        try:
            value = float(interval_var.get())
            if value <= 0:
                raise ValueError
            return value
        except Exception:
            return max(interval_seconds, 0.1)

    def _render_payload(payload: Any) -> None:
        text.delete("1.0", tk.END)
        snapshots: list[dict[str, Any]] = payload if isinstance(payload, list) else [payload]
        count = len(snapshots)

        hdr = (
            f"{'SYMBOL':<8} | {'CLOSE':>10} | {'SIGNAL':<6} | "
            f"{'CONF%':>7} | {'SCORE':>6} | {'LSTM Δ':>10} | AUTOTRADE\n"
        )
        sep = "-" * len(hdr.rstrip()) + "\n"

        text.insert(tk.END, f"=== Alpha AI Live ({count} instruments) ===\n", "header")
        text.insert(tk.END, hdr, "header")
        text.insert(tk.END, sep, "header")

        for snap in snapshots:
            sym = str(snap.get("symbol", "?"))
            close = snap.get("last_close", 0.0)
            lstm_d = float(snap.get("lstm_delta", 0.0))
            sig_data = snap.get("signal", {})
            sig = str(sig_data.get("signal", "HOLD")).upper()
            conf = float(sig_data.get("confidence", 0.0))
            score = int(sig_data.get("score", 0))
            at_str = _fmt_autotrade(snap.get("autotrade", {}))
            err = snap.get("error")

            if err:
                text.insert(tk.END, f"{sym:<8} | ERROR: {err}\n", "error")
                continue

            close_str = f"{close:.2f}" if close > 100 else f"{close:.5f}"
            delta_str = f"{lstm_d:+.5f}" if abs(lstm_d) < 100 else f"{lstm_d:+.3f}"

            line_prefix = f"{sym:<8} | {close_str:>10} | "
            line_suffix = f" | {conf:>7.1f} | {score:>6} | {delta_str:>10} | {at_str}\n"
            text.insert(tk.END, line_prefix)
            text.insert(tk.END, f"{sig:<6}", sig)
            text.insert(tk.END, line_suffix)

        text.insert(tk.END, "\n")
        for snap in snapshots:
            sig_data = snap.get("signal", {})
            reasons = sig_data.get("reasons", [])
            sym = snap.get("symbol", "?")
            if reasons:
                text.insert(tk.END, f"  {sym}: {', '.join(reasons)}\n", "header")

    def _refresh_once() -> None:
        try:
            payload = get_payload()
            _render_payload(payload)
            next_interval = _current_interval()
            status_var.set(f"Updated every {next_interval:.1f}s")
        except Exception as exc:
            status_var.set(f"Update error: {exc}")

    def _refresh() -> None:
        if not state["running"]:
            return
        _refresh_once()
        next_interval = _current_interval()
        state["after_id"] = root.after(int(next_interval * 1000), _refresh)

    def _start() -> None:
        if state["running"]:
            return
        state["running"] = True
        running_var.set("RUNNING")
        status_var.set("Resumed live updates")
        _refresh()

    def _stop() -> None:
        state["running"] = False
        running_var.set("PAUSED")
        status_var.set("Paused")
        if state["after_id"] is not None:
            root.after_cancel(state["after_id"])
            state["after_id"] = None

    def _refresh_now() -> None:
        _refresh_once()

    ttk.Button(controls, text="Start", command=_start, style="Dark.TButton").pack(
        side=tk.LEFT, padx=(0, 6)
    )
    ttk.Button(controls, text="Stop", command=_stop, style="Dark.TButton").pack(
        side=tk.LEFT
    )
    ttk.Button(
        controls,
        text="Refresh Now",
        command=_refresh_now,
        style="Dark.TButton",
    ).pack(side=tk.LEFT, padx=(6, 0))

    _refresh()
    root.mainloop()

    bg = "#000000"
    fg = "#ffffff"
    panel = "#111111"

    root = tk.Tk()
    root.title("Alpha AI Live")
    root.geometry("780x520")
    root.configure(bg=bg)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Dark.TFrame", background=bg)
    style.configure("Dark.TLabel", background=bg, foreground=fg)
    style.configure(
        "Dark.TButton",
        background=panel,
        foreground=fg,
        borderwidth=1,
    )
    style.map(
        "Dark.TButton",
        background=[("active", "#222222"), ("pressed", "#2a2a2a")],
    )
    style.configure("Dark.TEntry", fieldbackground=panel, foreground=fg)

    frame = ttk.Frame(root, padding=12, style="Dark.TFrame")
    frame.pack(fill=tk.BOTH, expand=True)

    title = ttk.Label(frame, text="Alpha AI Live Snapshot", style="Dark.TLabel")
    title.pack(anchor=tk.W, pady=(0, 8))

    status_var = tk.StringVar(value="Starting...")
    status = ttk.Label(frame, textvariable=status_var, style="Dark.TLabel")
    status.pack(anchor=tk.W, pady=(0, 8))

    controls = ttk.Frame(frame, style="Dark.TFrame")
    controls.pack(fill=tk.X, pady=(0, 8))

    ttk.Label(controls, text="Interval (s):", style="Dark.TLabel").pack(side=tk.LEFT)
    interval_var = tk.StringVar(value=f"{interval_seconds:.1f}")
    interval_entry = ttk.Entry(
        controls, textvariable=interval_var, width=8, style="Dark.TEntry"
    )
    interval_entry.pack(side=tk.LEFT, padx=(6, 10))

    running_var = tk.StringVar(value="RUNNING")
    running_label = ttk.Label(controls, textvariable=running_var, style="Dark.TLabel")
    running_label.pack(side=tk.LEFT, padx=(0, 12))

    state: dict[str, Any] = {"running": True, "after_id": None}

    text = tk.Text(
        frame,
        wrap=tk.NONE,
        bg=bg,
        fg=fg,
        insertbackground=fg,
        selectbackground="#333333",
        selectforeground=fg,
        highlightthickness=0,
        relief=tk.FLAT,
    )
    text.pack(fill=tk.BOTH, expand=True)

    text_any: Any = text

    def _on_y_scroll(*args: Any) -> None:
        text_any.yview(*args)

    yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=_on_y_scroll)
    text.configure(yscrollcommand=yscroll.set)
    yscroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_x_scroll(*args: Any) -> None:
        text_any.xview(*args)

    xscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=_on_x_scroll)
    text.configure(xscrollcommand=xscroll.set)
    xscroll.pack(side=tk.BOTTOM, fill=tk.X)

    def _current_interval() -> float:
        try:
            value = float(interval_var.get())
            if value <= 0:
                raise ValueError
            return value
        except Exception:
            return max(interval_seconds, 0.1)

    def _refresh_once() -> None:
        try:
            payload = get_payload()
            text.delete("1.0", tk.END)
            text.insert(tk.END, json.dumps(payload, indent=2))
            next_interval = _current_interval()
            status_var.set(f"Updated every {next_interval:.1f}s")
        except Exception as exc:
            status_var.set(f"Update error: {exc}")

    def _refresh() -> None:
        if not state["running"]:
            return
        _refresh_once()
        next_interval = _current_interval()
        state["after_id"] = root.after(int(next_interval * 1000), _refresh)

    def _start() -> None:
        if state["running"]:
            return
        state["running"] = True
        running_var.set("RUNNING")
        status_var.set("Resumed live updates")
        _refresh()

    def _stop() -> None:
        state["running"] = False
        running_var.set("PAUSED")
        status_var.set("Paused")
        if state["after_id"] is not None:
            root.after_cancel(state["after_id"])
            state["after_id"] = None

    def _refresh_now() -> None:
        _refresh_once()

    ttk.Button(controls, text="Start", command=_start, style="Dark.TButton").pack(
        side=tk.LEFT, padx=(0, 6)
    )
    ttk.Button(controls, text="Stop", command=_stop, style="Dark.TButton").pack(
        side=tk.LEFT
    )
    ttk.Button(
        controls,
        text="Refresh Now",
        command=_refresh_now,
        style="Dark.TButton",
    ).pack(side=tk.LEFT, padx=(6, 0))

    _refresh()
    root.mainloop()
