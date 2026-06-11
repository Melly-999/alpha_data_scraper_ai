"""MellyTrade API application."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.alpaca_paper import router as alpaca_paper_router
from app.api.routes.health import router as health_router
from app.api.routes.neon_memory import router as neon_memory_router

app = FastAPI(title="MellyTrade API", version="0.1.0")
app.include_router(health_router)
app.include_router(alpaca_paper_router)
app.include_router(neon_memory_router)
