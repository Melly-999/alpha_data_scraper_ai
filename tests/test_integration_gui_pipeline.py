# Copyright 2025-2026 Mati (Melly-999)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import Any

from gui import render_console
from indicators import add_indicators
from lstm_model import LSTMPipeline
from mt5_fetcher import MT5Fetcher
from signal_generator import generate_signal, signal_to_dict


def test_gui_pipeline_snapshot_prints(capsys: Any) -> None:
    fetcher = MT5Fetcher(symbol="EURUSD", timeframe="M5")
    raw = fetcher.get_latest_rates(bars=280)
    data = add_indicators(raw)

    features: Any = data[
        ["close", "rsi", "stoch_k", "stoch_d", "macd_hist", "bb_pos", "volume"]
    ]

    model = LSTMPipeline(lookback=20, epochs=1, batch_size=8)
    model.fit(features)
    delta = model.predict_next_delta(features)

    latest = data.iloc[-1]
    result = generate_signal(latest, delta)

    payload: dict[str, Any] = {
        "symbol": "EURUSD",
        "timeframe": "M5",
        "last_close": float(latest["close"]),
        "lstm_delta": float(delta),
        "signal": signal_to_dict(result),
    }

    render_console(payload)
    out: str = str(capsys.readouterr().out)
    assert "Alpha AI Live Snapshot" in out
    assert "EURUSD" in out
    assert '"signal"' in out
