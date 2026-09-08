"""
Tests for acf.science.fronts.
"""

import pytest

from acf.science.fronts import AirMass, FrontMovement, FrontType


def test_air_mass_all_6_standard_types():
    assert AirMass.classify_by_source_region("continental", "arctic") == "cA"
    assert AirMass.classify_by_source_region("continental", "polar") == "cP"
    assert AirMass.classify_by_source_region("maritime", "polar") == "mP"
    assert AirMass.classify_by_source_region("continental", "tropical") == "cT"
    assert AirMass.classify_by_source_region("maritime", "tropical") == "mT"
    assert AirMass.classify_by_source_region("maritime", "equatorial") == "mE"


def test_air_mass_invalid_combination():
    with pytest.raises(ValueError):
        AirMass.classify_by_source_region("continental", "equatorial")


def test_air_mass_description():
    assert "sec" in AirMass.description("cA")


def test_air_mass_description_invalid_code():
    with pytest.raises(ValueError):
        AirMass.description("xx")


def test_occlusion_cold_type():
    result = FrontType.classify_occlusion(
        temperature_behind_cold_front_c=-5.0, temperature_ahead_of_warm_front_c=2.0
    )
    assert result == FrontType.OCCLUDED_COLD_TYPE


def test_occlusion_warm_type():
    result = FrontType.classify_occlusion(
        temperature_behind_cold_front_c=3.0, temperature_ahead_of_warm_front_c=-2.0
    )
    assert result == FrontType.OCCLUDED_WARM_TYPE


def test_front_speed_directly_perpendicular_full_speed():
    # Front oriented E-W (0 deg), normal is 90 deg (due east); wind
    # from due west (270 deg, i.e. blowing eastward) should give full
    # speed advancing perpendicular to the front.
    speed = FrontMovement.speed(wind_speed_m_s=10.0, wind_direction_deg=270.0, front_orientation_deg=0.0)
    assert speed == pytest.approx(10.0, abs=1e-6)


def test_front_speed_parallel_wind_gives_zero():
    # Wind blowing exactly along the front-normal + 90 (i.e. parallel
    # to the front) contributes zero to front-normal movement.
    speed = FrontMovement.speed(wind_speed_m_s=10.0, wind_direction_deg=0.0, front_orientation_deg=0.0)
    assert speed == pytest.approx(0.0, abs=1e-6)


def test_front_speed_invalid_negative_wind():
    with pytest.raises(ValueError):
        FrontMovement.speed(wind_speed_m_s=-5.0, wind_direction_deg=90.0, front_orientation_deg=0.0)
