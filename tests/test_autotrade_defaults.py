"""Regression tests for the non-negotiable safety defaults.

``config.json`` is the shipped runtime config. The repo's safety
posture (CLAUDE.md) requires:

- ``autotrade.enabled`` is **off** by default
- ``autotrade.dry_run`` is **on** by default
- ``autotrade.min_confidence`` is at least the documented 70 gate

These tests fail loudly if anyone ships a config that loosens the
defaults — the most common way a paper-trading bot accidentally goes
live in production.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config.json"


def test_config_json_exists():
    assert CONFIG_PATH.exists(), f"Missing shipped config: {CONFIG_PATH}"


def test_autotrade_disabled_by_default():
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    autotrade = cfg.get("autotrade", {})
    assert autotrade.get("enabled") is False, (
        "autotrade.enabled must be False in the shipped config.json — "
        "flipping this to True is a live-trading commitment and must "
        "only happen via an explicit profile file."
    )


def test_dry_run_enabled_by_default():
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    autotrade = cfg.get("autotrade", {})
    assert autotrade.get("dry_run") is True, (
        "autotrade.dry_run must be True in the shipped config.json. "
        "This is the second layer of the dry-run-by-default safety net."
    )


def test_min_confidence_meets_documented_gate():
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    autotrade = cfg.get("autotrade", {})
    min_conf = float(autotrade.get("min_confidence", 0))
    assert min_conf >= 70.0, (
        f"autotrade.min_confidence={min_conf} is below the documented "
        f"70% live-trade gate (see CLAUDE.md)."
    )


def test_main_module_imports_cleanly():
    """main.py must import without NameError / ModuleNotFoundError.

    Previously it referenced a retired FTMO_MODE constant and a
    non-existent utils.risk_manager module; both regressions would
    fire at import time and crash the CLI.
    """
    import importlib
    import sys

    sys.modules.pop("main", None)
    importlib.import_module("main")
