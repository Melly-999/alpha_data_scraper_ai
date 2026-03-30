import os
import logging

import numpy as np
try:
    import torch
    import torch.nn as nn
except ImportError:
    torch = None
    nn = None

logger = logging.getLogger("GrokAlpha")


if nn is not None:
    class MultiFeatureLSTM(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers, dropout):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size, hidden_size, num_layers, batch_first=True, dropout=dropout
            )
            self.fc = nn.Linear(hidden_size, 1)

        def forward(self, x):
            out, _ = self.lstm(x)
            return self.fc(out[:, -1, :])
else:
    class MultiFeatureLSTM:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Torch is required for MultiFeatureLSTM")


class LSTMModel:
    """LSTM model for price direction prediction."""

    def __init__(self, input_size=2, hidden_size=64, num_layers=3, dropout=0.15):
        self.torch_available = torch is not None
        if self.torch_available:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = MultiFeatureLSTM(
                input_size, hidden_size, num_layers, dropout
            ).to(self.device)
            self.model.eval()
        else:
            self.device = None
            self.model = None
            logger.warning("Torch not installed; LSTM predictions disabled.")
        self.trained = False

    def load_checkpoint(self, path):
        if not self.torch_available:
            logger.warning("Skipping checkpoint load because torch is unavailable.")
            return
        if os.path.exists(path):
            try:
                checkpoint = torch.load(path, map_location=self.device, weights_only=True)
                self.model.load_state_dict(checkpoint["model_state_dict"])
                self.trained = True
                logger.info("LSTM checkpoint loaded from %s", path)
            except Exception as exc:
                logger.warning("Failed to load checkpoint: %s", exc)
        else:
            logger.warning("No LSTM checkpoint found. Model will use random weights.")

    def predict(self, price_seq, rsi_seq):
        """
        price_seq: numpy array of last N prices
        rsi_seq: numpy array of last N RSI values
        Returns predicted price (float) or None.
        """
        if not self.torch_available:
            return None
        if not self.trained or len(price_seq) != len(rsi_seq):
            return None

        seq = np.column_stack((price_seq, rsi_seq))
        if np.isnan(seq).any() or np.isinf(seq).any():
            return None

        seq = (seq - seq.mean(axis=0)) / (seq.std(axis=0) + 1e-8)
        seq_tensor = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            pred = self.model(seq_tensor).item()
        return pred
