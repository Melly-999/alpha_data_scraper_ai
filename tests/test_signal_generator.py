from signal_generator import SignalGenerator


def _signal_cfg():
    return {
        "slope_threshold": 0.7,
        "trend_slope_threshold": 1.3,
        "rsi_buy_max": 67,
        "rsi_sell_min": 33,
        "stoch_buy_max": 72,
        "stoch_sell_min": 28,
        "bb_buy_max": 38,
        "bb_sell_min": -38,
        "weights": {
            "slope": 0.28,
            "rsi": 0.22,
            "stochastic": 0.18,
            "lstm": 0.18,
            "bb": 0.14,
        },
    }


def test_buy_signal_skeleton():
    sg = SignalGenerator(_signal_cfg())
    signal, hold = sg.generate_signal(
        price_slope=1.0,
        rsi=30,
        stoch_k=20,
        bb_pos=-50,
        lstm_dir=1,
    )

    assert signal == "BUY"
    assert hold in ("TREND (minuty)", "SCALPING (sekundy)")


def test_confidence_range_skeleton():
    sg = SignalGenerator(_signal_cfg())
    conf = sg.compute_confidence(
        price_slope=1.0,
        rsi=30,
        stoch_k=20,
        lstm_dir=1,
        bb_pos=-50,
    )

    assert 33 <= conf <= 85
