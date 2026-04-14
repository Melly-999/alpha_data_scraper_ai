from fastapi import FastAPI
from app.schemas import HealthResponse

app = FastAPI(title='MellyTrade API', version='0.3.0')

@app.get('/health', response_model=HealthResponse)
def health():
    return HealthResponse()
