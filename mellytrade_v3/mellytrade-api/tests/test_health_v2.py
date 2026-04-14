from fastapi.testclient import TestClient
from app.main_v2 import app

client = TestClient(app)

def test_health_v2():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
