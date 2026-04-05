from __future__ import annotations

import threading
from typing import Any


class TradingController:
    """Thread-safe start / stop / pause controller for the trading loop.

    Usage
    -----
    controller = TradingController()
    controller.start()          # mark as running

    # in the trading loop:
    while controller.should_continue():
        stopped = controller.wait_if_paused()   # blocks while paused
        if stopped:
            break
        do_work()

    # from another thread or the dashboard API:
    controller.pause()
    controller.resume()
    controller.stop()
    """

    def __init__(self) -> None:
        self._stop_event = threading.Event()
        # _pause_event is set (=not paused) when running normally.
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._lock = threading.Lock()
        self._running = False

    # ── Control ───────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Mark the loop as started (clear stop; unpause)."""
        with self._lock:
            self._stop_event.clear()
            self._pause_event.set()
            self._running = True

    def stop(self) -> None:
        """Signal the loop to exit at the next check."""
        with self._lock:
            self._stop_event.set()
            self._pause_event.set()  # unblock wait_if_paused so loop can exit
            self._running = False

    def pause(self) -> None:
        """Suspend the loop after its current iteration completes."""
        self._pause_event.clear()

    def resume(self) -> None:
        """Resume a paused loop."""
        self._pause_event.set()

    # ── Loop helpers ──────────────────────────────────────────────────────────

    def should_continue(self) -> bool:
        """Return True when the loop should keep running (not stopped)."""
        return not self._stop_event.is_set()

    def wait_if_paused(self, poll_interval: float = 0.5) -> bool:
        """Block while paused; returns True if stop was requested during wait.

        The loop should call ``if controller.wait_if_paused(): break``.
        """
        while not self._pause_event.wait(timeout=poll_interval):
            if self._stop_event.is_set():
                return True
        return self._stop_event.is_set()

    # ── State queries ─────────────────────────────────────────────────────────

    def is_stopped(self) -> bool:
        return self._stop_event.is_set()

    def is_paused(self) -> bool:
        return not self._pause_event.is_set()

    def is_running(self) -> bool:
        return self._running and not self._stop_event.is_set()

    def status(self) -> dict[str, Any]:
        return {
            "running": self.is_running(),
            "stopped": self.is_stopped(),
            "paused": self.is_paused(),
        }
