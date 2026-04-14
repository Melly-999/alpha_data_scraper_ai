from fastapi import APIRouter

router = APIRouter()

@router.post('/signal')
async def signal_ingest():
    return {'status': 'todo'}
