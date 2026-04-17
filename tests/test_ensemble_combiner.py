"""
test_ensemble_combiner.py
─────────────────────────────────────────────────────────────────────
pytest test_ensemble_combiner.py -v

Covers:
  - Agreement / disagreement direction voting
  - LSTM unavailable → 100% technical, NO regime penalty (fix #14)
  - Uncertainty penalty curve + floor
  - Regime penalty applied only when LSTM available
  - Min-confidence threshold
  - LSTM HOLD handling
  - Internal _vote_direction
"""

import pytest
from ensemble_combiner import (
    EnsembleCombiner,
    LSTM_BASE_WEIGHT,
    LSTM_WEIGHT_FLOOR,
    TechnicalSignal,
    _compute_weights,
    _vote_direction,
)
from lstm_signal_adapter import LSTMSignal


# ─── Helpers ─────────────────────────────────────────────────────────


def make_tech(direction="BUY", confidence=80.0, sl=1.0950, tp=1.1050):
    return TechnicalSignal(direction=direction, confidence=confidence, sl=sl, tp=tp)


def make_lstm(
    direction="BUY",
    confidence=85.0,
    uncertainty=0.1,
    regime="TRENDING",
    available=True,
):
    return LSTMSignal(
        direction=direction,
        confidence=confidence,
        lstm_delta=0.0005,
        lstm_uncertainty=uncertainty,
        regime=regime,
        score=3,
        reasons=["LSTM reason 1", "LSTM reason 2"],
        available=available,
    )


@pytest.fixture
def combiner():
    return EnsembleCombiner()


# ─── Agreement ───────────────────────────────────────────────────────


class TestAgreement:
    def test_both_buy_trending(self, combiner):
        result = combiner.combine(make_tech("BUY", 80), make_lstm("BUY", 85))
        assert result.direction == "BUY"
        assert not result.blocked
        assert result.confidence == pytest.approx(82.5, abs=0.1)

    def test_both_sell_trending(self, combiner):
        result = combiner.combine(make_tech("SELL", 80), make_lstm("SELL", 90))
        assert result.direction == "SELL"
        assert not result.blocked
        assert result.confidence == pytest.approx(85.0, abs=0.1)

    def test_preserves_tech_sl_tp(self, combiner):
        tech = make_tech("BUY", 80, sl=1.0900, tp=1.1100)
        result = combiner.combine(tech, make_lstm("BUY", 85))
        assert result.sl == 1.0900
        assert result.tp == 1.1100


# ─── Disagreement ────────────────────────────────────────────────────


class TestDisagreement:
    def test_lstm_stronger_wins(self, combiner):
        result = combiner.combine(make_tech("BUY", 70), make_lstm("SELL", 95))
        assert result.direction == "SELL"

    def test_tech_stronger_wins(self, combiner):
        result = combiner.combine(make_tech("BUY", 95), make_lstm("SELL", 60))
        assert result.direction == "BUY"


# ─── LSTM Unavailable (fix #14) ─────────────────────────────────────


class TestLSTMUnavailable:
    def test_full_technical_weight(self, combiner):
        lstm = make_lstm(available=False, regime="UNKNOWN")
        result = combiner.combine(make_tech("BUY", 85), lstm)
        assert result.lstm_weight == 0.0
        assert result.technical_weight == 1.0

    def test_no_regime_penalty_when_unavailable(self, combiner):
        """FIX #14: UNKNOWN regime should NOT penalise pure-technical signals."""
        lstm = make_lstm(available=False, regime="UNKNOWN")
        result = combiner.combine(make_tech("BUY", 85), lstm)
        # regime_mult = 1.0 (not 0.90) → confidence = 85.0
        assert result.confidence == pytest.approx(85.0, abs=0.1)

    def test_reason_logged(self, combiner):
        result = combiner.combine(make_tech("BUY", 85), make_lstm(available=False))
        assert any("unavailable" in r.lower() for r in result.reasons)


# ─── Uncertainty Penalty ─────────────────────────────────────────────


class TestUncertaintyPenalty:
    def test_low_no_penalty(self, combiner):
        result = combiner.combine(
            make_tech("BUY", 80), make_lstm("BUY", 85, uncertainty=0.1)
        )
        assert result.lstm_weight == LSTM_BASE_WEIGHT

    def test_at_threshold_no_penalty(self, combiner):
        result = combiner.combine(
            make_tech("BUY", 80), make_lstm("BUY", 85, uncertainty=0.30)
        )
        assert result.lstm_weight == LSTM_BASE_WEIGHT

    def test_high_reduces_weight(self, combiner):
        result = combiner.combine(
            make_tech("BUY", 80), make_lstm("BUY", 85, uncertainty=0.6)
        )
        # penalty = (0.6-0.3)*2 = 0.6 → weight = max(0.1, 0.5-0.6) = 0.1
        assert result.lstm_weight == pytest.approx(LSTM_WEIGHT_FLOOR, abs=0.01)

    def test_extreme_floored(self, combiner):
        result = combiner.combine(
            make_tech("BUY", 80), make_lstm("BUY", 85, uncertainty=0.99)
        )
        assert result.lstm_weight >= LSTM_WEIGHT_FLOOR


# ─── Regime Penalty ──────────────────────────────────────────────────


class TestRegimePenalty:
    @pytest.mark.parametrize(
        "regime,mult",
        [
            ("TRENDING", 1.00),
            ("RANGING", 0.90),
            ("VOLATILE", 0.80),
            ("UNKNOWN", 0.90),
        ],
    )
    def test_multiplier_when_lstm_available(self, combiner, regime, mult):
        result = combiner.combine(
            make_tech("BUY", 80), make_lstm("BUY", 80, regime=regime)
        )
        assert result.confidence == pytest.approx(80 * mult, abs=0.1)

    def test_volatile_blocks_marginal(self, combiner):
        result = combiner.combine(
            make_tech("BUY", 86), make_lstm("BUY", 86, regime="VOLATILE")
        )
        # 86 * 0.80 = 68.8 < 70
        assert result.blocked
        assert "Confidence" in result.block_reason


# ─── Min Confidence ──────────────────────────────────────────────────


class TestMinConfidence:
    def test_below_blocked(self, combiner):
        result = combiner.combine(make_tech("BUY", 60), make_lstm("BUY", 60))
        assert result.blocked

    def test_at_threshold_emits(self, combiner):
        result = combiner.combine(
            make_tech("BUY", 70), make_lstm("BUY", 70, regime="TRENDING")
        )
        assert not result.blocked

    def test_block_reason_has_pct(self, combiner):
        result = combiner.combine(make_tech("BUY", 50), make_lstm("BUY", 50))
        assert "%" in result.block_reason


# ─── LSTM HOLD ───────────────────────────────────────────────────────


class TestLSTMHold:
    def test_lstm_hold_mild_push(self, combiner):
        result = combiner.combine(make_tech("BUY", 85), make_lstm("HOLD", 50))
        # Tech should still dominate; direction is BUY or HOLD
        assert result.direction in ("BUY", "HOLD")


# ─── Weight Calculation ─────────────────────────────────────────────


class TestComputeWeights:
    def test_unavailable_returns_zero_one(self):
        reasons = []
        lw, tw = _compute_weights(make_lstm(available=False), reasons)
        assert lw == 0.0
        assert tw == 1.0

    def test_available_sums_to_one(self):
        reasons = []
        lw, tw = _compute_weights(make_lstm(uncertainty=0.5), reasons)
        assert lw + tw == pytest.approx(1.0)


# ─── Vote Direction ──────────────────────────────────────────────────


class TestVoteDirection:
    def test_agreement_sums(self):
        d = _vote_direction(make_tech("BUY", 80), make_lstm("BUY", 90), 0.5, 0.5)
        assert d == "BUY"

    def test_unavailable_no_contribution(self):
        d = _vote_direction(
            make_tech("BUY", 80), make_lstm("BUY", 90, available=False), 1.0, 0.0
        )
        assert d == "BUY"
