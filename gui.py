from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk
from typing import Any


def render_console(payload: dict[str, Any]) -> None:
    print("=== Alpha AI Live Snapshot ===")
    print(json.dumps(payload, indent=2))


def run_live_gui(get_payload: Any, interval_seconds: float = 2.0) -> None:
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
