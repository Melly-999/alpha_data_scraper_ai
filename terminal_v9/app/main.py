from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.stream import router as stream_router
from app.api.ops import router as ops_router
from app.core.logging_config import setup_logging
from app.core.request_middleware import request_context_middleware
from app.core.security import auth_middleware
from app.db.db import init_db
from app.services.ws_broadcast_service import broadcaster
from app.services.execution_queue import execution_queue

setup_logging()
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broadcaster.start()
    await execution_queue.start()
    yield
    await execution_queue.stop()
    await broadcaster.stop()

app = FastAPI(title="Alpha AI Trading Terminal v9", lifespan=lifespan)
app.middleware("http")(auth_middleware)
app.middleware("http")(request_context_middleware)

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(stream_router, prefix="/stream", tags=["stream"])
app.include_router(ops_router, prefix="/ops", tags=["ops"])
