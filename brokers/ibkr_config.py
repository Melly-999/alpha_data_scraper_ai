# brokers/ibkr_config.py
"""IBKR-001 — :class:`IBKRPaperConfig`.

Safety-first configuration for the read-only IBKR Paper adapter
(:class:`brokers.ibkr_paper_readonly.IBKRPaperReadOnlyAdapter`).

Design contract:

* ``paper`` and ``read_only`` are pinned to ``True`` and rejected if
  flipped, so a config object can never describe an executable live
  session.
* No credential field — no ``password`` / ``token`` / ``api_key`` /
  ``secret`` / ``credential`` / ``account_id`` is declared. The TWS /
  IB Gateway session that this adapter will eventually read from is
  started manually by the operator outside this process.
* No environment / secret loading. No values are logged.
* Standard library only (``dataclasses``).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IBKRPaperConfig:
    """Connection parameters for the read-only IBKR Paper adapter.

    The defaults match the standard TWS Paper port (``7497``) on
    ``localhost``. ``client_id`` is a process-local handle TWS uses to
    distinguish concurrent read-only consumers; it is *not* a broker
    account id.
    """

    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 101
    account_filter: str | None = None
    timeout_s: float = 5.0
    enabled: bool = False
    paper: bool = True
    read_only: bool = True

    def __post_init__(self) -> None:
        if self.paper is not True:
            raise ValueError("IBKRPaperConfig.paper must be True")
        if self.read_only is not True:
            raise ValueError("IBKRPaperConfig.read_only must be True")
        if not isinstance(self.host, str) or not self.host:
            raise ValueError("IBKRPaperConfig.host must be a non-empty string")
        if self.port <= 0:
            raise ValueError("IBKRPaperConfig.port must be > 0")
        if self.client_id <= 0:
            raise ValueError("IBKRPaperConfig.client_id must be > 0")
        if self.timeout_s <= 0:
            raise ValueError("IBKRPaperConfig.timeout_s must be > 0")


__all__ = ["IBKRPaperConfig"]
