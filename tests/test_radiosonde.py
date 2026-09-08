"""
Tests for acf.science.radiosonde.
"""

import pytest

from acf.science.radiosonde import SoundingLevel, SoundingProfile


def _sample_profile() -> SoundingProfile:
    levels = [
        SoundingLevel(pressure_hpa=1000.0, height_m=110.0, temperature_c=25.0, dewpoint_c=18.0),
        SoundingLevel(pressure_hpa=925.0, height_m=750.0, temperature_c=20.0, dewpoint_c=15.0),
        SoundingLevel(pressure_hpa=850.0, height_m=1460.0, temperature_c=15.0, dewpoint_c=10.0),
        SoundingLevel(pressure_hpa=700.0, height_m=3010.0, temperature_c=5.0, dewpoint_c=-2.0),
        SoundingLevel(pressure_hpa=500.0, height_m=5700.0, temperature_c=-15.0, dewpoint_c=-25.0),
        SoundingLevel(pressure_hpa=300.0, height_m=9200.0, temperature_c=-45.0, dewpoint_c=-55.0),
    ]
    return SoundingProfile(levels)


def test_profile_requires_at_least_two_levels():
    with pytest.raises(ValueError):
        SoundingProfile([SoundingLevel(1000.0, 0.0, 20.0, 15.0)])


def test_profile_requires_decreasing_pressure():
    with pytest.raises(ValueError):
        SoundingProfile(
            [
                SoundingLevel(pressure_hpa=900.0, height_m=0.0, temperature_c=20.0, dewpoint_c=15.0),
                SoundingLevel(pressure_hpa=1000.0, height_m=500.0, temperature_c=15.0, dewpoint_c=10.0),
            ]
        )


def test_interpolate_at_pressure_matches_exact_level():
    profile = _sample_profile()
    lvl = profile.interpolate_at_pressure(850.0)
    assert lvl.temperature_c == pytest.approx(15.0)
    assert lvl.dewpoint_c == pytest.approx(10.0)


def test_interpolate_at_pressure_between_levels():
    profile = _sample_profile()
    lvl = profile.interpolate_at_pressure(900.0)
    # Between 925hPa(T=20) and 850hPa(T=15) -> interpolated T should be
    # strictly between the two, closer to neither extreme trivially.
    assert 15.0 < lvl.temperature_c < 20.0
    assert 750.0 < lvl.height_m < 1460.0


def test_interpolate_out_of_range_raises():
    profile = _sample_profile()
    with pytest.raises(ValueError):
        profile.interpolate_at_pressure(50.0)
    with pytest.raises(ValueError):
        profile.interpolate_at_pressure(1050.0)


def test_potential_temperature_profile_increases_with_height_for_stable_profile():
    profile = _sample_profile()
    theta = profile.potential_temperature_profile()
    assert all(theta[i] < theta[i + 1] for i in range(len(theta) - 1))


def test_relative_humidity_profile_bounded():
    profile = _sample_profile()
    rh = profile.relative_humidity_profile()
    assert all(0.0 <= v <= 1.0 for v in rh)


def test_precipitable_water_positive_and_reasonable():
    profile = _sample_profile()
    pwat = profile.precipitable_water_mm()
    # Typical range for a moist mid-latitude sounding: a few mm to ~60mm.
    assert 5.0 < pwat < 80.0


def test_surface_based_parcel_indices_includes_ki_tt_when_levels_present():
    profile = _sample_profile()
    indices = profile.surface_based_parcel_indices()
    assert "lcl_height_m" in indices
    assert "surface_theta_e_k" in indices
    assert "precipitable_water_mm" in indices
    assert "k_index" in indices
    assert "total_totals" in indices
    assert indices["lcl_height_m"] > 0


def test_surface_based_parcel_indices_omits_ki_tt_when_levels_missing():
    # A profile that never reaches 500hPa can't compute KI/TT.
    levels = [
        SoundingLevel(pressure_hpa=1000.0, height_m=110.0, temperature_c=25.0, dewpoint_c=18.0),
        SoundingLevel(pressure_hpa=900.0, height_m=980.0, temperature_c=18.0, dewpoint_c=13.0),
    ]
    profile = SoundingProfile(levels)
    indices = profile.surface_based_parcel_indices()
    assert "k_index" not in indices
    assert "total_totals" not in indices
    assert "lcl_height_m" in indices  # still computable from surface alone
