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

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

try:
    import tensorflow as tf  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency
    tf = None


def build_sequences(values: np.ndarray, lookback: int) -> tuple[np.ndarray, np.ndarray]:
    x, y = [], []
    for i in range(lookback, len(values)):
        x.append(values[i - lookback : i])
        y.append(values[i, 0])
    return np.array(x), np.array(y)


class NaiveSequenceModel:
    def predict(self, x: np.ndarray, verbose: int = 0) -> np.ndarray:
        return x[:, -1, 0:1]


@dataclass
class LSTMPipeline:
    lookback: int = 30
    epochs: int = 3
    batch_size: int = 16
    model: Any = None
    scaler: MinMaxScaler | None = None

    def fit(self, features: pd.DataFrame, target_col: str = "close") -> None:
        feature_values = features.values
        self.scaler = MinMaxScaler()
        scaled = self.scaler.fit_transform(feature_values)

        x, y = build_sequences(scaled, self.lookback)
        if len(x) < 10:
            self.model = NaiveSequenceModel()
            return

        if tf is None:
            self.model = NaiveSequenceModel()
            return

        model = tf.keras.Sequential(
            [
                tf.keras.layers.Input(shape=(x.shape[1], x.shape[2])),
                tf.keras.layers.LSTM(64, return_sequences=True),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.LSTM(32, return_sequences=True),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.LSTM(16),
                tf.keras.layers.Dense(16, activation="relu"),
                tf.keras.layers.Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mse")
        model.fit(x, y, epochs=self.epochs, batch_size=self.batch_size, verbose=0)
        self.model = model

    def predict_next_delta(
        self, features: pd.DataFrame, close_col_index: int = 0
    ) -> float:
        if self.model is None or self.scaler is None:
            return 0.0

        values = features.values
        if len(values) < self.lookback + 1:
            return 0.0

        scaled = self.scaler.transform(values)
        x_last = scaled[-self.lookback :].reshape(1, self.lookback, scaled.shape[1])
        pred_scaled_close = float(self.model.predict(x_last, verbose=0).reshape(-1)[0])

        dummy = np.zeros((1, scaled.shape[1]))
        dummy[0, close_col_index] = pred_scaled_close
        pred_unscaled = self.scaler.inverse_transform(dummy)[0, close_col_index]

        current_close = float(values[-1, close_col_index])
        return pred_unscaled - current_close
