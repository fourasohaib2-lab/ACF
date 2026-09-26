import numpy as np
import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.ops.engine import (
    DEFAULT_OPERATIONAL_PROFILE_PATH,
    combine,
    legacy_module_scores,
    legacy_profile,
    level_codes,
    load_profile,
    operational_module_scores,
)

RNG = np.random.default_rng(7)
N = 10_000
INPUTS = {
    "temperature": RNG.uniform(220.0, 320.0, N),
    "specific_humidity": RNG.uniform(0.0, 0.03, N),
    "wind_speed": RNG.uniform(0.0, 70.0, N),
    "cape": RNG.uniform(0.0, 6000.0, N),
    "cin": RNG.uniform(-600.0, 0.0, N),
    "precipitation": RNG.uniform(0.0, 60.0, N),
    "pressure": RNG.uniform(100.0, 1030.0, N),
    "altitude": RNG.uniform(-100.0, 4000.0, N),
    "confidence": RNG.uniform(0.0, 100.0, N),
    "temporal_change": RNG.uniform(0.0, 25.0, N),
}


def test_legacy_module_scores_match_calculator() -> None:
    calc = AWCICalculator()
    scores = legacy_module_scores(INPUTS)
    for idx in range(0, N, 97):
        point = {key: float(values[idx]) for key, values in INPUTS.items()}
        expected = calc.calculate_module_scores(point)
        for module, value in expected.items():
            assert scores[module][idx] == pytest.approx(value, abs=1e-12)


def test_legacy_composite_matches_calculator_after_its_rounding() -> None:
    calc = AWCICalculator()
    result = combine(legacy_module_scores(INPUTS), legacy_profile())
    for idx in range(0, N, 97):
        point = {key: float(values[idx]) for key, values in INPUTS.items()}
        assert abs(result.awci[idx] - calc.calculate(point)["awci"]) <= 0.05 + 1e-9


def test_operational_profile_file_is_valid() -> None:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    assert profile.name == "operational-v1"
    assert sum(profile.weights.values()) == pytest.approx(1.0)
    assert profile.min_present_weight == 0.5


def _op_scores(theta_e: float) -> dict:
    one = lambda x: np.array([x])  # noqa: E731
    return operational_module_scores(
        wind_speed=one(25.0), layer_shear=one(10.0), theta_e=one(theta_e), mucape=one(1000.0),
        precip_rate=one(5.0), ptype_severity=one(0.2), elevation=one(300.0),
    )


def test_missing_module_is_renormalized_never_zero() -> None:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    full = combine(_op_scores(330.0), profile)
    missing = combine(_op_scores(np.nan), profile)
    assert np.isnan(missing.decomposition["thermodynamic"][0])
    assert missing.present_weight[0] == pytest.approx(full.present_weight[0] - 0.25)
    assert missing.awci[0] > 0.0 and np.isfinite(missing.awci[0])
    assert _op_scores(330.0)["temporal"] is None and _op_scores(330.0)["confidence"] is None


def test_insufficient_data_gives_null_awci() -> None:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    nan = np.array([np.nan])
    scores = operational_module_scores(
        wind_speed=nan, layer_shear=nan, theta_e=nan, mucape=nan,
        precip_rate=np.array([1.0]), ptype_severity=np.array([0.2]), elevation=np.array([10.0]),
    )
    assert np.isnan(combine(scores, profile).awci[0])


def test_level_codes_use_calculator_thresholds() -> None:
    codes = level_codes(np.array([10.0, 20.0, 49.9, 90.0, np.nan]), legacy_profile())
    np.testing.assert_array_equal(codes, [0, 1, 2, 5, -1])
