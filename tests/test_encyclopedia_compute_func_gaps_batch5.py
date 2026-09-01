"""
Regression tests for a fifth (small) batch of EncyclopediaEntry
compute_func gaps found by the repo-wide AST scan.
"""

import pytest

from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_green_ampt_infiltration_rate():
    law = EncyclopediaRegistry.get("green_ampt_infiltration_model")
    assert law.calculate(
        saturated_hydraulic_conductivity=10.0, wetting_front_suction=100.0,
        moisture_deficit=0.3, cumulative_infiltration=50.0,
    ) == pytest.approx(16.0)
    with pytest.raises(ValueError):
        law.calculate(
            saturated_hydraulic_conductivity=10.0, wetting_front_suction=100.0,
            moisture_deficit=0.3, cumulative_infiltration=0.0,
        )


def test_graupel_ice_collision_charging_rate_is_always_non_negative():
    law = EncyclopediaRegistry.get("graupel_ice_collision_charging")
    value = law.calculate(
        graupel_concentration=100.0, ice_concentration=1000.0, collision_cross_section=1e-6,
        relative_velocity=3.0, charge_transfer=1e-15,
    )
    assert value == pytest.approx(3e-16)
    # A negative relative velocity (ice falling faster than graupel) must
    # still yield a non-negative charging rate - collision rate can't be
    # negative regardless of which hydrometeor falls faster.
    value_reversed = law.calculate(
        graupel_concentration=100.0, ice_concentration=1000.0, collision_cross_section=1e-6,
        relative_velocity=-3.0, charge_transfer=1e-15,
    )
    assert value_reversed == pytest.approx(value)
