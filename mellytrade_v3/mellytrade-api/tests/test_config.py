from __future__ import annotations

import importlib


def test_get_settings_reads_environment_per_call(monkeypatch):
    config = importlib.import_module("app.config")

    monkeypatch.setenv("FASTAPI_KEY", "first-key")
    monkeypatch.setenv("MIN_CONFIDENCE", "71")
    first = config.get_settings()

    monkeypatch.setenv("FASTAPI_KEY", "second-key")
    monkeypatch.setenv("MIN_CONFIDENCE", "82")
    second = config.get_settings()

    assert first.fastapi_key == "first-key"
    assert first.min_confidence == 71.0
    assert second.fastapi_key == "second-key"
    assert second.min_confidence == 82.0
