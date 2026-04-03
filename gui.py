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

import tkinter as tk
from tkinter import ttk
from typing import Any, cast


_SIGNAL_COLOR = {"BUY": "\033[92m", "SELL": "\033[91m", "HOLD": "\033[93m", "NONE": "\033[91m"}
_RESET = "\033[0m"


def _send_alert(message: str) -> None:
    print(message)


def _as_snapshots(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        snapshots: list[dict[str, Any]] = []
        for item in payload:
            if isinstance(item, dict):
                snapshots.append(cast(dict[str, Any], item))
        return snapshots
    if isinstance(payload, dict):
        return [cast(dict[str, Any], payload)]
    return []


def _fmt_autotrade(at: Any) -> str:
    if not isinstance(at, dict):
        return str(at)

    at_dict = cast(dict[str, Any], at)
    status = str(at_dict.get("status", "?")).lower()
    extra = ""
    if status == "cooldown":
        extra = f" ({at_dict.get('seconds_left', '?')}s left)"
    elif status in {"placed", "dry_run"}:
        req_raw = at_dict.get("request", {})
        req = cast(dict[str, Any], req_raw) if isinstance(req_raw, dict) else {}
        side = req.get("side", at_dict.get("side", "?"))
        volume = req.get("volume", at_dict.get("lot", "?"))
        price = req.get("price", at_dict.get("price", "?"))
        extra = f" {side} {volume}lot @ {price}"
    elif status == "risk_blocked":
        extra = f" ({at_dict.get('reason', 'blocked')})"
    elif status == "auto_trading_off":
        extra = " (toggle OFF)"
    return status + extra


def render_console(payload: Any) -> None:
    snapshots = _as_snapshots(payload)

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
        raw_sig = sig_data.get("signal", "HOLD")
        sig = "NONE" if raw_sig is None else str(raw_sig).upper()
        conf = float(sig_data.get("confidence", 0.0))
        score = int(sig_data.get("score", 0))
        at_str = _fmt_autotrade(snap.get("autotrade", {}))
        err = snap.get("error")
        color = _SIGNAL_COLOR.get(sig, "")

        if err:
            print(f"{sym:<{col_sym}} | ERROR: {err}")
            continue

        close_str = f"{close:.2f}" if close > 100 else f"{close:.5f}"
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
    green = "#00c853"
    red = "#ff5252"
    yellow = "#ffd54f"
    dim = "#aaaaaa"

    runtime = getattr(get_payload, "__self__", None)

    root = tk.Tk()
    root.title("Alpha AI Live")
    root.geometry("1120x720")
    root.configure(bg=bg)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Dark.TFrame", background=bg)
    style.configure("Dark.TLabel", background=bg, foreground=fg)
    style.configure("Dark.TButton", background=panel, foreground=fg, borderwidth=1)
    style.map("Dark.TButton", background=[("active", "#222222"), ("pressed", "#2a2a2a")])
    style.configure("Dark.TEntry", fieldbackground=panel, foreground=fg)

    frame = ttk.Frame(root, padding=12, style="Dark.TFrame")
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Alpha AI Live Snapshot", style="Dark.TLabel").pack(anchor=tk.W, pady=(0, 8))

    status_var = tk.StringVar(value="Starting...")
    status_label = tk.Label(frame, textvariable=status_var, bg=bg, fg=fg, anchor="w")
    status_label.pack(fill=tk.X, pady=(0, 8))

    controls = ttk.Frame(frame, style="Dark.TFrame")
    controls.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(controls, text="Interval (s):", style="Dark.TLabel").pack(side=tk.LEFT)
    interval_var = tk.StringVar(value=f"{interval_seconds:.1f}")
    ttk.Entry(controls, textvariable=interval_var, width=8, style="Dark.TEntry").pack(side=tk.LEFT, padx=(6, 10))

    running_var = tk.StringVar(value="RUNNING")
    ttk.Label(controls, textvariable=running_var, style="Dark.TLabel").pack(side=tk.LEFT, padx=(0, 12))

    auto_var = tk.StringVar(value="Auto Trading: OFF")
    auto_button = ttk.Button(controls, textvariable=auto_var, style="Dark.TButton")
    auto_button.pack(side=tk.LEFT, padx=(0, 12))

    state: dict[str, Any] = {
        "running": True,
        "after_id": None,
        "warning_sent": False,
        "blocked_sent": False,
    }

    risk_frame = tk.Frame(frame, bg=panel, padx=10, pady=10)
    risk_frame.pack(fill=tk.X, pady=(0, 10))

    ftmo_title = tk.Label(risk_frame, text="FTMO Panel", bg=panel, fg=fg, anchor="w", font=("Segoe UI", 11, "bold"))
    ftmo_title.grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 8))

    risk_labels: dict[str, tk.Label] = {}
    headers = [
        ("daily_loss", "Daily P/L"),
        ("daily_limit", "Daily loss limit"),
        ("drawdown", "Drawdown"),
        ("trades_today", "Trades today"),
        ("status", "Status"),
    ]
    for idx, (key, title) in enumerate(headers):
        tk.Label(risk_frame, text=title, bg=panel, fg=dim, anchor="w").grid(row=1, column=idx, sticky="w", padx=(0, 20))
        label = tk.Label(risk_frame, text="-", bg=panel, fg=fg, anchor="w", font=("Segoe UI", 11, "bold"))
        label.grid(row=2, column=idx, sticky="w", padx=(0, 20))
        risk_labels[key] = label

    reason_var = tk.StringVar(value="Status: waiting for data")
    reason_label = tk.Label(frame, textvariable=reason_var, bg=bg, fg=dim, anchor="w")
    reason_label.pack(fill=tk.X, pady=(0, 8))

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
    text.tag_configure("BUY", foreground=green)
    text.tag_configure("SELL", foreground=red)
    text.tag_configure("HOLD", foreground=yellow)
    text.tag_configure("NONE", foreground=red)
    text.tag_configure("header", foreground=dim)
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

    def _set_auto_button_state(enabled: bool, can_toggle: bool) -> None:
        auto_var.set(f"Auto Trading: {'ON' if enabled else 'OFF'}")
        auto_button.state(["!disabled"] if can_toggle else ["disabled"])

    def _render_payload(payload: Any) -> None:
        snapshots = _as_snapshots(payload)
        text.delete("1.0", tk.END)
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
            raw_sig = sig_data.get("signal", "HOLD")
            sig = "NONE" if raw_sig is None else str(raw_sig).upper()
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

    def _update_risk_panel(payload: Any) -> None:
        snapshots = _as_snapshots(payload)
        first = snapshots[0] if snapshots else {}
        risk_raw = first.get("risk_status", {})
        risk_status = cast(dict[str, Any], risk_raw) if isinstance(risk_raw, dict) else {}
        auto_enabled = bool(first.get("auto_trading_enabled", False))

        daily_loss = float(risk_status.get("daily_loss", 0.0))
        daily_limit = float(risk_status.get("daily_limit", -1.0))
        drawdown = float(risk_status.get("drawdown", 0.0))
        trades_today = int(risk_status.get("trades_today", 0))
        blocked = bool(risk_status.get("blocked", False))
        can_trade = bool(risk_status.get("can_trade", True))
        reason = str(risk_status.get("reason", "OK"))

        daily_used = abs(daily_loss / daily_limit) if daily_limit else 0.0
        if blocked or not can_trade:
            color = red
            status_text = "BLOCKED"
        elif daily_used > 0.7:
            color = yellow
            status_text = "WARNING"
        else:
            color = green
            status_text = "ACTIVE"

        risk_labels["daily_loss"].config(text=f"{daily_loss:+.2f}", fg=color)
        risk_labels["daily_limit"].config(text=f"{daily_limit:.2f}", fg=color)
        risk_labels["drawdown"].config(text=f"{drawdown:+.2f}", fg=color)
        risk_labels["trades_today"].config(text=str(trades_today), fg=color)
        risk_labels["status"].config(text=status_text, fg=color)

        if (blocked or not can_trade) and runtime is not None and getattr(runtime, "auto_trading_enabled", False):
            toggle_result = runtime.set_auto_trading(False)
            auto_enabled = bool(getattr(runtime, "auto_trading_enabled", False))
            if not toggle_result[0]:
                reason = toggle_result[1]

        _set_auto_button_state(auto_enabled, can_trade and not blocked)

        if blocked or not can_trade:
            status_var.set(f"🚫 BLOCKED: {reason}")
            status_label.config(fg=red)
            reason_label.config(text=f"Reason: {reason}", fg=red)
        else:
            reason_label.config(text=f"Reason: {reason}", fg=color)

        if daily_used > 0.8 and not state["warning_sent"]:
            _send_alert("⚠️ WARNING: 80% daily loss reached")
            state["warning_sent"] = True
        elif daily_used <= 0.8:
            state["warning_sent"] = False

        if blocked and not state["blocked_sent"]:
            _send_alert("🚫 FTMO BLOCKED")
            state["blocked_sent"] = True
        elif not blocked:
            state["blocked_sent"] = False

    def _refresh_once() -> None:
        try:
            payload = get_payload()
            _render_payload(payload)
            _update_risk_panel(payload)
            next_interval = _current_interval()
            if not str(status_var.get()).startswith("🚫 BLOCKED"):
                status_var.set(f"Updated every {next_interval:.1f}s")
                status_label.config(fg=fg)
        except Exception as exc:
            status_var.set(f"Update error: {exc}")
            status_label.config(fg=red)

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
        status_label.config(fg=fg)
        _refresh()

    def _stop() -> None:
        state["running"] = False
        running_var.set("PAUSED")
        status_var.set("Paused")
        status_label.config(fg=yellow)
        if state["after_id"] is not None:
            root.after_cancel(state["after_id"])
            state["after_id"] = None

    def _refresh_now() -> None:
        _refresh_once()

    def _toggle_auto_trading() -> None:
        if runtime is None or not hasattr(runtime, "set_auto_trading"):
            status_var.set("Auto trading toggle unavailable")
            status_label.config(fg=yellow)
            return

        target = not bool(getattr(runtime, "auto_trading_enabled", False))
        ok, reason = runtime.set_auto_trading(target)
        enabled = bool(getattr(runtime, "auto_trading_enabled", False))
        _set_auto_button_state(enabled, True)
        if ok:
            status_var.set(f"Auto trading {'enabled' if enabled else 'disabled'}")
            status_label.config(fg=green if enabled else yellow)
        else:
            status_var.set(f"🚫 BLOCKED: {reason}")
            status_label.config(fg=red)
        reason_label.config(text=f"Reason: {reason}", fg=status_label.cget("fg"))

    auto_button.configure(command=_toggle_auto_trading)

    ttk.Button(controls, text="Start", command=_start, style="Dark.TButton").pack(side=tk.LEFT, padx=(0, 6))
    ttk.Button(controls, text="Stop", command=_stop, style="Dark.TButton").pack(side=tk.LEFT)
    ttk.Button(controls, text="Refresh Now", command=_refresh_now, style="Dark.TButton").pack(side=tk.LEFT, padx=(6, 0))

    _set_auto_button_state(bool(getattr(runtime, "auto_trading_enabled", False)), True)
    _refresh()
    root.mainloop()
