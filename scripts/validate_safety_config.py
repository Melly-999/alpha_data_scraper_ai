#!/usr/bin/env python3
"""Local safety validation script for MellyTrade.

Repeatable pre-PR check that confirms the committed safety posture has
not drifted. Designed to run in seconds, with zero network access, zero
broker access, zero MT5 / IBKR dependency, and only the Python standard
library.

What the script verifies:

1. ``config.json`` is present and parseable JSON.
2. ``autotrade.enabled`` is ``false``.
3. ``autotrade.dry_run`` is ``true``.
4. ``autotrade.min_confidence`` is present and ``>= 70`` when expressed
   on the percent scale (>= 1.0). Values in [0, 1] are interpreted as a
   ratio and checked against ``>= 0.70``.
5. If ``config.json`` carries a top-level ``risk`` block, the script
   verifies:
     - ``max_risk_per_trade_pct <= 1.0``
     - ``max_daily_loss_pct`` is present
     - ``max_open_positions`` is present
   When the ``risk`` block is absent, the live defaults live in
   ``app/services/risk_service.py`` / ``app/schemas/risk.py`` and are
   asserted by the existing pytest suite — the script reports this as
   a NOTE (passing) rather than failing.
6. A static text scan of ``app/api/routes/*.py`` confirms that no
   registered route path contains forbidden execution segments
   (``execute_trade``, ``place_order``, ``submit_order``, ``live_trade``,
   ``broker_execute``).

Usage::

    python scripts/validate_safety_config.py
    python scripts/validate_safety_config.py --config path/to/other.json

Exit code: 0 on PASS, 1 on FAIL. Each check prints a single line of
``[PASS]`` / ``[FAIL]`` / ``[NOTE]`` with a short explanation, and a
summary block follows at the end.

This script must NEVER mutate any file. It is read-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config.json"
ROUTES_DIR = REPO_ROOT / "app" / "api" / "routes"

# Forbidden segments that, if found inside an ``@router.<verb>("/...")``
# path string, indicate an order-placement or execution-shaped route.
FORBIDDEN_ROUTE_SEGMENTS: tuple[str, ...] = (
    "execute_trade",
    "place_order",
    "submit_order",
    "live_trade",
    "broker_execute",
)

# Regex that captures the path string from any FastAPI route decorator.
# Examples it matches:
#   @router.get("/health")
#   @router.post('/risk/emergency-stop', response_model=...)
ROUTE_DECORATOR = re.compile(
    r'@router\.(?:get|post|put|patch|delete)\s*\(\s*["\']([^"\']+)["\']'
)


# ---------------------------------------------------------------------------
# Result accumulator
# ---------------------------------------------------------------------------


class Report:
    """Collects PASS / FAIL / NOTE rows and prints a final summary."""

    def __init__(self) -> None:
        self.rows: list[tuple[str, str]] = []
        self.failed = 0

    def passed(self, message: str) -> None:
        self.rows.append(("PASS", message))

    def failed_check(self, message: str) -> None:
        self.rows.append(("FAIL", message))
        self.failed += 1

    def note(self, message: str) -> None:
        self.rows.append(("NOTE", message))

    def print_full(self) -> None:
        print("MellyTrade — local safety configuration check")
        print("=" * 60)
        for kind, msg in self.rows:
            print(f"[{kind}] {msg}")
        print("=" * 60)
        total = len(self.rows)
        passed_n = sum(1 for k, _ in self.rows if k == "PASS")
        failed_n = sum(1 for k, _ in self.rows if k == "FAIL")
        notes_n = sum(1 for k, _ in self.rows if k == "NOTE")
        print(
            f"Summary: {passed_n} passed, "
            f"{failed_n} failed, "
            f"{notes_n} notes ({total} checks total)."
        )
        if self.failed:
            print("OVERALL: FAIL")
        else:
            print("OVERALL: PASS")


# ---------------------------------------------------------------------------
# Individual check helpers
# ---------------------------------------------------------------------------


def _load_config(path: Path, report: Report) -> dict[str, Any] | None:
    """Read and parse the config file. Returns the dict or None on failure."""
    if not path.is_file():
        report.failed_check(f"config file not found at {path}")
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.failed_check(f"could not read {path}: {exc}")
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        report.failed_check(f"{path} is not valid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        report.failed_check(f"{path} top-level value must be an object")
        return None
    report.passed(f"{path.name} parsed successfully")
    return data


def _check_autotrade(config: dict[str, Any], report: Report) -> None:
    autotrade = config.get("autotrade")
    if not isinstance(autotrade, dict):
        report.failed_check("config.autotrade block is missing or not an object")
        return

    # autotrade.enabled
    enabled = autotrade.get("enabled")
    if enabled is False:
        report.passed("autotrade.enabled is false")
    else:
        report.failed_check(
            f"autotrade.enabled must be false (got {enabled!r}); "
            "Terminal V1 must never enable live trading"
        )

    # autotrade.dry_run
    dry_run = autotrade.get("dry_run")
    if dry_run is True:
        report.passed("autotrade.dry_run is true")
    else:
        report.failed_check(
            f"autotrade.dry_run must be true (got {dry_run!r}); "
            "Terminal V1 dry-run posture is non-negotiable"
        )

    # autotrade.min_confidence — accept either a percent (>= 1) or a
    # ratio in [0, 1]. Strict floor: 70% / 0.70.
    min_conf = autotrade.get("min_confidence")
    if min_conf is None:
        report.failed_check("autotrade.min_confidence is missing")
        return
    try:
        min_conf_f = float(min_conf)
    except (TypeError, ValueError):
        report.failed_check(
            f"autotrade.min_confidence is not numeric (got {min_conf!r})"
        )
        return
    # Heuristic: if value <= 1.0, treat as a ratio; otherwise as a percent.
    if min_conf_f <= 1.0:
        threshold = 0.70
        scale = "ratio"
    else:
        threshold = 70.0
        scale = "percent"
    if min_conf_f >= threshold:
        report.passed(
            f"autotrade.min_confidence is {min_conf_f} ({scale} scale; "
            f">= {threshold})"
        )
    else:
        report.failed_check(
            f"autotrade.min_confidence={min_conf_f} ({scale} scale) is "
            f"below the safety floor of {threshold}"
        )


def _check_risk_block(config: dict[str, Any], report: Report) -> None:
    """Conditionally validate the risk block if present in config.json.

    The repo currently keeps the live risk defaults in
    ``app/services/risk_service.py`` / ``app/schemas/risk.py`` rather
    than ``config.json``. If a future commit adds a ``risk`` block to
    config, this function enforces the required fields. If the block
    is absent we emit a NOTE rather than a FAIL — the existing pytest
    safety suite already verifies the live ``RiskConfig`` shape.
    """
    risk = config.get("risk")
    if risk is None:
        report.note(
            "config.risk block is absent; risk defaults live in "
            "app/schemas/risk.py and are asserted by the pytest safety "
            "suite (test_safety_invariants.py)"
        )
        return
    if not isinstance(risk, dict):
        report.failed_check(
            f"config.risk must be an object if present (got {type(risk).__name__})"
        )
        return

    # max_risk_per_trade_pct <= 1.0
    max_risk = risk.get("max_risk_per_trade_pct")
    if max_risk is None:
        report.failed_check("config.risk.max_risk_per_trade_pct is missing")
    else:
        try:
            max_risk_f = float(max_risk)
        except (TypeError, ValueError):
            report.failed_check(
                f"config.risk.max_risk_per_trade_pct is not numeric "
                f"(got {max_risk!r})"
            )
        else:
            if max_risk_f <= 1.0:
                report.passed(
                    f"config.risk.max_risk_per_trade_pct={max_risk_f} "
                    f"(<= 1.0%)"
                )
            else:
                report.failed_check(
                    f"config.risk.max_risk_per_trade_pct={max_risk_f} "
                    f"exceeds the 1.0% safety cap"
                )

    # max_daily_loss_pct presence
    if "max_daily_loss_pct" in risk:
        report.passed(
            f"config.risk.max_daily_loss_pct present "
            f"(value={risk['max_daily_loss_pct']!r})"
        )
    else:
        report.failed_check("config.risk.max_daily_loss_pct is missing")

    # max_open_positions presence
    if "max_open_positions" in risk:
        report.passed(
            f"config.risk.max_open_positions present "
            f"(value={risk['max_open_positions']!r})"
        )
    else:
        report.failed_check("config.risk.max_open_positions is missing")


def _check_route_segments(routes_dir: Path, report: Report) -> None:
    """Static text scan of the FastAPI route files for forbidden segments."""
    if not routes_dir.is_dir():
        report.note(
            f"routes directory not found at {routes_dir}; "
            "skipping route-segment scan"
        )
        return
    offenders: list[tuple[str, str, str]] = []
    files_scanned = 0
    paths_seen = 0
    for py_file in sorted(routes_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        files_scanned += 1
        try:
            source = py_file.read_text(encoding="utf-8")
        except OSError as exc:
            report.failed_check(f"could not read {py_file}: {exc}")
            continue
        for path in ROUTE_DECORATOR.findall(source):
            paths_seen += 1
            for seg in FORBIDDEN_ROUTE_SEGMENTS:
                if seg in path:
                    offenders.append((py_file.name, path, seg))
    if offenders:
        for filename, path, seg in offenders:
            report.failed_check(
                f"route path '{path}' in {filename} contains forbidden "
                f"segment '{seg}'"
            )
        return
    report.passed(
        f"no forbidden execution segments found across "
        f"{files_scanned} route file(s) ({paths_seen} path(s) scanned)"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run(config_path: Path, routes_dir: Path = ROUTES_DIR) -> int:
    """Run the validation. Returns 0 on PASS, 1 on FAIL."""
    report = Report()
    config = _load_config(config_path, report)
    if config is not None:
        _check_autotrade(config, report)
        _check_risk_block(config, report)
    _check_route_segments(routes_dir, report)
    report.print_full()
    return 1 if report.failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate MellyTrade local safety configuration."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"path to the config JSON (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--routes-dir",
        type=Path,
        default=ROUTES_DIR,
        help=(
            "directory containing FastAPI route modules to scan "
            f"(default: {ROUTES_DIR})"
        ),
    )
    args = parser.parse_args(argv)
    return run(args.config, args.routes_dir)


if __name__ == "__main__":
    sys.exit(main())
