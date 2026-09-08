"""
Unit test suite for NWPVerificationMetrics (ACF-NWP-001).
"""

import pytest

from acf.verification.nwp_metrics import NWPVerificationMetrics


def test_continuous_metrics():
    """Test RMSE, BIAS, MAE, ACC calculations."""
    fcst = [10.0, 20.0, 30.0, 40.0]
    obs = [10.0, 20.0, 30.0, 40.0]

    assert NWPVerificationMetrics.rmse(fcst, obs) == 0.0
    assert NWPVerificationMetrics.bias(fcst, obs) == 0.0
    assert NWPVerificationMetrics.mae(fcst, obs) == 0.0
    assert NWPVerificationMetrics.acc(fcst, obs) == 1.0


def test_categorical_metrics():
    """Test POD, FAR, CSI, ETS calculations."""
    fcst = [5.0, 15.0, 2.0, 20.0]
    obs = [4.0, 12.0, 8.0, 18.0]
    threshold = 10.0

    eval_res = NWPVerificationMetrics.evaluate_all(fcst, obs, threshold=threshold)

    assert "rmse" in eval_res
    assert "pod" in eval_res
    assert "far" in eval_res
    assert "csi" in eval_res
    assert "ets" in eval_res
    assert 0.0 <= eval_res["pod"] <= 1.0
    assert 0.0 <= eval_res["far"] <= 1.0


def test_contingency_table_rejects_mismatched_lengths():
    """CORRECTED: used to silently truncate to the shorter sequence
    (zip strict=False) instead of raising, unlike every continuous
    metric in this class which explicitly guards against this."""
    with pytest.raises(ValueError):
        NWPVerificationMetrics.contingency_table([1.0, 2.0, 3.0], [1.0, 2.0], threshold=1.5)


# ------------------------------------------------- brier_score (§39)


def test_brier_score_matches_a_hand_computed_reference():
    """0.9/1, 0.1/0, 0.8/1 -> ((0.1)^2 + (0.1)^2 + (0.2)^2) / 3 = 0.02
    exactly - a real, independently hand-verified value."""
    forecasts = [0.9, 0.1, 0.8]
    observations = [1, 0, 1]
    assert NWPVerificationMetrics.brier_score(forecasts, observations) == pytest.approx(0.02)


def test_brier_score_is_zero_for_a_perfect_forecast():
    assert NWPVerificationMetrics.brier_score([1.0, 0.0, 1.0], [1, 0, 1]) == 0.0


def test_brier_score_is_one_for_the_worst_possible_forecast():
    assert NWPVerificationMetrics.brier_score([0.0, 1.0], [1, 0]) == 1.0


def test_brier_score_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        NWPVerificationMetrics.brier_score([0.5], [1, 0])


def test_brier_score_rejects_empty_sequences():
    with pytest.raises(ValueError, match="not be empty"):
        NWPVerificationMetrics.brier_score([], [])


# ---------------------------------------------------- roc_auc (§39)


def test_roc_auc_matches_a_hand_computed_pairwise_reference():
    """scores=[0.1, 0.4, 0.35, 0.8], labels=[0, 0, 1, 1] - real
    pairwise check (definition: fraction of (positive, negative) pairs
    where positive > negative): (0.35,0.1)=1, (0.35,0.4)=0, (0.8,0.1)=1,
    (0.8,0.4)=1 -> 3/4 = 0.75 exactly, independently verified by hand,
    not derived from this module's own rank-based implementation."""
    scores = [0.1, 0.4, 0.35, 0.8]
    labels = [0, 0, 1, 1]
    assert NWPVerificationMetrics.roc_auc(scores, labels) == pytest.approx(0.75)


def test_roc_auc_is_one_for_perfect_separation():
    scores = [0.1, 0.2, 0.8, 0.9]
    labels = [0, 0, 1, 1]
    assert NWPVerificationMetrics.roc_auc(scores, labels) == pytest.approx(1.0)


def test_roc_auc_is_zero_for_perfectly_backwards_separation():
    scores = [0.9, 0.8, 0.2, 0.1]
    labels = [0, 0, 1, 1]
    assert NWPVerificationMetrics.roc_auc(scores, labels) == pytest.approx(0.0)


def test_roc_auc_is_half_when_every_score_ties():
    """All scores identical - no real discrimination, the same result
    a random guess would achieve on average - the real tie-correction
    (averaged ranks) must produce exactly 0.5, not an arbitrary value."""
    scores = [0.5, 0.5, 0.5, 0.5]
    labels = [0, 1, 0, 1]
    assert NWPVerificationMetrics.roc_auc(scores, labels) == pytest.approx(0.5)


def test_roc_auc_rejects_no_positive_observations():
    with pytest.raises(ValueError, match="positive"):
        NWPVerificationMetrics.roc_auc([0.1, 0.9], [0, 0])


def test_roc_auc_rejects_no_negative_observations():
    with pytest.raises(ValueError, match="negative"):
        NWPVerificationMetrics.roc_auc([0.1, 0.9], [1, 1])


def test_roc_auc_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        NWPVerificationMetrics.roc_auc([0.5], [1, 0])


def test_roc_auc_rejects_empty_sequences():
    with pytest.raises(ValueError, match="not be empty"):
        NWPVerificationMetrics.roc_auc([], [])
