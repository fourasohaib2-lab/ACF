"""
Tests for acf.science.stability.Stability (facade over existing,
individually-tested stability modules — no new formulas here).
"""

import pytest

from acf.science.stability import Stability


def test_lcl_height_espy_matches_underlying_module():
    from acf.science.lcl import LCL

    assert Stability.lcl_height_espy(30.0, 20.0) == LCL.calculate(30.0, 20.0)


def test_lcl_height_bolton_matches_underlying_module():
    from acf.science.lcl import LCL

    assert Stability.lcl_height_bolton(303.15, 293.15) == LCL.calculate_bolton(303.15, 293.15)


def test_lifted_index():
    assert Stability.lifted_index(parcel_temperature_500=-10.0, environment_temperature_500=-15.0) == -5.0


def test_showalter_index():
    assert Stability.showalter_index(parcel_temperature_500=-10.0, environment_temperature_500=-15.0) == -5.0


def test_k_index():
    ki = Stability.k_index(t850=20.0, t700=10.0, t500=-10.0, td850=15.0, td700=5.0)
    assert ki > 0


def test_total_totals():
    tt = Stability.total_totals(t850=20.0, td850=15.0, t500=-10.0)
    assert tt == 20.0 + 15.0 - (2 * -10.0)


def test_sweat_index():
    sweat = Stability.sweat_index(td850=18, tt=52, wind850=25, wind500=50, dir850=170, dir500=240)
    assert sweat > 0


def test_calculate_cape_for_parcel_all_types_give_same_formula():
    kwargs = dict(
        parcel_temperature=[22, 18, 14],
        environment_temperature=[20, 16, 13],
        height=[0, 1000, 2000],
    )
    sb = Stability.calculate_cape_for_parcel("surface_based", **kwargs)
    ml = Stability.calculate_cape_for_parcel("mixed_layer", **kwargs)
    mu = Stability.calculate_cape_for_parcel("most_unstable", **kwargs)
    assert sb == ml == mu
    assert sb > 0


def test_calculate_cape_for_parcel_rejects_unknown_type():
    with pytest.raises(ValueError):
        Stability.calculate_cape_for_parcel(
            "not_a_real_parcel_type",
            parcel_temperature=[22, 18],
            environment_temperature=[20, 16],
            height=[0, 1000],
        )


def test_cin():
    cin = Stability.cin(
        parcel_temperature=[18, 15, 10],
        environment_temperature=[20, 17, 12],
        height=[0, 1000, 2000],
    )
    assert cin > 0


def test_srh_layer_and_profile_consistency():
    single = Stability.storm_relative_helicity_layer(u=20, v=10, storm_u=10, storm_v=5, du=3, dv=4)
    profile = Stability.storm_relative_helicity_profile(u=[20, 23], v=[10, 14], storm_u=10, storm_v=5)
    assert single == pytest.approx(profile)
