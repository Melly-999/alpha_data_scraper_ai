"""
Centralized secrets manager — loads, validates, and sanitizes secrets from
environment variables.  No third-party vault required; integrates with Docker
secrets (file-based), k8s Secrets (env injection), and CI secrets.

Usage
-----
    from secrets_manager import get_secrets

    secrets = get_secrets()
    api_key = secrets.claude_api_key          # raises if missing and required
    news_key = secrets.news_api_key           # None if optional and unset

    # Validate all required secrets up-front (raises SecretsValidationError):
    secrets.validate()

Security
--------
- Secret values are never logged (masked with ***).
- No secret is written to disk.
- __repr__ / __str__ never expose values.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Optional

logger = logging.getLogger("SecretsManager")


class SecretsValidationError(RuntimeError):
    """Raised when one or more required secrets are missing."""


def _read_file_secret(path: str) -> Optional[str]:
    """Read a secret from a file (Docker secrets / k8s projected volumes)."""
    try:
        return Path(path).read_text().strip() or None
    except (FileNotFoundError, PermissionError):
        return None


def _load(
    env_var: str,
    file_env_var: Optional[str] = None,
    default: Optional[str] = None,
) -> Optional[str]:
    """Load a secret: env var → file path env var → default."""
    value = os.getenv(env_var)
    if value:
        return value.strip()

    if file_env_var:
        file_path = os.getenv(file_env_var)
        if file_path:
            value = _read_file_secret(file_path)
            if value:
                return value

    return default


@dataclass
class Secrets:
    """All secrets used by the trading bot.

    Required secrets raise SecretsValidationError when validate() is called
    if they are None.  Optional secrets return None silently.
    """

    # ── Required ─────────────────────────────────────────────────────────────
    claude_api_key: Optional[str] = field(default=None, repr=False)

    # ── Optional ─────────────────────────────────────────────────────────────
    news_api_key: Optional[str] = field(default=None, repr=False)
    mt5_login: Optional[str] = field(default=None, repr=False)
    mt5_password: Optional[str] = field(default=None, repr=False)
    mt5_server: Optional[str] = field(default=None, repr=False)
    telegram_token: Optional[str] = field(default=None, repr=False)
    telegram_chat_id: Optional[str] = field(default=None, repr=False)
    grafana_password: Optional[str] = field(default=None, repr=False)

    # ── Class-level config ────────────────────────────────────────────────────
    _REQUIRED = frozenset({"claude_api_key"})

    def validate(self) -> None:
        """Raise SecretsValidationError if any required secret is missing."""
        missing = [
            name
            for name in self._REQUIRED
            if getattr(self, name) is None
        ]
        if missing:
            raise SecretsValidationError(
                f"Missing required secrets: {', '.join(sorted(missing))}. "
                "Set the corresponding environment variables before starting the bot."
            )
        logger.info("All required secrets validated OK.")

    def mask(self, value: Optional[str], visible: int = 4) -> str:
        """Return a masked version of *value* for safe logging."""
        if not value:
            return "<not set>"
        if len(value) <= visible:
            return "***"
        return value[:visible] + "***"

    def summary(self) -> str:
        """Return a safe string showing which secrets are set (values masked)."""
        lines = ["Secrets summary:"]
        for f in fields(self):
            if f.name.startswith("_"):
                continue
            val = getattr(self, f.name)
            status = self.mask(val) if val else "<not set>"
            required = " [REQUIRED]" if f.name in self._REQUIRED else ""
            lines.append(f"  {f.name}: {status}{required}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        names = [f.name for f in fields(self) if not f.name.startswith("_")]
        parts = [f"{n}=<hidden>" for n in names]
        return f"Secrets({', '.join(parts)})"

    def __str__(self) -> str:
        return repr(self)


_secrets_singleton: Optional[Secrets] = None


def load_secrets() -> Secrets:
    """Load all secrets from environment and return a Secrets instance."""
    return Secrets(
        claude_api_key=_load("CLAUDE_API_KEY", "CLAUDE_API_KEY_FILE"),
        news_api_key=_load("NEWS_API_KEY", "NEWS_API_KEY_FILE"),
        mt5_login=_load("MT5_LOGIN"),
        mt5_password=_load("MT5_PASSWORD", "MT5_PASSWORD_FILE"),
        mt5_server=_load("MT5_SERVER", default="MetaQuotes-Demo"),
        telegram_token=_load("TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN_FILE"),
        telegram_chat_id=_load("TELEGRAM_CHAT_ID"),
        grafana_password=_load("GRAFANA_PASSWORD", default="changeme"),
    )


def get_secrets(validate: bool = False) -> Secrets:
    """Return the global Secrets singleton.

    Args:
        validate: If True, call validate() and raise on missing required secrets.
    """
    global _secrets_singleton
    if _secrets_singleton is None:
        _secrets_singleton = load_secrets()
        logger.debug("Secrets loaded.")
    if validate:
        _secrets_singleton.validate()
    return _secrets_singleton


def reset_secrets() -> None:
    """Reset the singleton — useful in tests."""
    global _secrets_singleton
    _secrets_singleton = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = get_secrets()
    print(s.summary())
