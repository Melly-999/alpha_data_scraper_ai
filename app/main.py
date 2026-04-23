from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    account,
    dashboard,
    health,
    logs,
    mt5,
    orders,
    positions,
    risk,
    signals,
)
from app.core.container import build_container
from app.core.settings import load_settings
from app.schemas.common import LogCategory, Severity
from app.schemas.log import LogEntry
from app.services.fixture_data import prototype_logs
from core.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)
settings = load_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = build_container()
    container.log_service.seed(
        [LogEntry.model_validate(item) for item in prototype_logs()]
    )
    app.state.container = container
    logger.info("MellyTrade Phase 1 backend initialized")
    yield


app = FastAPI(
    title="MellyTrade Phase 1 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    request.app.state.container.log_service.add(
        category=LogCategory.API,
        severity=Severity.INFO,
        message=f"{request.method} {request.url.path} [{response.status_code}] {duration_ms}ms request_id={request_id}",
    )
    response.headers["x-request-id"] = request_id
    response.headers["x-response-time-ms"] = str(duration_ms)
    return response


@app.exception_handler(KeyError)
async def handle_key_error(_: Request, exc: KeyError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled application error", exc_info=exc)
    if hasattr(request.app.state, "container"):
        request.app.state.container.log_service.add(
            category=LogCategory.SYSTEM,
            severity=Severity.ERROR,
            message=f"Unhandled error: {exc}",
        )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


for router in (
    health.router,
    dashboard.router,
    account.router,
    signals.router,
    positions.router,
    orders.router,
    risk.router,
    mt5.router,
    logs.router,
):
    app.include_router(router, prefix="/api")
