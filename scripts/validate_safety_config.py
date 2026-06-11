"""Validate the API safety contract."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _get_app():
    from app.main import app

    return app


def main() -> int:
    app = _get_app()
    paths = {}
    for route in app.routes:
        if hasattr(route, "path"):
            paths[route.path] = route.methods

    allowed_read_only_paths = {}
    for path, methods in paths.items():
        if path.startswith("/alpaca-paper") or path == "/health":
            allowed_read_only_paths[path] = methods
        if path.startswith("/api/neon-memory"):
            allowed_read_only_paths[path] = methods

    expected_paths = {
        "/health",
        "/alpaca-paper/status",
        "/alpaca-paper/account-preview",
        "/alpaca-paper/market-clock",
        "/alpaca-paper/watchlist-preview",
        "/alpaca-paper/order-preview",
        "/api/neon-memory/status",
        "/api/neon-memory/summary",
    }
    if set(allowed_read_only_paths) != expected_paths:
        unexpected = sorted(allowed_read_only_paths)
        raise SystemExit(f"Unexpected read-only API routes: {unexpected}")

    forbidden_methods = {"POST", "PUT", "PATCH", "DELETE"}
    for path, methods in allowed_read_only_paths.items():
        if forbidden_methods & set(methods or []):
            forbidden = sorted(methods)
            message = f"Forbidden methods present on {path}: {forbidden}"
            raise SystemExit(message)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
