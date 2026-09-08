"""
Tests for acf.science.ensemble_uncertainty.
"""

import pytest

from acf.science.ensemble_uncertainty import ConsensusResult, EnsembleMember, EnsembleRun, UncertaintyEstimate


def _run(values: list[float]) -> EnsembleRun:
    return EnsembleRun(variable="T2m", members=[EnsembleMember(f"m{i}", v) for i, v in enumerate(values)])


def test_mean():
    run = _run([10.0, 20.0, 30.0])
    assert run.mean() == pytest.approx(20.0)


def test_mean_empty_raises():
    with pytest.raises(ValueError):
        EnsembleRun(variable="T2m").mean()


def test_spread_zero_for_identical_members():
    run = _run([15.0, 15.0, 15.0])
    assert run.spread() == pytest.approx(0.0)


def test_spread_positive_for_varying_members():
    run = _run([10.0, 20.0, 30.0])
    assert run.spread() > 0


def test_spread_requires_two_members():
    run = _run([10.0])
    with pytest.raises(ValueError):
        run.spread()


def test_percentile_median():
    run = _run([10.0, 20.0, 30.0, 40.0, 50.0])
    assert run.percentile(50.0) == pytest.approx(30.0)


def test_probability_exceeding():
    run = _run([1.0, 2.0, 3.0, 4.0, 5.0])
    assert run.probability_exceeding(3.0) == pytest.approx(2 / 5)


def test_probability_exceeding_none_exceed():
    run = _run([1.0, 2.0, 3.0])
    assert run.probability_exceeding(100.0) == 0.0


def test_probability_exceeding_all_exceed():
    run = _run([10.0, 20.0, 30.0])
    assert run.probability_exceeding(1.0) == 1.0


def test_uncertainty_estimate_from_ensemble():
    run = _run([10.0, 20.0, 30.0, 40.0, 50.0])
    est = UncertaintyEstimate.from_ensemble(run)
    assert est.mean == pytest.approx(30.0)
    assert est.p50 == pytest.approx(30.0)
    assert est.p10 < est.p50 < est.p90


def test_consensus_high_confidence_tight_ensemble():
    run = _run([20.0, 20.5, 19.5, 20.2, 19.8])
    result = ConsensusResult.from_ensemble(run, agreement_tolerance=1.0)
    assert result.recommendation == "High confidence"
    assert result.agreement_fraction == pytest.approx(1.0)


def test_consensus_low_confidence_divergent_ensemble():
    run = _run([0.0, 50.0, -50.0, 100.0, -100.0])
    result = ConsensusResult.from_ensemble(run, agreement_tolerance=1.0)
    assert result.recommendation == "Low confidence / divergent"


def test_consensus_invalid_negative_tolerance():
    run = _run([1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        ConsensusResult.from_ensemble(run, agreement_tolerance=-1.0)
