"""Alpha AI Execution Control Plane — FastAPI v2.2 entrypoint.

Registers:
  GET /status               — health + mode check
  GET /account              — account snapshot
  GET /positions            — open positions
  GET /execution/decision   — latest execution decision
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.account import router as account_router
from api.routes.execution import router as execution_router
from api.routes.execution import set_execution_service
from api.routes.positions import router as positions_router
from execution_service import ExecutionService
from services.execution_snapshot_service import ExecutionSnapshotService
from services.signal_history_service import SignalHistoryService

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Shared service singletons
# ------------------------------------------------------------------
_signal_history = SignalHistoryService()
_snapshot_exporter = ExecutionSnapshotService()
execution_svc = ExecutionService(
    signal_history=_signal_history,
    snapshot_exporter=_snapshot_exporter,
)

# Wire the shared service into the execution route module
set_execution_service(execution_svc)

# ------------------------------------------------------------------
# FastAPI application
# ------------------------------------------------------------------
app = FastAPI(
    title="Alpha AI Execution Control Plane",
    version="2.2.0",
    description=(
        "Execution visibility API for the Alpha AI trading backend. "
        "All operations run in dry_run mode — live trading is never enabled."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------


@app.get("/status")
def status() -> dict:
    """System health and mode check."""
    logger.info("Status endpoint called")
    return {"status": "ok", "mode": "dry_run", "version": "2.2.0"}


app.include_router(account_router)
app.include_router(positions_router)
app.include_router(execution_router)
