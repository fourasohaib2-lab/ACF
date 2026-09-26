"""Convective rule calibration against METAR: stricter candidate rules, ETS under a bias constraint."""

import numpy as np
import pytest

from acf.awci.ops.calibration_convection import ConvectiveSample, candidate_rules, evaluate, select_rule


def _sample() -> ConvectiveSample:
    # 8 pairs: current rule (class >= TCU) fires on 6, observations show convection on 2 of them
    return ConvectiveSample(
        observed=np.array([1, 1, 0, 0, 0, 0, 0, 1], bool),
        base=np.array([1, 1, 1, 1, 1, 1, 0, 0], bool),
        predictors={"mucape": np.array([900, 300, 150, 120, 800, 200, 50, 1200.0]),
                    "precip_rate": np.array([1.2, 0.3, 0.0, 0.0, 0.0, 0.05, 0.0, 2.0])},
    )


def test_baseline_rule_reproduces_the_current_diagnosis() -> None:
    s = evaluate(_sample(), {})
    assert (s["a"], s["b"], s["c"], s["d"]) == (2, 4, 1, 1)
    assert s["bias"] == pytest.approx(2.0)


def test_a_stricter_rule_only_removes_forecasts() -> None:
    s = evaluate(_sample(), {"precip_rate": (">=", 0.1)})
    assert (s["a"], s["b"], s["c"], s["d"]) == (2, 0, 1, 5)  # both false alarms without rain removed


def test_selection_maximises_ets_within_the_bias_range_and_prefers_the_simplest() -> None:
    rules = [{}, {"mucape": (">=", 250.0)}, {"precip_rate": (">=", 0.1)},
             {"precip_rate": (">=", 0.1), "mucape": (">=", 250.0)}]
    best, table = select_rule(_sample(), rules, bias_range=(0.5, 1.5))
    assert best == {"precip_rate": (">=", 0.1)}  # same ETS as the 2-condition rule, fewer conditions
    assert len(table) == 4 and table[0]["rule"] == {}


def test_no_rule_within_the_bias_range_raises() -> None:
    with pytest.raises(ValueError):
        select_rule(_sample(), [{}], bias_range=(0.8, 1.2))


def test_candidate_grid_is_small_and_physically_labelled() -> None:
    rules = candidate_rules()
    assert {} in rules and len(rules) < 200
    from acf.awci.ops.cloud_profile import _REALISED
    assert all(set(r) <= set(_REALISED) for r in rules)  # only conditions the diagnosis can apply
