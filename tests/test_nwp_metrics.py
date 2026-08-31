"""
Unit test suite for NWPVerificationMetrics (ACF-NWP-001).
"""

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
