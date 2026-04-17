from __future__ import annotations

import json

from main import AppConfig, _load_config


def test_load_config_returns_dataclass_and_normalizes_symbol(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "symbol": "GBPUSD",
                "bars": "500",
                "lookback": "20",
                "indicator_buffer_size": "120",
                "http_timeout": "3.5",
                "enable_ensemble": True,
                "autotrade": {
                    "enabled": True,
                    "dry_run": True,
                    "min_confidence": "77.5",
                },
                "risk": {
                    "min_rr": "2.0",
                    "max_open_positions": "3",
                },
            }
        ),
        encoding="utf-8",
    )

    cfg = _load_config(str(config_path))

    assert isinstance(cfg, AppConfig)
    assert cfg.symbols == ["GBPUSD"]
    assert cfg.bars == 500
    assert cfg.lookback == 20
    assert cfg.indicator_buffer_size == 120
    assert cfg.http_timeout == 3.5
    assert cfg.enable_ensemble is True
    assert cfg.autotrade.enabled is True
    assert cfg.autotrade.dry_run is True
    assert cfg.autotrade.min_confidence == 77.5
    assert cfg.risk.min_rr == 2.0
    assert cfg.risk.max_open_positions == 3


def test_load_config_keeps_safe_defaults_when_file_missing(tmp_path) -> None:
    cfg = _load_config(str(tmp_path / "missing.json"))

    assert isinstance(cfg, AppConfig)
    assert cfg.autotrade.enabled is False
    assert cfg.autotrade.dry_run is True
    assert cfg.enable_ensemble is False
