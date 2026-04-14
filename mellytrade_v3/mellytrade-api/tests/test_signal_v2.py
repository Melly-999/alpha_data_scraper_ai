from fastapi.testclient import TestClient
from app.main_v2 import app

client = TestClient(app)

def test_signal_v2_unauthorized():
    payload = {
        'symbol': 'EURUSD',
        'direction': 'BUY',
        'confidence': 80,
        'price': 1.1,
        'stopLoss': 1.09,
        'takeProfit': 1.12,
        'riskPercent': 0.5,
    }
    response = client.post('/signal', json=payload)
    assert response.status_code == 401
