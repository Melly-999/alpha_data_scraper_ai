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

from indicators import add_indicators


def test_add_indicators_has_expected_columns(sample_ohlcv: pd.DataFrame) -> None:
    out = add_indicators(sample_ohlcv)
    expected = {
        "rsi",
        "stoch_k",
        "stoch_d",
        "macd",
        "macd_signal",
        "macd_hist",
        "bb_middle",
        "bb_upper",
        "bb_lower",
        "bb_pos",
    }
    assert expected.issubset(set(out.columns))
    assert len(out) > 0


def test_add_indicators_no_nan_after_cleanup(sample_ohlcv: pd.DataFrame) -> None:
    out = add_indicators(sample_ohlcv)
    assert out.isna().sum().sum() == 0
