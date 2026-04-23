from __future__ import annotations

from datetime import datetime, timedelta, timezone

BASE_TIME = datetime(2026, 4, 23, 14, 33, 12, tzinfo=timezone.utc)


def prototype_signals() -> list[dict[str, object]]:
    return [
        {
            "id": "sig-001",
            "symbol": "EURUSD",
            "direction": "BUY",
            "confidence": 82,
            "mtf_alignment": 4,
            "mtf_total": 5,
            "sentiment_score": 0.62,
            "claude_status": "VALIDATED",
            "regime": "TRENDING",
            "sl": 1.0782,
            "tp": 1.0854,
            "entry": 1.0812,
            "rr": 2.1,
            "eligible": True,
            "blocked": False,
            "blocked_reason": None,
            "cooldown_remaining": None,
            "timestamp": BASE_TIME - timedelta(minutes=1),
            "reasoning": "Strong bullish momentum on H4 confirmed by M15 breakout. Sentiment remains positive and risk controls are satisfied.",
            "technicals": {
                "rsi": 58.2,
                "macd": "bullish_cross",
                "atr": 0.00045,
                "ema20": 1.0798,
                "ema50": 1.0781,
            },
            "timeframes": {
                "M15": "BUY",
                "H1": "BUY",
                "H4": "BUY",
                "D1": "BUY",
                "W1": "NEUTRAL",
            },
            "claude_response": "Validated by fallback contract data.",
            "technical_factors": [
                "RSI neutral-bullish",
                "MACD bullish cross",
                "Higher timeframe alignment",
            ],
            "sentiment_context": "ECB commentary remains supportive for EUR strength.",
        },
        {
            "id": "sig-002",
            "symbol": "XAUUSD",
            "direction": "SELL",
            "confidence": 78,
            "mtf_alignment": 3,
            "mtf_total": 5,
            "sentiment_score": -0.44,
            "claude_status": "VALIDATED",
            "regime": "RANGING",
            "sl": 2345.5,
            "tp": 2298.0,
            "entry": 2321.0,
            "rr": 2.0,
            "eligible": True,
            "blocked": False,
            "blocked_reason": None,
            "cooldown_remaining": None,
            "timestamp": BASE_TIME - timedelta(minutes=4),
            "reasoning": "Gold is stalling at resistance while the dollar bid is strengthening. The setup remains dry-run eligible.",
            "technicals": {
                "rsi": 62.4,
                "macd": "bearish_div",
                "atr": 8.2,
                "ema20": 2318.4,
                "ema50": 2305.1,
            },
            "timeframes": {
                "M15": "SELL",
                "H1": "SELL",
                "H4": "SELL",
                "D1": "NEUTRAL",
                "W1": "BUY",
            },
            "claude_response": "Validated by fallback contract data.",
            "technical_factors": [
                "Distribution at resistance",
                "Bearish divergence on MACD",
                "News bias is negative",
            ],
            "sentiment_context": "Moderately bearish macro tone from jobs data.",
        },
        {
            "id": "sig-003",
            "symbol": "GBPUSD",
            "direction": "HOLD",
            "confidence": 51,
            "mtf_alignment": 2,
            "mtf_total": 5,
            "sentiment_score": 0.08,
            "claude_status": "INSUFFICIENT",
            "regime": "CHOPPY",
            "sl": None,
            "tp": None,
            "entry": None,
            "rr": None,
            "eligible": False,
            "blocked": True,
            "blocked_reason": "LOW_CONFIDENCE",
            "cooldown_remaining": None,
            "timestamp": BASE_TIME - timedelta(minutes=8),
            "reasoning": "Mixed signals across timeframes. Confidence is below the execution floor and there is no tradeable edge.",
            "technicals": {
                "rsi": 50.1,
                "macd": "flat",
                "atr": 0.00038,
                "ema20": 1.2641,
                "ema50": 1.2658,
            },
            "timeframes": {
                "M15": "BUY",
                "H1": "NEUTRAL",
                "H4": "SELL",
                "D1": "NEUTRAL",
                "W1": "BUY",
            },
            "claude_response": "Insufficient alignment for an actionable view.",
            "technical_factors": [
                "Mixed timeframe alignment",
                "Flat MACD",
                "No protection levels",
            ],
            "sentiment_context": "Neutral to mixed macro backdrop.",
        },
        {
            "id": "sig-004",
            "symbol": "USDJPY",
            "direction": "BUY",
            "confidence": 68,
            "mtf_alignment": 3,
            "mtf_total": 5,
            "sentiment_score": 0.31,
            "claude_status": "VALIDATED",
            "regime": "TRENDING",
            "sl": 153.2,
            "tp": 155.8,
            "entry": 154.3,
            "rr": 1.9,
            "eligible": False,
            "blocked": True,
            "blocked_reason": "COOLDOWN",
            "cooldown_remaining": 87,
            "timestamp": BASE_TIME - timedelta(minutes=13),
            "reasoning": "Valid bullish structure but the same setup fired recently and is still in cooldown.",
            "technicals": {
                "rsi": 61.8,
                "macd": "bullish",
                "atr": 0.285,
                "ema20": 154.12,
                "ema50": 153.44,
            },
            "timeframes": {
                "M15": "BUY",
                "H1": "BUY",
                "H4": "BUY",
                "D1": "NEUTRAL",
                "W1": "NEUTRAL",
            },
            "claude_response": "Validated, but cooldown is active.",
            "technical_factors": [
                "Trend intact",
                "Protection levels present",
                "Cooldown still active",
            ],
            "sentiment_context": "Yen remains soft but execution is deferred.",
        },
    ]


def prototype_account() -> dict[str, object]:
    return {
        "balance": 50000.0,
        "equity": 51234.56,
        "margin": 2100.0,
        "free_margin": 49134.56,
        "margin_level": 2440.7,
        "drawdown": -1.2,
        "daily_pnl": 1234.56,
        "daily_pnl_pct": 2.47,
        "open_positions": 3,
        "today_trades": 7,
    }


def prototype_positions_open() -> list[dict[str, object]]:
    return [
        {
            "id": "pos-001",
            "ticket": 1842001,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lots": 0.10,
            "open_price": 1.0799,
            "current_price": 1.0812,
            "sl": 1.0782,
            "tp": 1.0854,
            "unrealized_pnl": 130.0,
            "duration_seconds": 8040,
            "signal_id": "sig-001",
            "mt5_synced": True,
            "open_time": BASE_TIME - timedelta(hours=2, minutes=14),
        },
        {
            "id": "pos-002",
            "ticket": 1842002,
            "symbol": "XAUUSD",
            "direction": "SELL",
            "lots": 0.05,
            "open_price": 2324.5,
            "current_price": 2321.0,
            "sl": 2345.5,
            "tp": 2298.0,
            "unrealized_pnl": 175.0,
            "duration_seconds": 2760,
            "signal_id": "sig-002",
            "mt5_synced": True,
            "open_time": BASE_TIME - timedelta(minutes=46),
        },
    ]


def prototype_positions_history() -> list[dict[str, object]]:
    return [
        {
            "id": "pos-c01",
            "ticket": 1841990,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lots": 0.10,
            "open_price": 1.0771,
            "close_price": 1.0799,
            "realized_pnl": 280.0,
            "duration_seconds": 6240,
            "signal_id": None,
            "mt5_synced": True,
            "open_time": BASE_TIME - timedelta(hours=3, minutes=58),
            "close_time": BASE_TIME - timedelta(hours=2, minutes=15),
        },
        {
            "id": "pos-c02",
            "ticket": 1841985,
            "symbol": "USDJPY",
            "direction": "SELL",
            "lots": 0.12,
            "open_price": 154.82,
            "close_price": 155.11,
            "realized_pnl": -348.0,
            "duration_seconds": 3300,
            "signal_id": None,
            "mt5_synced": True,
            "open_time": BASE_TIME - timedelta(hours=4, minutes=26),
            "close_time": BASE_TIME - timedelta(hours=3, minutes=31),
        },
    ]


def prototype_orders() -> list[dict[str, object]]:
    return [
        {
            "id": "ord-001",
            "ticket": 1842010,
            "symbol": "EURUSD",
            "direction": "BUY",
            "type": "MARKET",
            "lots": 0.10,
            "price": 1.0812,
            "sl": 1.0782,
            "tp": 1.0854,
            "status": "FILLED",
            "source": "AI",
            "confidence": 82,
            "slippage_pips": 0.1,
            "submitted_at": BASE_TIME - timedelta(minutes=1, seconds=3),
            "filled_at": BASE_TIME - timedelta(minutes=1, seconds=3),
            "notes": "Signal sig-001 DRY-RUN",
        },
        {
            "id": "ord-002",
            "ticket": 1842009,
            "symbol": "XAUUSD",
            "direction": "SELL",
            "type": "MARKET",
            "lots": 0.05,
            "price": 2321.0,
            "sl": 2345.5,
            "tp": 2298.0,
            "status": "FILLED",
            "source": "AI",
            "confidence": 78,
            "slippage_pips": 0.2,
            "submitted_at": BASE_TIME - timedelta(minutes=4, seconds=29),
            "filled_at": BASE_TIME - timedelta(minutes=4, seconds=29),
            "notes": "Signal sig-002 DRY-RUN",
        },
        {
            "id": "ord-003",
            "ticket": 1842008,
            "symbol": "USDJPY",
            "direction": "BUY",
            "type": "MARKET",
            "lots": 0.10,
            "price": 154.3,
            "sl": 153.2,
            "tp": 155.8,
            "status": "BLOCKED",
            "source": "AI",
            "confidence": 68,
            "slippage_pips": None,
            "submitted_at": BASE_TIME - timedelta(minutes=13, seconds=16),
            "filled_at": None,
            "notes": "BLOCKED: COOLDOWN",
        },
    ]


def prototype_mt5_status() -> dict[str, object]:
    return {
        "connected": False,
        "server": "ICMarkets-Demo02",
        "account_id": "80124753",
        "account_name": "MellyTrade Demo",
        "broker": "IC Markets",
        "currency": "USD",
        "leverage": "1:100",
        "last_heartbeat": BASE_TIME.isoformat(),
        "latency_ms": 12,
        "symbols_loaded": 284,
        "orders_sync": True,
        "positions_sync": True,
        "build_version": "5.0.37",
        "fallback": True,
        "connection_logs": [
            {"time": "14:33:12", "event": "HEARTBEAT", "msg": "Fallback heartbeat OK"},
            {"time": "14:00:00", "event": "RECONNECT", "msg": "Fallback mode active"},
        ],
    }


def prototype_watchlist() -> list[dict[str, object]]:
    return [
        {
            "symbol": "EURUSD",
            "bid": 1.08108,
            "ask": 1.08121,
            "change": 0.42,
            "signal": "BUY",
            "confidence": 82,
        },
        {
            "symbol": "XAUUSD",
            "bid": 2320.85,
            "ask": 2321.05,
            "change": -0.18,
            "signal": "SELL",
            "confidence": 78,
        },
        {
            "symbol": "GBPUSD",
            "bid": 1.26388,
            "ask": 1.26401,
            "change": 0.08,
            "signal": "HOLD",
            "confidence": 51,
        },
        {
            "symbol": "USDJPY",
            "bid": 154.285,
            "ask": 154.298,
            "change": 0.31,
            "signal": "BUY*",
            "confidence": 68,
        },
    ]


def prototype_activity_feed() -> list[dict[str, str]]:
    return [
        {
            "time": "14:32:09",
            "type": "TRADE",
            "msg": "[DRY] BUY EURUSD 0.10 @ 1.08120",
            "color": "green",
        },
        {
            "time": "14:28:43",
            "type": "TRADE",
            "msg": "[DRY] SELL XAUUSD 0.05 @ 2321.00",
            "color": "green",
        },
        {
            "time": "14:25:19",
            "type": "BLOCK",
            "msg": "GBPUSD HOLD blocked — low confidence",
            "color": "amber",
        },
        {
            "time": "14:19:56",
            "type": "BLOCK",
            "msg": "USDJPY BUY blocked — cooldown",
            "color": "amber",
        },
    ]


def prototype_equity_curve() -> list[dict[str, float | int]]:
    values = [
        50000.0,
        50150.0,
        50320.0,
        50210.0,
        50540.0,
        50780.0,
        50940.0,
        51040.0,
        51120.0,
        51234.56,
    ]
    return [{"x": index, "y": value} for index, value in enumerate(values)]


def prototype_risk_violations() -> list[dict[str, object]]:
    return [
        {
            "id": "rv-001",
            "type": "COOLDOWN",
            "signal_ref": "USDJPY BUY",
            "reason": "Same signal fired recently. Cooldown still active.",
            "severity": "WARN",
            "timestamp": BASE_TIME - timedelta(minutes=13),
        },
        {
            "id": "rv-002",
            "type": "LOW_CONFIDENCE",
            "signal_ref": "GBPUSD HOLD",
            "reason": "Confidence below execution floor.",
            "severity": "WARN",
            "timestamp": BASE_TIME - timedelta(minutes=8),
        },
    ]


def prototype_logs() -> list[dict[str, object]]:
    return [
        {
            "id": "l-001",
            "timestamp": BASE_TIME,
            "category": "MT5",
            "severity": "INFO",
            "message": "Fallback heartbeat OK.",
        },
        {
            "id": "l-002",
            "timestamp": BASE_TIME - timedelta(minutes=1),
            "category": "EXECUTION",
            "severity": "INFO",
            "message": "[DRY-RUN] BUY EURUSD 0.10 @ 1.08120 — Signal sig-001",
        },
        {
            "id": "l-003",
            "timestamp": BASE_TIME - timedelta(minutes=8),
            "category": "RISK",
            "severity": "WARN",
            "message": "BLOCKED: GBPUSD HOLD — confidence below threshold.",
        },
    ]
