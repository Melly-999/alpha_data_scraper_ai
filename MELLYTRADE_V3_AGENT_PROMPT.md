Use this prompt with Codex / Claude Code inside the target repo:

Open this repository and integrate the MellyTrade v3 folders already copied in. Preserve existing files. Then:
1. Wire any existing alpha_data_scraper_ai LSTM pipeline into `mt5/lstm_signal_adapter.py` by setting the correct import path and adapting the output to the `LSTMSignal` dataclass.
2. Ensure FastAPI `/signal` forwards accepted signals to the Cloudflare Worker `/api/publish` endpoint.
3. Add or update tests for API validation and DB logging.
4. Do not loosen risk rules: max 1% risk, min confidence 70, SL/TP mandatory.
