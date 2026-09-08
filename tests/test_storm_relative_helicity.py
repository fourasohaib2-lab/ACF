import pytest

from acf.science.storm_relative_helicity import (
    StormRelativeHelicity,
)


def test_srh():

    value = StormRelativeHelicity.calculate(
        u=20,
        v=10,
        storm_u=10,
        storm_v=5,
        du=3,
        dv=4,
    )

    assert value == pytest.approx(25)


def test_srh_profile_matches_single_layer_for_two_levels():
    # A 2-level profile should reduce exactly to the single-layer formula.
    single = StormRelativeHelicity.calculate(u=20, v=10, storm_u=10, storm_v=5, du=3, dv=4)
    profile = StormRelativeHelicity.calculate_profile(u=[20, 23], v=[10, 14], storm_u=10, storm_v=5)
    assert profile == pytest.approx(single)


def test_srh_profile_sums_multiple_layers():
    # 3 levels = 2 layers; total SRH should equal sum of each layer's
    # single-layer contribution computed independently.
    u = [20.0, 23.0, 25.0]
    v = [10.0, 14.0, 12.0]
    storm_u, storm_v = 10.0, 5.0

    layer1 = StormRelativeHelicity.calculate(
        u=u[0], v=v[0], storm_u=storm_u, storm_v=storm_v, du=u[1] - u[0], dv=v[1] - v[0]
    )
    layer2 = StormRelativeHelicity.calculate(
        u=u[1], v=v[1], storm_u=storm_u, storm_v=storm_v, du=u[2] - u[1], dv=v[2] - v[1]
    )

    profile = StormRelativeHelicity.calculate_profile(u=u, v=v, storm_u=storm_u, storm_v=storm_v)
    assert profile == pytest.approx(layer1 + layer2)


def test_srh_profile_invalid_length_mismatch():
    with pytest.raises(ValueError):
        StormRelativeHelicity.calculate_profile(u=[1, 2, 3], v=[1, 2], storm_u=0, storm_v=0)


def test_srh_profile_invalid_too_few_levels():
    with pytest.raises(ValueError):
        StormRelativeHelicity.calculate_profile(u=[1], v=[1], storm_u=0, storm_v=0)


def test_category():

    assert StormRelativeHelicity.category(50) == "Weak"

    assert StormRelativeHelicity.category(150) == "Moderate"

    assert StormRelativeHelicity.category(300) == "Strong"

    assert StormRelativeHelicity.category(500) == "Extreme"
