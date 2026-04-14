from fastapi import FastAPI

from app.api.server import app as health_app
from app.api.signal_endpoint_v2 import router as signal_router

app = FastAPI(title='MellyTrade API', version='0.3.0')
app.include_router(signal_router)
app.router.routes.extend(health_app.router.routes)
