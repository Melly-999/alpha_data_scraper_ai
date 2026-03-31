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

import pandas as pd

from signal_generator import generate_signal


def test_generate_signal_buy_case() -> None:
    latest = pd.Series(
        {
            "rsi": 28.0,
            "stoch_k": 18.0,
            "stoch_d": 15.0,
            "macd_hist": 0.001,
            "bb_pos": 0.1,
        }
    )
    result = generate_signal(latest, lstm_delta=0.002)
    assert result.signal == "BUY"
    assert 33 <= result.confidence <= 85


def test_generate_signal_sell_case() -> None:
    latest = pd.Series(
        {
            "rsi": 72.0,
            "stoch_k": 84.0,
            "stoch_d": 87.0,
            "macd_hist": -0.001,
            "bb_pos": 0.92,
        }
    )
    result = generate_signal(latest, lstm_delta=-0.003)
    assert result.signal == "SELL"
    assert 33 <= result.confidence <= 85
