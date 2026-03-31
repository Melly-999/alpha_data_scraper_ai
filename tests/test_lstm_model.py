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

import numpy as np
import pandas as pd

from lstm_model import LSTMPipeline, build_sequences


def test_build_sequences_shapes() -> None:
    arr = np.arange(120).reshape(40, 3)
    x, y = build_sequences(arr, lookback=5)
    assert x.shape == (35, 5, 3)
    assert y.shape == (35,)


def test_lstm_pipeline_predict_delta(sample_ohlcv: pd.DataFrame) -> None:
    features = sample_ohlcv[["close", "open", "high", "low", "volume"]].copy()
    model = LSTMPipeline(lookback=20, epochs=1, batch_size=8)
    model.fit(features)
    delta = model.predict_next_delta(features, close_col_index=0)
    assert isinstance(delta, float)
    assert np.isfinite(delta)
