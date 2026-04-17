#!/usr/bin/env python3
"""
MCP Server for Alpha AI Trading Bot.

Exposes the full trading pipeline as MCP tools:
  fetch data → compute indicators → generate signals → validate risk → execute trades

Runs via stdio (local) or streamable HTTP (remote).
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from enum import Enum
from pathlib import Path
from collections.abc import Callable
from typing import Any, Dict, List, Optional, TypeVar

try:
    from pydantic import BaseModel, ConfigDict, Field, field_validator

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

    class BaseModel:  # type: ignore[no-redef]
        """Minimal import-time shim for the optional MCP entrypoint."""

        def __init__(self, **data: object) -> None:
            for key, value in data.items():
                setattr(self, key, value)

        def model_dump(self) -> dict[str, object]:
            return dict(self.__dict__)

    class ConfigDict(dict):  # type: ignore[no-redef]
        pass

    def Field(default: object = None, **_kwargs: object) -> object:  # type: ignore[no-redef]
        return default

    def field_validator(  # type: ignore[no-redef]
        *_args: object, **_kwargs: object
    ) -> Callable[[_F], _F]:
        def _decorator(func: _F) -> _F:
            return func

        return _decorator


# Ensure project root is on sys.path so local imports work
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from mcp.server.fastmcp import FastMCP  # noqa: E402

    MCP_AVAILABLE = True
except ImportError:
    FastMCP = None  # type: ignore[assignment,misc]
    MCP_AVAILABLE = False

from core.config import (  # noqa: E402
    ACCOUNT_BALANCE,
)
from indicators import add_indicators  # noqa: E402
from mt5_fetcher import batch_fetch  # noqa: E402
from risk.risk_manager import RiskConfig, RiskManager  # noqa: E402
from signal_generator import generate_signal, signal_to_dict  # noqa: E402

# Optional heavy deps — graceful fallback
try:
    from lstm_model import LSTMPipeline  # noqa: E402
except Exception:
    LSTMPipeline = None  # type: ignore[assignment,misc]

try:
    from news_sentiment import SentimentAnalyzer  # noqa: E402
except Exception:
    SentimentAnalyzer = None  # type: ignore[assignment,misc]

try:
    from ai_engine import AIEngine  # noqa: E402
except Exception:
    AIEngine = None  # type: ignore[assignment,misc]

try:
    from ensemble_combiner import (
        EnsembleCombiner,
        TechnicalSignal,
    )  # noqa: E402
    from lstm_signal_adapter import LSTMSignalAdapter  # noqa: E402

    ENSEMBLE_AVAILABLE = True
except ImportError:
    ENSEMBLE_AVAILABLE = False

_F = TypeVar("_F", bound=Callable[..., object])

logger = logging.getLogger("alpha_mcp")


class _MissingMCP:
    """No-op decorator host used when optional MCP deps are not installed."""

    def __init__(self, name: str) -> None:
        self.name = name

    def tool(self, *_args: object, **_kwargs: object) -> Callable[[_F], _F]:
        def _decorator(func: _F) -> _F:
            return func

        return _decorator

    def run(self) -> None:
        raise RuntimeError(
            "MCP support is optional. Install it with "
            "`pip install -r requirements-mcp.txt` before running mcp_server.py."
        )


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------
mcp = (
    FastMCP("alpha_trading_mcp")
    if MCP_AVAILABLE and PYDANTIC_AVAILABLE
    else _MissingMCP("alpha_trading_mcp")
)

# Shared state (lightweight — no heavy init until first tool call)
_risk_manager: RiskManager | None = None
_engine: Any = None

LSTM_FEATURE_COLS = [
    "close",
    "rsi",
    "stoch_k",
    "stoch_d",
    "macd_hist",
    "bb_pos",
    "volume",
]


def _get_risk_manager() -> RiskManager:
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager()
    return _risk_manager


# ---------------------------------------------------------------------------
# Enums & Pydantic input models
# ---------------------------------------------------------------------------


class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


class FetchDataInput(BaseModel):
    """Input for fetching OHLCV data."""

    model_config = ConfigDict(str_strip_whitespace=True)

    symbols: List[str] = Field(
        ...,
        description="List of instrument symbols (e.g. ['EURUSD','XAUUSD'])",
        min_length=1,
        max_length=20,
    )
    timeframe: str = Field(
        default="M5",
        description="Candle timeframe: M1, M5, M15, H1",
    )
    bars: int = Field(
        default=700,
        description="Number of bars to fetch (min 120)",
        ge=120,
        le=5000,
    )

    @field_validator("timeframe")
    @classmethod
    def validate_tf(cls, v: str) -> str:
        allowed = {"M1", "M5", "M15", "H1"}
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"timeframe must be one of {allowed}")
        return v


class AnalyzeSymbolInput(BaseModel):
    """Input for analysing a single symbol."""

    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(
        ..., description="Instrument symbol (e.g. 'EURUSD')", min_length=1
    )
    timeframe: str = Field(default="M5", description="Candle timeframe")
    bars: int = Field(default=700, ge=120, le=5000)
    use_lstm: bool = Field(
        default=True, description="Run LSTM prediction (slower but more accurate)"
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class RiskCheckInput(BaseModel):
    """Input for pre-trade risk validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    signal: str = Field(..., description="Trade signal: BUY or SELL")
    confidence: float = Field(..., description="Signal confidence 0-100", ge=0, le=100)
    entry_price: Optional[float] = Field(default=None, description="Entry price")
    stop_loss: Optional[float] = Field(default=None, description="Stop-loss price")
    take_profit: Optional[float] = Field(default=None, description="Take-profit price")
    balance: Optional[float] = Field(
        default=None, description="Account balance override"
    )

    @field_validator("signal")
    @classmethod
    def validate_signal(cls, v: str) -> str:
        v = v.upper()
        if v not in ("BUY", "SELL"):
            raise ValueError("signal must be BUY or SELL")
        return v


class PositionSizeInput(BaseModel):
    """Input for position sizing calculation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    balance: float = Field(default=ACCOUNT_BALANCE, description="Account balance", gt=0)
    stop_loss_pips: float = Field(
        default=20.0, description="Stop-loss distance in pips", gt=0
    )
    risk_pct: Optional[float] = Field(
        default=None, description="Override risk % per trade (default from config)"
    )


class FullPipelineInput(BaseModel):
    """Input for running the complete signal pipeline on one or more symbols."""

    model_config = ConfigDict(str_strip_whitespace=True)

    symbols: List[str] = Field(
        default_factory=lambda: ["EURUSD"],
        description="Symbols to analyse",
        min_length=1,
        max_length=20,
    )
    timeframe: str = Field(default="M5")
    bars: int = Field(default=700, ge=120, le=5000)
    include_risk_check: bool = Field(
        default=True, description="Run risk gate after signal generation"
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class EngineStatusInput(BaseModel):
    """Input for engine status query."""

    model_config = ConfigDict(str_strip_whitespace=True)

    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _fmt_signal_md(
    symbol: str, sig: dict[str, Any], risk_result: dict[str, Any] | None = None
) -> str:
    """Format a signal snapshot as Markdown."""
    lines = [
        f"## {symbol}",
        f"- **Signal**: {sig.get('signal', 'N/A')}",
        f"- **Confidence**: {sig.get('confidence', 0):.1f}%",
        f"- **Score**: {sig.get('score', 0)}",
    ]
    reasons = sig.get("reasons", [])
    if reasons:
        lines.append("- **Reasons**: " + "; ".join(reasons))
    if risk_result:
        lines.append(f"- **Risk gate**: {risk_result.get('status', 'N/A')}")
        if risk_result.get("lot_size"):
            lines.append(f"- **Lot size**: {risk_result['lot_size']}")
        if risk_result.get("reason"):
            lines.append(f"- **Note**: {risk_result['reason']}")
    return "\n".join(lines)


def _handle_error(e: Exception) -> str:
    """Consistent error formatting."""
    return f"Error: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="alpha_fetch_data",
    annotations={
        "title": "Fetch OHLCV Market Data",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def alpha_fetch_data(params: FetchDataInput) -> str:
    """Fetch OHLCV candle data for one or more symbols from MT5 (or synthetic fallback).

    Returns last N bars of open/high/low/close/volume data. Use this as the
    first step before running analysis or generating signals.

    Args:
        params (FetchDataInput): symbols, timeframe, bars count

    Returns:
        str: JSON with per-symbol summary (rows, last close, time range)
    """
    try:
        loop = asyncio.get_running_loop()
        raw = await loop.run_in_executor(
            None,
            batch_fetch,
            params.symbols,
            params.timeframe,
            params.bars,
        )
        summary: Dict[str, Any] = {}
        for sym, df in raw.items():
            summary[sym] = {
                "rows": len(df),
                "last_close": (
                    round(float(df["close"].iloc[-1]), 6) if len(df) > 0 else None
                ),
                "first_time": (
                    str(df["time"].iloc[0])
                    if "time" in df.columns and len(df) > 0
                    else None
                ),
                "last_time": (
                    str(df["time"].iloc[-1])
                    if "time" in df.columns and len(df) > 0
                    else None
                ),
            }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="alpha_analyze_symbol",
    annotations={
        "title": "Analyse Symbol (Indicators + Signal)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def alpha_analyze_symbol(params: AnalyzeSymbolInput) -> str:
    """Run full technical analysis on a single symbol: fetch data, compute
    all indicators (RSI, MACD, Bollinger, ADX, ATR, OBV, VWAP), optionally
    run LSTM prediction, and generate a BUY/SELL/HOLD signal with confidence.

    Args:
        params (AnalyzeSymbolInput): symbol, timeframe, bars, use_lstm flag

    Returns:
        str: Markdown or JSON analysis report
    """
    try:
        loop = asyncio.get_running_loop()
        raw = await loop.run_in_executor(
            None,
            batch_fetch,
            [params.symbol],
            params.timeframe,
            params.bars,
        )
        df = raw.get(params.symbol)
        if df is None or df.empty:
            return f"No data available for {params.symbol}"

        data = add_indicators(df)
        if data.empty:
            return f"Insufficient data for indicator computation on {params.symbol}"

        lstm_delta = 0.0
        if params.use_lstm and LSTMPipeline is not None:
            try:
                pipeline = LSTMPipeline(lookback=30, epochs=2)
                features = data[LSTM_FEATURE_COLS]
                pipeline.fit(features)
                lstm_delta = float(
                    pipeline.predict_next_delta(features, close_col_index=0)
                )
            except Exception as le:
                logger.warning(f"LSTM failed for {params.symbol}: {le}")

        latest = data.iloc[-1]
        signal = generate_signal(latest, lstm_delta=lstm_delta)
        sig_dict = signal_to_dict(signal)

        result = {
            "symbol": params.symbol,
            "timeframe": params.timeframe,
            "bars": len(data),
            "last_close": round(float(latest["close"]), 6),
            "lstm_delta": round(lstm_delta, 6),
            "signal": sig_dict,
            "indicators": {
                "rsi": round(float(latest.get("rsi", 0)), 2),
                "macd_hist": round(float(latest.get("macd_hist", 0)), 6),
                "bb_pos": round(float(latest.get("bb_pos", 0)), 4),
                "adx": round(float(latest.get("adx", 0)), 2),
                "atr_pct": round(float(latest.get("atr_pct", 0)), 6),
                "obv_z": round(float(latest.get("obv_z", 0)), 4),
                "vwap_dev": round(float(latest.get("vwap_dev", 0)), 4),
            },
        }

        if params.response_format == ResponseFormat.MARKDOWN:
            md = [
                f"# Analysis: {params.symbol} ({params.timeframe})",
                "",
                f"**Last close**: {result['last_close']}  |  **Bars**: {result['bars']}",
                f"**LSTM delta**: {result['lstm_delta']}",
                "",
                "## Signal",
                f"- **Direction**: {sig_dict['signal']}",
                f"- **Confidence**: {sig_dict['confidence']:.1f}%",
                f"- **Score**: {sig_dict['score']}",
                "- **Reasons**: " + "; ".join(sig_dict["reasons"]),
                "",
                "## Key Indicators",
            ]
            for k, v in result["indicators"].items():
                md.append(f"- **{k}**: {v}")
            return "\n".join(md)

        return json.dumps(result, indent=2)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="alpha_validate_risk",
    annotations={
        "title": "Pre-Trade Risk Validation",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def alpha_validate_risk(params: RiskCheckInput) -> str:
    """Run all pre-trade risk gates: confidence threshold, max open positions,
    daily loss cap, risk-reward ratio, and position sizing.

    Returns whether the trade is ALLOWED or BLOCKED with the specific reason.

    Args:
        params (RiskCheckInput): signal, confidence, optional SL/TP/entry

    Returns:
        str: JSON risk validation result
    """
    try:
        rm = _get_risk_manager()
        if params.balance:
            rm.update_balance(params.balance)

        validation = rm.validate(
            signal=params.signal,
            confidence=params.confidence,
            entry_price=params.entry_price,
            stop_loss=params.stop_loss,
            take_profit=params.take_profit,
        )
        return json.dumps(validation.to_dict(), indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="alpha_calculate_position_size",
    annotations={
        "title": "Calculate Position Size",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def alpha_calculate_position_size(params: PositionSizeInput) -> str:
    """Calculate the optimal lot size given account balance, stop-loss
    distance, and risk percentage (max 1% per trade by default).

    Args:
        params (PositionSizeInput): balance, stop_loss_pips, optional risk_pct

    Returns:
        str: JSON with lot_size and calculation details
    """
    try:
        rm = _get_risk_manager()
        if params.risk_pct is not None:
            original = rm.config.max_risk_per_trade_pct
            # Temporarily override — frozen dataclass workaround
            rm.config = RiskConfig(
                max_risk_per_trade_pct=params.risk_pct,
                min_confidence=rm.config.min_confidence,
                min_rr=rm.config.min_rr,
                max_open_positions=rm.config.max_open_positions,
                max_daily_loss_pct=rm.config.max_daily_loss_pct,
                max_position_size_lots=rm.config.max_position_size_lots,
                stop_loss_pips=rm.config.stop_loss_pips,
                pip_value_per_lot=rm.config.pip_value_per_lot,
            )
            lot = rm.calculate_lot_size(params.balance, sl_pips=params.stop_loss_pips)
            rm.config = RiskConfig(max_risk_per_trade_pct=original)
        else:
            lot = rm.calculate_lot_size(params.balance, sl_pips=params.stop_loss_pips)

        risk_amt = params.balance * (rm.config.max_risk_per_trade_pct / 100.0)
        return json.dumps(
            {
                "lot_size": lot,
                "balance": params.balance,
                "risk_pct": params.risk_pct or rm.config.max_risk_per_trade_pct,
                "risk_amount": round(risk_amt, 2),
                "stop_loss_pips": params.stop_loss_pips,
            },
            indent=2,
        )
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="alpha_run_pipeline",
    annotations={
        "title": "Run Full Trading Pipeline",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def alpha_run_pipeline(params: FullPipelineInput) -> str:
    """Run the complete trading pipeline for one or more symbols:
    fetch OHLCV → compute indicators → LSTM prediction → generate signal
    → risk validation. Returns a consolidated report.

    This is the primary tool for getting actionable trade signals.

    Args:
        params (FullPipelineInput): symbols, timeframe, bars, risk_check flag

    Returns:
        str: Markdown or JSON report with signals for all symbols
    """
    try:
        loop = asyncio.get_running_loop()
        raw = await loop.run_in_executor(
            None,
            batch_fetch,
            params.symbols,
            params.timeframe,
            params.bars,
        )

        rm = _get_risk_manager()
        results: List[Dict[str, Any]] = []

        for symbol in params.symbols:
            df = raw.get(symbol)
            if df is None or df.empty:
                results.append({"symbol": symbol, "error": "No data"})
                continue

            data = add_indicators(df)
            if data.empty:
                results.append({"symbol": symbol, "error": "Insufficient data"})
                continue

            lstm_delta = 0.0
            if LSTMPipeline is not None:
                try:
                    pipeline = LSTMPipeline(lookback=30, epochs=2)
                    features = data[LSTM_FEATURE_COLS]
                    pipeline.fit(features)
                    lstm_delta = float(
                        pipeline.predict_next_delta(features, close_col_index=0)
                    )
                except Exception:
                    pass

            latest = data.iloc[-1]
            signal = generate_signal(latest, lstm_delta=lstm_delta)
            sig_dict = signal_to_dict(signal)

            risk_result = None
            if params.include_risk_check:
                validation = rm.validate(
                    signal=sig_dict["signal"], confidence=sig_dict["confidence"]
                )
                risk_result = validation.to_dict()

            results.append(
                {
                    "symbol": symbol,
                    "last_close": round(float(latest["close"]), 6),
                    "lstm_delta": round(lstm_delta, 6),
                    "signal": sig_dict,
                    "risk": risk_result,
                }
            )

        if params.response_format == ResponseFormat.MARKDOWN:
            md_lines = ["# Alpha AI Pipeline Results", ""]
            for r in results:
                if "error" in r:
                    md_lines.append(f"## {r['symbol']}\n- Error: {r['error']}\n")
                else:
                    md_lines.append(
                        _fmt_signal_md(r["symbol"], r["signal"], r.get("risk"))
                    )
                    md_lines.append(f"- **Last close**: {r['last_close']}")
                    md_lines.append(f"- **LSTM delta**: {r['lstm_delta']}")
                    md_lines.append("")
            return "\n".join(md_lines)

        return json.dumps(results, indent=2)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="alpha_get_risk_status",
    annotations={
        "title": "Get Risk Manager Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def alpha_get_risk_status(params: EngineStatusInput) -> str:
    """Get the current risk manager status: balance, open positions,
    daily P&L, and all risk configuration parameters.

    Args:
        params (EngineStatusInput): response_format

    Returns:
        str: Markdown or JSON status report
    """
    try:
        rm = _get_risk_manager()
        status = rm.get_status()
        can_trade, reason = rm.can_trade()
        status["can_trade"] = can_trade
        status["can_trade_reason"] = reason

        if params.response_format == ResponseFormat.MARKDOWN:
            rc = status.get("risk_config", {})
            md = [
                "# Risk Manager Status",
                "",
                f"- **Balance**: ${status['balance']:,.2f}",
                f"- **Open positions**: {status['open_positions']}",
                f"- **Daily P&L**: {status['daily_pnl_pct']:.2f}%",
                f"- **Can trade**: {'Yes' if can_trade else 'No'} ({reason})",
                "",
                "## Risk Configuration",
                f"- Max risk/trade: {rc.get('max_risk_per_trade_pct', 1.0)}%",
                f"- Min confidence: {rc.get('min_confidence', 50)}",
                f"- Min R:R: {rc.get('min_rr', 1.2)}",
                f"- Max open positions: {rc.get('max_open_positions', 5)}",
                f"- Max daily loss: {rc.get('max_daily_loss_pct', 2.0)}%",
                f"- Max lot size: {rc.get('max_position_size_lots', 1.0)}",
            ]
            return "\n".join(md)

        return json.dumps(status, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="alpha_get_sentiment",
    annotations={
        "title": "Get News Sentiment",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def alpha_get_sentiment(params: EngineStatusInput) -> str:
    """Fetch and aggregate news sentiment from ForexFactory economic
    calendar and NewsAPI. Returns per-currency sentiment scores.

    Args:
        params (EngineStatusInput): response_format

    Returns:
        str: Markdown or JSON sentiment report
    """
    if SentimentAnalyzer is None:
        return "Error: SentimentAnalyzer not available (missing dependencies)"

    try:
        analyzer = SentimentAnalyzer()
        sentiment_map = await analyzer.analyze_sentiment_async(
            include_forexfactory=True,
            include_newsapi=True,
        )

        if params.response_format == ResponseFormat.MARKDOWN:
            md = ["# News Sentiment Report", ""]
            if not sentiment_map:
                md.append("No sentiment data available.")
            for curr, score in sentiment_map.items():
                md.append(f"## {curr}")
                md.append(f"- Avg sentiment: {score.average_sentiment:+.2f}")
                md.append(
                    f"- Positive: {score.positive_count} | Neutral: {score.neutral_count} | Negative: {score.negative_count}"
                )
                md.append(f"- High-impact events: {score.high_impact_count}")
                md.append("")
            return "\n".join(md)

        result = {}
        for curr, score in sentiment_map.items():
            result[curr] = {
                "average_sentiment": round(score.average_sentiment, 4),
                "positive": score.positive_count,
                "neutral": score.neutral_count,
                "negative": score.negative_count,
                "high_impact": score.high_impact_count,
            }
        return json.dumps(result, indent=2)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="alpha_ensemble_signal",
    annotations={
        "title": "Ensemble Signal (Technical + LSTM)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def alpha_ensemble_signal(params: AnalyzeSymbolInput) -> str:
    """Run the ensemble combiner that fuses a technical signal (from indicators)
    with the LSTM adapter signal for a single symbol. Returns a weighted
    CombinedSignal with direction, confidence, regime, and blocking status.

    Requires ensemble_combiner + lstm_signal_adapter modules.

    Args:
        params (AnalyzeSymbolInput): symbol, timeframe, bars

    Returns:
        str: Markdown or JSON ensemble analysis report
    """
    if not ENSEMBLE_AVAILABLE:
        return "Error: Ensemble modules not available (ensemble_combiner / lstm_signal_adapter missing)"

    try:
        loop = asyncio.get_running_loop()
        raw = await loop.run_in_executor(
            None,
            batch_fetch,
            [params.symbol],
            params.timeframe,
            params.bars,
        )
        df = raw.get(params.symbol)
        if df is None or df.empty:
            return f"No data available for {params.symbol}"

        data = add_indicators(df)
        if data.empty:
            return f"Insufficient data for {params.symbol}"

        # Technical signal via standard signal_generator
        lstm_delta = 0.0
        if LSTMPipeline is not None:
            try:
                pipeline = LSTMPipeline(lookback=30, epochs=2)
                features = data[LSTM_FEATURE_COLS]
                pipeline.fit(features)
                lstm_delta = float(
                    pipeline.predict_next_delta(features, close_col_index=0)
                )
            except Exception:
                pass

        latest = data.iloc[-1]
        sig = generate_signal(latest, lstm_delta=lstm_delta)
        tech = TechnicalSignal(
            direction=sig.signal,
            confidence=sig.confidence,
            sl=0.0,
            tp=0.0,
        )

        # LSTM adapter signal
        adapter = LSTMSignalAdapter(params.symbol, ensemble_size=2)
        lstm_sig = adapter.predict(data)

        # Combine
        combiner = EnsembleCombiner()
        combined = combiner.combine(tech, lstm_sig)

        result = {
            "symbol": params.symbol,
            "direction": combined.direction,
            "confidence": round(combined.confidence, 2),
            "blocked": combined.blocked,
            "block_reason": combined.block_reason,
            "regime": combined.regime,
            "lstm_weight": round(combined.lstm_weight, 2),
            "technical_weight": round(combined.technical_weight, 2),
            "reasons": combined.reasons[:5],
            "technical_signal": sig.signal,
            "technical_confidence": round(sig.confidence, 2),
            "lstm_direction": lstm_sig.direction,
            "lstm_confidence": round(lstm_sig.confidence, 2),
            "lstm_uncertainty": round(lstm_sig.lstm_uncertainty, 4),
        }

        if params.response_format == ResponseFormat.MARKDOWN:
            md = [
                f"# Ensemble Signal: {params.symbol}",
                "",
                f"**Direction**: {combined.direction}  |  **Confidence**: {combined.confidence:.1f}%",
                f"**Blocked**: {'Yes — ' + combined.block_reason if combined.blocked else 'No'}",
                f"**Regime**: {combined.regime}",
                "",
                "## Weights",
                f"- Technical: {combined.technical_weight:.0%} ({sig.signal} @ {sig.confidence:.1f}%)",
                f"- LSTM: {combined.lstm_weight:.0%} ({lstm_sig.direction} @ {lstm_sig.confidence:.1f}%, unc={lstm_sig.lstm_uncertainty:.3f})",
                "",
                "## Reasons",
            ]
            for r in combined.reasons[:5]:
                md.append(f"- {r}")
            return "\n".join(md)

        return json.dumps(result, indent=2)

    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
