"""Tests for ``scripts/validate_safety_config.py``.

Invokes the script as a subprocess via ``--config <temp file>`` so the
real ``config.json`` is never mutated. Each test exercises one drift
scenario and asserts the script exits with the correct code.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_safety_config.py"
REAL_CONFIG = REPO_ROOT / "config.json"


def _run_script(config_path: Path) -> subprocess.CompletedProcess[str]:
    """Invoke the script with ``--config`` pointed at the given file."""
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--config", str(config_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def _write_config(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@pytest.fixture
def base_safe_config() -> dict[str, Any]:
    """A minimal config that should pass every check the script enforces."""
    return {
        "symbol": "EURUSD",
        "timeframe": "M5",
        "autotrade": {
            "enabled": False,
            "dry_run": True,
            "min_confidence": 75.0,
        },
    }


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_script_passes_on_real_repo_config() -> None:
    """The committed ``config.json`` must keep the script green."""
    result = _run_script(REAL_CONFIG)
    assert result.returncode == 0, (
        f"script failed on real config.json with exit {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "OVERALL: PASS" in result.stdout


def test_script_passes_on_minimal_safe_config(
    tmp_path: Path, base_safe_config: dict[str, Any]
) -> None:
    cfg = tmp_path / "config.json"
    _write_config(cfg, base_safe_config)
    result = _run_script(cfg)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OVERALL: PASS" in result.stdout


# ---------------------------------------------------------------------------
# Drift scenarios — each must FAIL (non-zero exit)
# ---------------------------------------------------------------------------


def test_script_fails_when_autotrade_enabled_is_true(
    tmp_path: Path, base_safe_config: dict[str, Any]
) -> None:
    base_safe_config["autotrade"]["enabled"] = True
    cfg = tmp_path / "config.json"
    _write_config(cfg, base_safe_config)
    result = _run_script(cfg)
    assert result.returncode != 0, (
        "script must reject autotrade.enabled=true; " f"stdout:\n{result.stdout}"
    )
    assert "autotrade.enabled must be false" in result.stdout
    assert "OVERALL: FAIL" in result.stdout


def test_script_fails_when_dry_run_is_false(
    tmp_path: Path, base_safe_config: dict[str, Any]
) -> None:
    base_safe_config["autotrade"]["dry_run"] = False
    cfg = tmp_path / "config.json"
    _write_config(cfg, base_safe_config)
    result = _run_script(cfg)
    assert result.returncode != 0, result.stdout
    assert "autotrade.dry_run must be true" in result.stdout
    assert "OVERALL: FAIL" in result.stdout


def test_script_fails_when_min_confidence_below_threshold(
    tmp_path: Path, base_safe_config: dict[str, Any]
) -> None:
    base_safe_config["autotrade"]["min_confidence"] = 50.0
    cfg = tmp_path / "config.json"
    _write_config(cfg, base_safe_config)
    result = _run_script(cfg)
    assert result.returncode != 0, result.stdout
    assert "below the safety floor" in result.stdout
    assert "OVERALL: FAIL" in result.stdout


def test_script_fails_when_max_risk_per_trade_exceeds_one_percent(
    tmp_path: Path, base_safe_config: dict[str, Any]
) -> None:
    """If a future commit adds a ``risk`` block, > 1.0% must fail."""
    base_safe_config["risk"] = {
        "max_risk_per_trade_pct": 1.5,
        "max_daily_loss_pct": 5.0,
        "max_open_positions": 3,
    }
    cfg = tmp_path / "config.json"
    _write_config(cfg, base_safe_config)
    result = _run_script(cfg)
    assert result.returncode != 0, result.stdout
    assert "exceeds the 1.0% safety cap" in result.stdout
    assert "OVERALL: FAIL" in result.stdout


def test_script_passes_when_risk_block_is_complete_and_safe(
    tmp_path: Path, base_safe_config: dict[str, Any]
) -> None:
    """A well-formed risk block at the cap should pass."""
    base_safe_config["risk"] = {
        "max_risk_per_trade_pct": 1.0,
        "max_daily_loss_pct": 5.0,
        "max_open_positions": 3,
    }
    cfg = tmp_path / "config.json"
    _write_config(cfg, base_safe_config)
    result = _run_script(cfg)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OVERALL: PASS" in result.stdout


def test_script_fails_when_risk_block_missing_max_daily_loss(
    tmp_path: Path, base_safe_config: dict[str, Any]
) -> None:
    base_safe_config["risk"] = {
        "max_risk_per_trade_pct": 1.0,
        "max_open_positions": 3,
        # max_daily_loss_pct deliberately missing
    }
    cfg = tmp_path / "config.json"
    _write_config(cfg, base_safe_config)
    result = _run_script(cfg)
    assert result.returncode != 0, result.stdout
    assert "max_daily_loss_pct is missing" in result.stdout


def test_script_fails_on_invalid_json(tmp_path: Path) -> None:
    cfg = tmp_path / "config.json"
    cfg.write_text("{ this is not json }", encoding="utf-8")
    result = _run_script(cfg)
    assert result.returncode != 0, result.stdout
    assert "is not valid JSON" in result.stdout


def test_script_fails_when_config_missing(tmp_path: Path) -> None:
    """Pointing at a non-existent file should fail cleanly."""
    cfg = tmp_path / "does_not_exist.json"
    result = _run_script(cfg)
    assert result.returncode != 0, result.stdout
    assert "config file not found" in result.stdout
