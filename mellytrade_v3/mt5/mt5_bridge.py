from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

import httpx

from ensemble_combiner import CombinedSignal, EnsembleCombiner, TechnicalSignal
from lstm_signal_adapter import LSTMSignalAdapter

FASTAPI_URL = os.getenv('FASTAPI_URL', 'http://127.0.0.1:8000')
FASTAPI_KEY = os.getenv('FASTAPI_KEY', 'change-me-fastapi-key')
SYMBOLS = [s.strip() for s in os.getenv('SYMBOLS', 'EURUSD,GBPUSD,XAUUSD,USDJPY').split(',') if s.strip()]
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '15'))
RISK_PERCENT = float(os.getenv('RISK_PERCENT', '0.8'))

class MT5Bridge:
    def __init__(self):
        self.running = False
        self._client = httpx.AsyncClient(timeout=5.0)
        self._combiner = EnsembleCombiner()
        self._lstm = {sym: LSTMSignalAdapter(sym, ensemble_size=2) for sym in SYMBOLS}

    def _fake_tech_signal(self, symbol: str) -> TechnicalSignal:
        price = 1.1 if symbol != 'XAUUSD' else 2300.0
        direction = 'BUY'
        confidence = 78.0
        sl = price * 0.995
        tp = price * 1.01
        return TechnicalSignal(direction=direction, confidence=confidence, sl=round(sl, 5), tp=round(tp, 5))

    async def _analyse(self, symbol: str):
        tech = self._fake_tech_signal(symbol)
        lstm = self._lstm[symbol].predict(None)
        combined = self._combiner.combine(tech, lstm)
        if combined.blocked:
            return None
        price = 1.1 if symbol != 'XAUUSD' else 2300.0
        return {
            'symbol': symbol,
            'direction': combined.direction,
            'confidence': combined.confidence,
            'price': price,
            'stopLoss': combined.sl,
            'takeProfit': combined.tp,
            'riskPercent': RISK_PERCENT,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'mt5_bridge_v3',
            'meta': {
                'regime': combined.regime,
                'lstm_weight': round(combined.lstm_weight, 2),
                'technical_weight': round(combined.technical_weight, 2),
                'reasons': combined.reasons,
            },
        }

    async def _push(self, payload):
        response = await self._client.post(
            FASTAPI_URL + '/signal',
            json=payload,
            headers={'X-API-Key': FASTAPI_KEY},
        )
        return response.status_code, response.text

    async def run(self):
        self.running = True
        while self.running:
            results = await asyncio.gather(*[self._analyse(s) for s in SYMBOLS])
            for payload in results:
                if payload is not None:
                    await self._push(payload)
            await asyncio.sleep(POLL_INTERVAL)

    async def close(self):
        await self._client.aclose()

async def main():
    bridge = MT5Bridge()
    try:
        await bridge.run()
    finally:
        await bridge.close()

if __name__ == '__main__':
    asyncio.run(main())
