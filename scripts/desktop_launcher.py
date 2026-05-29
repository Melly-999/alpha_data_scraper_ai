"""
MellyTrade Desktop Launcher — scripts/desktop_launcher.py

Starts the local MellyTrade backend and frontend helper scripts, waits for
readiness, then opens the browser to /terminal.

Safety posture (enforced at launch, never weakened):
  autotrade=false
  dry_run=true
  read_only=true
  live_orders_blocked=true
  max risk <=1%

Constraints:
  - Standard library only. No third-party imports.
  - Windows-first; fails gracefully on other platforms.
  - Localhost GET checks only — no POST/PUT/PATCH/DELETE.
  - No secrets, account IDs, or broker credentials.
  - No broker execution endpoints called.
  - Only terminates child processes started by this launcher.

Usage:
  py -3.11 scripts/desktop_launcher.py [options]

Options:
  --repo-root              Path to repo root (default: inferred from script location)
  --backend-url            Backend base URL (default: http://127.0.0.1:8001)
  --frontend-url           Frontend base URL (default: http://127.0.0.1:5173)
  --terminal-path          Path opened in browser (default: /terminal)
  --no-browser             Skip opening the browser
  --skip-backend           Skip starting the backend helper
  --skip-frontend          Skip starting the frontend helper
  --backend-timeout        Seconds to wait for backend readiness (default: 60)
  --frontend-timeout       Seconds to wait for frontend readiness (default: 90)
"""

from __future__ import annotations

import argparse
import atexit
import os
import platform
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------


def _tag(level: str, msg: str) -> str:
    return f"[{level}] {msg}"


def info(msg: str) -> None:
    print(_tag("INFO", msg), flush=True)


def warn(msg: str) -> None:
    print(_tag("WARN", msg), flush=True)


def error(msg: str) -> None:
    print(_tag("ERROR", msg), file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Safety banner
# ---------------------------------------------------------------------------


def print_safety_banner() -> None:
    banner = """
======================================================
  MellyTrade Local Launcher  —  READ-ONLY / DRY-RUN
======================================================
  SAFETY: autotrade=false
  SAFETY: dry_run=true
  SAFETY: read_only=true
  SAFETY: live_orders_blocked=true
  SAFETY: max risk <=1%
  No broker execution.  No live orders.
  Advisory output only.  Human review required.
======================================================
"""
    print(banner, flush=True)


# ---------------------------------------------------------------------------
# Repo root resolution
# ---------------------------------------------------------------------------


def resolve_repo_root(override: Optional[str] = None) -> Path:
    """Return the repo root directory.

    Priority:
    1. --repo-root CLI override (explicit path, validated).
    2. PyInstaller frozen mode: sys.executable → dist/MellyTradeLauncher.exe
       → parent is dist/ → parent is repo root.
       (PyInstaller --onefile extracts __file__ to a temp directory, so
       __file__-based resolution is incorrect when frozen.)
    3. Source / dev mode: __file__ → scripts/desktop_launcher.py
       → parent is scripts/ → parent is repo root.
    """
    if override:
        root = Path(override).resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"--repo-root does not exist: {root}")
        return root

    if getattr(sys, "frozen", False):
        # Running as a PyInstaller --onefile executable.
        # sys.executable = dist/MellyTradeLauncher.exe
        # .parent        = dist/
        # .parent.parent = repo root
        return Path(sys.executable).resolve().parent.parent

    # Source / dev mode:
    # __file__ → scripts/desktop_launcher.py → parent is scripts/ → parent is repo root
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# File existence guard
# ---------------------------------------------------------------------------


def ensure_file(path: Path, description: str) -> None:
    """Raise FileNotFoundError with a clear message if *path* is missing."""
    if not path.is_file():
        raise FileNotFoundError(
            f"{description} not found at: {path}\n"
            "Check that the repo root is correct and the file exists."
        )


# ---------------------------------------------------------------------------
# Process management
# ---------------------------------------------------------------------------

_started_processes: List[subprocess.Popen] = []  # type: ignore[type-arg]


def start_powershell_script(
    script_path: Path,
    description: str,
    extra_args: Optional[List[str]] = None,
) -> "subprocess.Popen[bytes]":
    """Launch *script_path* via powershell.exe and return the Popen handle.

    Uses -ExecutionPolicy Bypass so the script runs without requiring a
    system-wide policy change.  stdin is set to DEVNULL to avoid blocking.
    stdout/stderr are inherited so the helper's output appears in the console.
    """
    if platform.system() != "Windows":
        warn(f"Not running on Windows — skipping PowerShell helper: {script_path.name}")
        raise OSError("PowerShell helpers require Windows.")

    cmd: List[str] = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
    ]
    if extra_args:
        cmd.extend(extra_args)

    info(f"Starting {description}: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        # Inherit stdout/stderr so helper output is visible in the console.
        stdout=None,
        stderr=None,
    )
    _started_processes.append(proc)
    info(f"{description} started (PID {proc.pid})")
    return proc


def stop_process(proc: "subprocess.Popen[bytes]", description: str) -> None:
    """Terminate a single child process gracefully, then force-kill if needed."""
    if proc.poll() is not None:
        info(f"{description} (PID {proc.pid}) already exited.")
        return
    info(f"Stopping {description} (PID {proc.pid}) …")
    try:
        proc.terminate()
        try:
            proc.wait(timeout=5)
            info(f"{description} (PID {proc.pid}) terminated.")
        except subprocess.TimeoutExpired:
            warn(f"{description} (PID {proc.pid}) did not stop — force-killing.")
            proc.kill()
            proc.wait()
    except OSError as exc:
        warn(f"Could not stop {description} (PID {proc.pid}): {exc}")


def stop_started_processes() -> None:
    """Stop all child processes started by this launcher, in reverse order."""
    if not _started_processes:
        return
    info("Stopping child processes started by this launcher …")
    for proc in reversed(_started_processes):
        stop_process(proc, f"process PID {proc.pid}")
    _started_processes.clear()
    info("All launcher child processes stopped.")


# ---------------------------------------------------------------------------
# HTTP readiness check — GET only
# ---------------------------------------------------------------------------


def wait_for_http_ok(
    url: str,
    timeout_seconds: int,
    description: str,
    poll_interval: float = 2.0,
) -> bool:
    """Poll *url* with GET until it returns HTTP 2xx or timeout is reached.

    Only GET is used — never POST/PUT/PATCH/DELETE.
    Returns True if the endpoint became ready within the timeout, False otherwise.
    """
    deadline = time.monotonic() + timeout_seconds
    attempt = 0
    info(f"Waiting for {description} at {url} (timeout {timeout_seconds}s) …")
    while time.monotonic() < deadline:
        attempt += 1
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status < 300:
                    info(
                        f"{description} ready after {attempt} attempt(s) — HTTP {resp.status}"
                    )
                    return True
        except (urllib.error.URLError, OSError):
            pass  # Not ready yet — keep polling
        except Exception as exc:  # noqa: BLE001
            warn(f"Unexpected error polling {description}: {exc}")

        remaining = max(0.0, deadline - time.monotonic())
        if remaining < poll_interval:
            time.sleep(remaining)
        else:
            time.sleep(poll_interval)

    error(
        f"{description} did not become ready within {timeout_seconds}s.\n"
        f"  URL checked: {url}\n"
        "  Check that the helper script started successfully."
    )
    return False


# ---------------------------------------------------------------------------
# Browser
# ---------------------------------------------------------------------------


def open_terminal(terminal_url: str) -> None:
    """Open *terminal_url* in the default browser."""
    info(f"Opening browser to: {terminal_url}")
    try:
        webbrowser.open(terminal_url)
    except Exception as exc:  # noqa: BLE001
        warn(f"Could not open browser automatically: {exc}")
        warn(f"Open manually: {terminal_url}")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "MellyTrade Desktop Launcher — starts backend + frontend locally "
            "and opens the terminal UI. Read-only / dry-run. No execution controls."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        metavar="PATH",
        help="Path to repo root (default: inferred from script location).",
    )
    parser.add_argument(
        "--backend-url",
        default="http://127.0.0.1:8001",
        metavar="URL",
        help="Backend base URL (default: http://127.0.0.1:8001).",
    )
    parser.add_argument(
        "--frontend-url",
        default="http://127.0.0.1:5173",
        metavar="URL",
        help="Frontend base URL (default: http://127.0.0.1:5173).",
    )
    parser.add_argument(
        "--terminal-path",
        default="/terminal",
        metavar="PATH",
        help="Browser path to open (default: /terminal).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Skip opening the browser.",
    )
    parser.add_argument(
        "--skip-backend",
        action="store_true",
        help="Skip starting the backend helper (assume it is already running).",
    )
    parser.add_argument(
        "--skip-frontend",
        action="store_true",
        help="Skip starting the frontend helper (assume it is already running).",
    )
    parser.add_argument(
        "--backend-timeout",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Seconds to wait for backend readiness (default: 60).",
    )
    parser.add_argument(
        "--frontend-timeout",
        type=int,
        default=90,
        metavar="SECONDS",
        help="Seconds to wait for frontend readiness (default: 90).",
    )
    return parser


# ---------------------------------------------------------------------------
# Signal / atexit cleanup
# ---------------------------------------------------------------------------


def _handle_signal(signum: int, frame: object) -> None:  # noqa: ARG001
    print("\n", flush=True)
    info(f"Signal {signum} received — shutting down launcher …")
    stop_started_processes()
    sys.exit(0)


def _register_cleanup() -> None:
    atexit.register(stop_started_processes)
    try:
        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)
    except (OSError, ValueError):
        # Signal registration may fail in some environments (e.g. non-main thread).
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    print_safety_banner()
    _register_cleanup()

    # 1. Resolve repo root
    try:
        repo_root = resolve_repo_root(args.repo_root)
    except FileNotFoundError as exc:
        error(str(exc))
        return 1

    info(f"Repo root: {repo_root}")
    info(f"Backend URL:  {args.backend_url}")
    info(f"Frontend URL: {args.frontend_url}")
    info(f"Terminal:     {args.frontend_url.rstrip('/')}{args.terminal_path}")

    backend_script = repo_root / "scripts" / "start_backend_local.ps1"
    frontend_script = repo_root / "scripts" / "start_frontend_local.ps1"

    # 2. Validate helper scripts exist
    if not args.skip_backend:
        try:
            ensure_file(backend_script, "Backend helper script")
        except FileNotFoundError as exc:
            error(str(exc))
            return 1

    if not args.skip_frontend:
        try:
            ensure_file(frontend_script, "Frontend helper script")
        except FileNotFoundError as exc:
            error(str(exc))
            return 1

    # 3. Start backend
    if not args.skip_backend:
        if platform.system() != "Windows":
            warn(
                "Not running on Windows — backend PowerShell helper cannot be started."
            )
            warn("Start the backend manually and re-run with --skip-backend.")
        else:
            try:
                start_powershell_script(backend_script, "Backend helper")
            except OSError as exc:
                error(f"Could not start backend: {exc}")
                stop_started_processes()
                return 1

        # 4. Wait for backend readiness — try /api/health first, fall back to /health
        backend_health_primary = f"{args.backend_url.rstrip('/')}/api/health"
        backend_health_fallback = f"{args.backend_url.rstrip('/')}/health"

        ready = wait_for_http_ok(
            backend_health_primary,
            args.backend_timeout,
            "Backend (/api/health)",
        )
        if not ready:
            warn("Primary health endpoint not ready — trying /health fallback …")
            ready = wait_for_http_ok(
                backend_health_fallback,
                min(args.backend_timeout, 15),
                "Backend (/health fallback)",
            )
        if not ready:
            error("Backend did not become ready. Cannot continue.")
            stop_started_processes()
            return 1
    else:
        info("--skip-backend: assuming backend is already running.")

    # 5. Start frontend
    if not args.skip_frontend:
        if platform.system() != "Windows":
            warn(
                "Not running on Windows — frontend PowerShell helper cannot be started."
            )
            warn("Start the frontend manually and re-run with --skip-frontend.")
        else:
            try:
                start_powershell_script(frontend_script, "Frontend helper")
            except OSError as exc:
                error(f"Could not start frontend: {exc}")
                stop_started_processes()
                return 1

        # 6. Wait for frontend readiness
        frontend_health = f"{args.frontend_url.rstrip('/')}"
        ready = wait_for_http_ok(
            frontend_health,
            args.frontend_timeout,
            "Frontend",
        )
        if not ready:
            error("Frontend did not become ready. Cannot continue.")
            stop_started_processes()
            return 1
    else:
        info("--skip-frontend: assuming frontend is already running.")

    # 7. Open browser
    terminal_url = f"{args.frontend_url.rstrip('/')}{args.terminal_path}"
    if not args.no_browser:
        open_terminal(terminal_url)
    else:
        info(f"--no-browser: open manually at {terminal_url}")

    # 8. Keep running
    info("Launcher is running. Press Ctrl+C to stop.")
    info(
        "Safety posture: autotrade=false | dry_run=true | read_only=true | live_orders_blocked=true"
    )
    try:
        while True:
            # Check child processes are still alive
            if _started_processes:
                for proc in _started_processes:
                    if proc.poll() is not None:
                        warn(
                            f"Child process PID {proc.pid} exited unexpectedly "
                            f"(code {proc.returncode})."
                        )
            time.sleep(5)
    except KeyboardInterrupt:
        info("KeyboardInterrupt received — shutting down …")

    stop_started_processes()
    info("Launcher exited cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
