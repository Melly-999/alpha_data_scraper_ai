# webhook_server.py
from fastapi import FastAPI, Request
from ai_engine import AlphaAIEngine
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Alpha AI TradingView Webhook")
engine = AlphaAIEngine()

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    """Receive alerts from TradingView"""
    try:
        data = await request.json()
        ticker = data.get("ticker", "UNKNOWN")
        action = data.get("action", "analyze")  # buy / sell / analyze
        message = data.get("message", "")

        logger.info(f"📨 TradingView Alert: {ticker} → {action} | {message}")

        # Optional: Run Claude analysis
        if "analyze" in action.lower():
            report = engine.claude.get_full_analysis(
                "citadel_technical",
                ticker_and_position=f"{ticker} (TradingView alert)"
            )
            logger.info(f"Analysis ready: {report[:200]}...")

        return {"status": "ok", "ticker": ticker, "action": action}
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "reason": str(e)}

@app.get("/health")
def health():
    return {"status": "running", "timestamp": str(__import__('datetime').datetime.now())}

if __name__ == "__main__":
    logger.info("🚀 Starting webhook server on http://localhost:8000")
    logger.info("📊 TradingView webhook URL: http://your-ip:8000/webhook")
    uvicorn.run(app, host="0.0.0.0", port=8000)
