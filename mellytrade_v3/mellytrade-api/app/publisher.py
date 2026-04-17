import httpx
from app.core.config import get_settings

settings = get_settings()

async def publish_signal(payload):
    data = payload.model_dump() if hasattr(payload, 'model_dump') else payload
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            settings.cf_hub_url + '/api/publish',
            json=data,
            headers={'X-API-Secret': settings.cf_api_secret},
        )
        response.raise_for_status()
        return response.json()
