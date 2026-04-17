from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Iterator

import pytest

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent  # mellytrade-api/
REPO_ROOT = PKG_ROOT.parent.parent  # alpha_data_scraper_ai/

for p in (str(PKG_ROOT), str(REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(autouse=True)
def _isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Fresh SQLite + predictable risk settings for every test."""
    db_file = tmp_path / "mellytrade.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file.as_posix()}")
    monkeypatch.setenv("FASTAPI_KEY", "test-key")
    monkeypatch.setenv("COOLDOWN_SECONDS", "60")
    monkeypatch.setenv("MIN_CONFIDENCE", "70")
    monkeypatch.setenv("MAX_RISK_PERCENT", "1.0")
    monkeypatch.delenv("CF_HUB_URL", raising=False)

    # Force a fresh import so engine/settings pick up the new env.
    for mod in list(sys.modules):
        if mod == "app" or mod.startswith("app."):
            del sys.modules[mod]

    yield


@pytest.fixture()
def client():
    os.environ["DATABASE_URL"]  # ensure fixture ran
    from fastapi.testclient import TestClient

    main = importlib.import_module("app.main")
    with TestClient(main.app) as c:
        yield c
