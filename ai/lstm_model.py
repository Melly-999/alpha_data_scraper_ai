from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

try:
    import tensorflow as tf  # type: ignore

    _TF_AVAILABLE = True
except Exception:  # pragma: no cover - optional runtime dependency
    tf = None
    _TF_AVAILABLE = False


# ── Sequence builder ──────────────────────────────────────────────────────────


def build_sequences(
    values: np.ndarray, lookback: int, target_idx: int = 0
) -> tuple[np.ndarray, np.ndarray]:
    x, y = [], []
    for i in range(lookback, len(values)):
        x.append(values[i - lookback : i])
        y.append(values[i, target_idx])
    return np.array(x), np.array(y)


# ── Naive fallback (no TF dependency) ────────────────────────────────────────


class NaiveSequenceModel:
    """Last-value carry-forward — used when TensorFlow is unavailable."""

    def predict(self, x: np.ndarray, verbose: int = 0) -> np.ndarray:
        return x[:, -1, 0]  # shape (batch,)


# ── Attention-augmented model factory ─────────────────────────────────────────


def _build_attention_lstm(
    input_shape: tuple[int, int], seed: int = 0
) -> "tf.keras.Model":
    """Stacked LSTM with scaled dot-product self-attention.

    Architecture
    ------------
    Input  → LSTM(64, return_seq) → Dropout(0.2)
           → LSTM(32, return_seq) → Dropout(0.2)
           → Self-attention (Q/K/V projections, dim=32)
           → GlobalAveragePooling → Dense(16, relu) → Dense(1)

    The attention layer lets the model focus on the most informative
    timesteps in the sequence rather than relying solely on the final
    hidden state.
    """
    tf.random.set_seed(seed)

    inputs = tf.keras.layers.Input(shape=input_shape)

    # Stacked LSTM
    x = tf.keras.layers.LSTM(64, return_sequences=True)(inputs)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.LSTM(32, return_sequences=True)(x)
    x = tf.keras.layers.Dropout(0.2)(x)

    # Scaled dot-product self-attention
    dim = 32
    scale = tf.math.sqrt(tf.cast(dim, tf.float32))
    query = tf.keras.layers.Dense(dim)(x)
    key = tf.keras.layers.Dense(dim)(x)
    value = tf.keras.layers.Dense(dim)(x)

    scores = tf.matmul(query, key, transpose_b=True) / scale
    weights = tf.keras.layers.Softmax(axis=-1)(scores)
    context = tf.matmul(weights, value)

    pooled = tf.keras.layers.GlobalAveragePooling1D()(context)
    hidden = tf.keras.layers.Dense(16, activation="relu")(pooled)
    outputs = tf.keras.layers.Dense(1)(hidden)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3), loss="mse")
    return model


# ── Pipeline ──────────────────────────────────────────────────────────────────


@dataclass
class LSTMPipeline:
    """LSTM pipeline with optional attention and ensemble averaging.

    Args:
        lookback:      Number of past bars fed to the model.
        epochs:        Training epochs per ensemble member.
        batch_size:    Mini-batch size.
        ensemble_size: Number of independently-seeded models to train.
                       Set to 1 to disable ensemble (single model, faster).
                       Ensemble predictions are averaged; std-dev is available
                       via ``prediction_uncertainty()`` for position sizing.
    """

    lookback: int = 30
    epochs: int = 3
    batch_size: int = 16
    ensemble_size: int = 3

    # Internal state — not part of the public constructor signature
    _models: list[Any] = field(default_factory=list, init=False, repr=False)
    scaler: MinMaxScaler | None = field(default=None, init=False, repr=False)
    target_idx: int = field(default=0, init=False, repr=False)

    # ── Backward-compatible property ──────────────────────────────────────────
    @property
    def model(self) -> Any | None:
        """Return the primary model (first ensemble member) for legacy callers."""
        return self._models[0] if self._models else None

    # ── Training ──────────────────────────────────────────────────────────────

    def fit(self, features: pd.DataFrame, target_col: str = "close") -> None:
        # Store target column index
        if target_col not in features.columns:
            raise ValueError(f"Target column '{target_col}' not found in features")
        self.target_idx = features.columns.get_loc(target_col)

        feature_values = features.values
        self.scaler = MinMaxScaler()
        scaled = self.scaler.fit_transform(feature_values)

        x, y = build_sequences(scaled, self.lookback, target_idx=self.target_idx)

        if len(x) < 10 or not _TF_AVAILABLE:
            warnings.warn(
                "Insufficient data or TensorFlow unavailable. Using naive fallback model.",
                UserWarning,
            )
            self._models = [NaiveSequenceModel()]
            return

        input_shape = (x.shape[1], x.shape[2])
        self._models = []

        for seed in range(self.ensemble_size):
            try:
                m = _build_attention_lstm(input_shape, seed=seed)
                m.fit(
                    x,
                    y,
                    epochs=self.epochs,
                    batch_size=self.batch_size,
                    verbose=0,
                )
                self._models.append(m)
            except Exception as e:
                warnings.warn(
                    f"LSTM training failed for seed {seed}: {e}. Falling back to naive model.",
                    UserWarning,
                )
                self._models = [NaiveSequenceModel()]
                return

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict_next_delta(
        self,
        features: pd.DataFrame,
        close_col_index: int = 0,  # kept for backward compatibility, but target_idx is used
    ) -> float:
        """Predict the price delta for the next bar.

        Returns the ensemble-averaged prediction (or single-model if ensemble_size=1).
        Returns 0.0 when the pipeline has not been fitted or data is insufficient.
        """
        if not self._models or self.scaler is None:
            return 0.0

        values = features.values
        if len(values) < self.lookback + 1:
            return 0.0

        x_last = self._prepare_input(values)
        raw_preds = self._raw_predictions(x_last)

        pred_unscaled = self._unscale(float(np.mean(raw_preds)), values)
        return pred_unscaled - float(values[-1, self.target_idx])

    def prediction_uncertainty(
        self,
        features: pd.DataFrame,
        close_col_index: int = 0,  # kept for backward compatibility
    ) -> float:
        """Return the standard deviation of ensemble predictions (in price units).

        A higher value means the ensemble models disagree — consider reducing
        position size or requiring higher signal confidence before trading.

        Returns 0.0 when ensemble_size=1 or TF is unavailable (no meaningful
        uncertainty estimate in those cases).
        """
        if len(self._models) <= 1 or self.scaler is None:
            return 0.0

        values = features.values
        if len(values) < self.lookback + 1:
            return 0.0

        x_last = self._prepare_input(values)
        raw_preds = self._raw_predictions(x_last)

        unscaled = [self._unscale(p, values) for p in raw_preds]
        return float(np.std(unscaled))

    # ── Private helpers ────────────────────────────────────────────────────────

    def _prepare_input(self, values: np.ndarray) -> np.ndarray:
        """Scale and reshape the last `lookback` rows into model input format."""
        scaled = self.scaler.transform(values)  # type: ignore[union-attr]
        return scaled[-self.lookback :].reshape(1, self.lookback, scaled.shape[1])

    def _raw_predictions(self, x_last: np.ndarray) -> list[float]:
        """Collect raw (scaled) predictions from every ensemble member."""
        return [
            float(m.predict(x_last, verbose=0).reshape(-1)[0]) for m in self._models
        ]

    def _unscale(self, pred_scaled_close: float, values: np.ndarray) -> float:
        """Inverse-transform a scaled close prediction back to price units."""
        dummy = np.zeros((1, values.shape[1]))
        dummy[0, self.target_idx] = pred_scaled_close
        return float(
            self.scaler.inverse_transform(dummy)[0, self.target_idx]  # type: ignore[union-attr]
        )
