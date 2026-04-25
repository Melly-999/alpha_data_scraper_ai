from __future__ import annotations

import importlib

import pytest


def _reload_config(monkeypatch: pytest.MonkeyPatch):
    """Re-import app.config so dataclass defaults pick up env changes."""
    import sys

    for mod in ("app.config", "app.cloudmcp"):
        sys.modules.pop(mod, None)
    return importlib.import_module("app.config")


def test_cloudmcp_disabled_without_url(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CLOUDMCP_ENABLED", raising=False)
    monkeypatch.delenv("CLOUDMCP_ROUTER_URL", raising=False)
    monkeypatch.delenv("CLOUDMCP_DEFAULT_SERVERS", raising=False)

    config_mod = _reload_config(monkeypatch)
    cfg = config_mod.get_cloudmcp_config()

    assert cfg.enabled is False
    assert cfg.router_url == ""
    assert cfg.default_servers == ()
    assert cfg.timeout_seconds == 30.0
    assert cfg.connect_timeout_seconds == 5.0


def test_cloudmcp_enabled_requires_router_url(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CLOUDMCP_ENABLED", "true")
    monkeypatch.delenv("CLOUDMCP_ROUTER_URL", raising=False)

    config_mod = _reload_config(monkeypatch)
    with pytest.raises(RuntimeError, match="CLOUDMCP_ROUTER_URL"):
        config_mod.get_cloudmcp_config()


def test_cloudmcp_enabled_with_full_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CLOUDMCP_ENABLED", "true")
    monkeypatch.setenv(
        "CLOUDMCP_ROUTER_URL", "https://example.router.cloudmcp.run/mcp"
    )
    monkeypatch.setenv("CLOUDMCP_DEFAULT_SERVERS", " files , web,memory ")
    monkeypatch.setenv("CLOUDMCP_TIMEOUT_SECONDS", "45")
    monkeypatch.setenv("CLOUDMCP_CONNECT_TIMEOUT_SECONDS", "7.5")

    config_mod = _reload_config(monkeypatch)
    cfg = config_mod.get_cloudmcp_config()

    assert cfg.enabled is True
    assert cfg.router_url == "https://example.router.cloudmcp.run/mcp"
    assert cfg.default_servers == ("files", "web", "memory")
    assert cfg.timeout_seconds == 45.0
    assert cfg.connect_timeout_seconds == 7.5


def test_cloudmcp_legacy_vars_are_ignored(monkeypatch: pytest.MonkeyPatch):
    """Legacy per-server variables must not leak into the new config."""
    monkeypatch.setenv("CLOUDMCP_ENABLED", "true")
    monkeypatch.setenv(
        "CLOUDMCP_ROUTER_URL", "https://example.router.cloudmcp.run/mcp"
    )
    # These are the retired variables — setting them must be a no-op.
    monkeypatch.setenv("CLOUDMCP_TOKEN", "legacy-token")
    monkeypatch.setenv("CLOUDMCP_FILES_URL", "https://legacy/files")
    monkeypatch.setenv("CLOUDMCP_FILES_TOKEN", "legacy")
    monkeypatch.setenv("CLOUDMCP_WEB_URL", "https://legacy/web")
    monkeypatch.setenv("CLOUDMCP_WEB_TOKEN", "legacy")
    monkeypatch.setenv("CLOUDMCP_MEMORY_URL", "https://legacy/memory")
    monkeypatch.setenv("CLOUDMCP_MEMORY_TOKEN", "legacy")

    config_mod = _reload_config(monkeypatch)
    cfg = config_mod.get_cloudmcp_config()

    assert cfg.router_url == "https://example.router.cloudmcp.run/mcp"
    # No legacy fields should have materialised on the dataclass.
    field_names = {f.name for f in cfg.__dataclass_fields__.values()}
    assert field_names == {
        "enabled",
        "router_url",
        "default_servers",
        "timeout_seconds",
        "connect_timeout_seconds",
    }


def test_build_client_requires_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CLOUDMCP_ENABLED", raising=False)
    monkeypatch.delenv("CLOUDMCP_ROUTER_URL", raising=False)

    _reload_config(monkeypatch)
    cloudmcp = importlib.import_module("app.cloudmcp")

    with pytest.raises(RuntimeError, match="disabled"):
        cloudmcp.build_client()


def test_build_client_returns_httpx_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CLOUDMCP_ENABLED", "true")
    monkeypatch.setenv(
        "CLOUDMCP_ROUTER_URL", "https://example.router.cloudmcp.run/mcp"
    )
    monkeypatch.setenv("CLOUDMCP_DEFAULT_SERVERS", "files,web")

    _reload_config(monkeypatch)
    cloudmcp = importlib.import_module("app.cloudmcp")

    client = cloudmcp.build_client()
    try:
        assert str(client.base_url).startswith(
            "https://example.router.cloudmcp.run/mcp"
        )
        # URL-based auth — no Authorization header should be injected.
        assert "authorization" not in {k.lower() for k in client.headers.keys()}
    finally:
        client.close()

    assert cloudmcp.default_servers() == ("files", "web")
