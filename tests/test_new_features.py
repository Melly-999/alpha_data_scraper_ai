"""Tests for: TradingController, dashboard state, compute_grid_levels, AlertManager."""
from __future__ import annotations

import threading
import time
from typing import Any

import pandas as pd


# ── TradingController ─────────────────────────────────────────────────────────

class TestTradingController:
    def _make(self):
        from trading_controller import TradingController
        return TradingController()

    def test_initial_state(self):
        c = self._make()
        assert not c.is_running()
        assert not c.is_paused()
        assert not c.is_stopped()

    def test_start_sets_running(self):
        c = self._make()
        c.start()
        assert c.is_running()
        assert not c.is_paused()
        assert not c.is_stopped()

    def test_stop_clears_running(self):
        c = self._make()
        c.start()
        c.stop()
        assert not c.is_running()
        assert c.is_stopped()

    def test_pause_resume(self):
        c = self._make()
        c.start()
        c.pause()
        assert c.is_paused()
        assert c.is_running()   # still logically running, just paused
        c.resume()
        assert not c.is_paused()

    def test_should_continue_after_start(self):
        c = self._make()
        c.start()
        assert c.should_continue()

    def test_should_continue_false_after_stop(self):
        c = self._make()
        c.start()
        c.stop()
        assert not c.should_continue()

    def test_status_dict_keys(self):
        c = self._make()
        c.start()
        s = c.status()
        assert {"running", "stopped", "paused"} == set(s.keys())
        assert s["running"] is True
        assert s["stopped"] is False
        assert s["paused"] is False

    def test_wait_if_paused_returns_false_when_running(self):
        c = self._make()
        c.start()
        # Not paused → should return quickly (within timeout) with False
        stopped = c.wait_if_paused(poll_interval=0.05)
        assert stopped is False

    def test_wait_if_paused_unblocks_on_stop(self):
        """A paused loop should unblock when stop() is called."""
        c = self._make()
        c.start()
        c.pause()
        results: list[bool] = []

        def _waiter():
            results.append(c.wait_if_paused(poll_interval=0.05))

        t = threading.Thread(target=_waiter)
        t.start()
        time.sleep(0.15)
        c.stop()
        t.join(timeout=2)
        assert results == [True]

    def test_thread_safety_concurrent_start_stop(self):
        c = self._make()
        errors: list[Exception] = []

        def toggle():
            try:
                for _ in range(20):
                    c.start()
                    c.stop()
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=toggle) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []


# ── Dashboard state ───────────────────────────────────────────────────────────

class TestDashboardState:
    def test_push_state_updates_snapshots(self):
        from dashboard import push_state, _shared_state
        push_state([{"symbol": "EURUSD", "signal": {"signal": "BUY"}}])
        assert _shared_state["snapshots"][0]["symbol"] == "EURUSD"

    def test_push_state_updates_timestamp(self):
        from dashboard import push_state, _shared_state
        before = _shared_state["last_update"]
        time.sleep(0.01)
        push_state([{"symbol": "TEST"}])
        assert _shared_state["last_update"] > before

    def test_push_alerts_appends(self):
        from dashboard import push_alerts, _shared_state
        _shared_state["alerts"] = []
        push_alerts([{"symbol": "GBPUSD", "to_signal": "BUY", "ts": time.time()}])
        assert any(a["symbol"] == "GBPUSD" for a in _shared_state["alerts"])

    def test_push_state_thread_safe(self):
        from dashboard import push_state
        errors: list[Exception] = []

        def pusher(n: int) -> None:
            try:
                push_state([{"symbol": f"SYM{n}"}])
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=pusher, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []


# ── compute_grid_levels ───────────────────────────────────────────────────────

class TestComputeGridLevels:
    """Tests for main.compute_grid_levels — import via importlib to avoid tkinter."""

    @staticmethod
    def _import():
        import sys
        # Temporarily stub gui so main.py can import without tkinter
        if "gui" not in sys.modules:
            import types
            stub = types.ModuleType("gui")
            stub.render_console = lambda *a, **k: None  # type: ignore
            stub.run_live_gui = lambda *a, **k: None    # type: ignore
            sys.modules["gui"] = stub
        import main as m
        return m.compute_grid_levels

    def test_contains_current_level(self):
        fn = self._import()
        row = pd.Series({"close": 1.0823, "atr": 0.0005})
        levels = fn(row)
        types = [lv["type"] for lv in levels]
        assert "current" in types

    def test_contains_support_and_resistance(self):
        fn = self._import()
        row = pd.Series({"close": 1.0823, "atr": 0.0005})
        levels = fn(row)
        types = [lv["type"] for lv in levels]
        assert "support" in types
        assert "resistance" in types

    def test_sorted_descending(self):
        fn = self._import()
        row = pd.Series({"close": 1.0823, "atr": 0.0005})
        levels = fn(row)
        prices = [lv["price"] for lv in levels]
        assert prices == sorted(prices, reverse=True)

    def test_vwap_included_when_positive(self):
        fn = self._import()
        row = pd.Series({"close": 1.0823, "atr": 0.0005, "vwap": 1.0800})
        levels = fn(row)
        types = [lv["type"] for lv in levels]
        assert "vwap" in types

    def test_bb_levels_included(self):
        fn = self._import()
        row = pd.Series({
            "close": 1.0823, "atr": 0.0005,
            "bb_upper": 1.0870, "bb_lower": 1.0780,
        })
        levels = fn(row)
        types = [lv["type"] for lv in levels]
        assert types.count("resistance") >= 1
        assert types.count("support") >= 1

    def test_atr_fallback_when_zero(self):
        fn = self._import()
        row = pd.Series({"close": 1.0823, "atr": 0.0})  # ATR = 0 → 0.1% fallback
        levels = fn(row)
        assert len(levels) >= 1  # should not crash

    def test_n_levels_parameter(self):
        fn = self._import()
        row = pd.Series({"close": 1.0823, "atr": 0.0005})
        levels2 = fn(row, n_levels=2)
        levels5 = fn(row, n_levels=5)
        assert len(levels5) > len(levels2)


# ── AlertManager ──────────────────────────────────────────────────────────────

class TestAlertManager:
    @staticmethod
    def _import():
        import sys
        import types
        if "gui" not in sys.modules:
            stub = types.ModuleType("gui")
            stub.render_console = lambda *a, **k: None  # type: ignore
            stub.run_live_gui = lambda *a, **k: None    # type: ignore
            sys.modules["gui"] = stub
        import main as m
        return m.AlertManager

    def _snap(self, sym: str, sig: str, conf: float = 65.0) -> dict[str, Any]:
        return {"symbol": sym, "signal": {"signal": sig, "confidence": conf}}

    def test_no_alert_on_first_cycle(self):
        AM = self._import()
        am = AM()
        alerts = am.check([self._snap("EURUSD", "BUY")])
        assert alerts == []

    def test_alert_on_signal_change(self):
        AM = self._import()
        am = AM()
        am.check([self._snap("EURUSD", "BUY")])
        alerts = am.check([self._snap("EURUSD", "SELL")])
        assert len(alerts) == 1
        assert alerts[0]["symbol"] == "EURUSD"
        assert alerts[0]["from_signal"] == "BUY"
        assert alerts[0]["to_signal"] == "SELL"

    def test_no_alert_when_signal_unchanged(self):
        AM = self._import()
        am = AM()
        am.check([self._snap("EURUSD", "BUY")])
        alerts = am.check([self._snap("EURUSD", "BUY")])
        assert alerts == []

    def test_multiple_symbols_independent(self):
        AM = self._import()
        am = AM()
        am.check([self._snap("EURUSD", "BUY"), self._snap("GBPUSD", "SELL")])
        alerts = am.check([self._snap("EURUSD", "BUY"), self._snap("GBPUSD", "BUY")])
        assert len(alerts) == 1
        assert alerts[0]["symbol"] == "GBPUSD"

    def test_callback_fired(self):
        AM = self._import()
        am = AM()
        received: list[Any] = []
        am.on_alert(received.extend)
        am.check([self._snap("EURUSD", "HOLD")])
        am.check([self._snap("EURUSD", "BUY")])
        assert len(received) == 1

    def test_recent_returns_last_n(self):
        AM = self._import()
        am = AM()
        am.check([self._snap("EURUSD", "BUY")])
        for sig in ("SELL", "BUY", "SELL", "HOLD"):
            am.check([self._snap("EURUSD", sig)])
        recent = am.recent(2)
        assert len(recent) <= 2


# ── Quick backtest ────────────────────────────────────────────────────────────

class TestQuickBacktest:
    def test_returns_dict_with_expected_keys(self):
        from dashboard import _run_quick_backtest
        result = _run_quick_backtest("EURUSD", bars=120, initial_balance=1000.0)
        assert "symbol" in result
        # Either has trade stats or an error/no-trades message
        assert "total_trades" in result or "error" in result or "message" in result

    def test_win_rate_bounded(self):
        from dashboard import _run_quick_backtest
        result = _run_quick_backtest("EURUSD", bars=200, initial_balance=1000.0)
        if "win_rate" in result:
            assert 0.0 <= result["win_rate"] <= 100.0

    def test_symbol_reflected_in_result(self):
        from dashboard import _run_quick_backtest
        result = _run_quick_backtest("GBPUSD", bars=100, initial_balance=500.0)
        assert result.get("symbol") == "GBPUSD"
