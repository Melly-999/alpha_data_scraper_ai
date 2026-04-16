from __future__ import annotations

from typing import Any

from brokers.factory import create_broker
from brokers.base import BrokerOrder


class ExecutionManager:
    """Dispatch trading signals across primary + replica brokers."""

    def __init__(self, config: dict[str, Any]):
        execution_cfg = config.get("execution", {})

        primary_name = execution_cfg.get("primary", "mt5")
        replica_names = execution_cfg.get("replicas", [])

        self.primary = create_broker(primary_name, config)
        self.replicas = [create_broker(name, config) for name in replica_names]

        self.primary.connect()
        for r in self.replicas:
            r.connect()

    def execute(self, order: BrokerOrder) -> dict[str, Any]:
        results: dict[str, Any] = {}

        results["primary"] = self.primary.place_order(order)

        for replica in self.replicas:
            try:
                results[replica.name] = replica.place_order(order)
            except Exception as exc:
                results[replica.name] = {
                    "status": "error",
                    "reason": str(exc),
                }

        return results
