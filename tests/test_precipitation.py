"""
Tests for acf.science.precipitation.
"""

import pytest

from acf.science.precipitation import EchoTop, HydrometeorType, PrecipitationIntensity, VIL


def test_vil_layer_density_known_relation():
    m = VIL.layer_liquid_water_density(20000.0)
    assert m == pytest.approx(3.44e-6 * 20000.0 ** (4.0 / 7.0))


def test_vil_layer_density_invalid_negative():
    with pytest.raises(ValueError):
        VIL.layer_liquid_water_density(-1.0)


def test_vil_calculate_positive():
    vil = VIL.calculate(
        reflectivity_profile_mm6_m3=[10000.0, 30000.0, 15000.0, 0.0],
        height_profile_m=[0.0, 2000.0, 4000.0, 6000.0],
    )
    assert vil > 0


def test_vil_calculate_invalid_length_mismatch():
    with pytest.raises(ValueError):
        VIL.calculate(reflectivity_profile_mm6_m3=[1.0, 2.0, 3.0], height_profile_m=[0.0, 1000.0])


def test_echo_top_interpolates():
    reflectivity = [45.0, 30.0, 20.0, 10.0]
    heights = [0.0, 3000.0, 6000.0, 9000.0]
    eth = EchoTop.height(reflectivity, heights, threshold_dbz=18.0)
    # threshold 18 is between heights[1]=30dBZ@3000m and heights[2]=20dBZ@6000m... actually
    # crossing is between index 2 (20dBZ) and index 3 (10dBZ)
    assert 6000.0 < eth < 9000.0


def test_echo_top_zero_when_surface_below_threshold():
    eth = EchoTop.height([10.0, 5.0, 0.0], [0.0, 1000.0, 2000.0], threshold_dbz=18.0)
    assert eth == 0.0


def test_echo_top_returns_profile_top_when_never_drops_below():
    eth = EchoTop.height([40.0, 35.0, 30.0], [0.0, 1000.0, 2000.0], threshold_dbz=18.0)
    assert eth == 2000.0


@pytest.mark.parametrize(
    "rate,expected",
    [
        (0.05, "Trace"),
        (1.0, "Light"),
        (5.0, "Moderate"),
        (20.0, "Heavy"),
        (100.0, "Violent"),
    ],
)
def test_precipitation_intensity_classification(rate, expected):
    assert PrecipitationIntensity.classify(rate) == expected


def test_precipitation_intensity_invalid_negative():
    with pytest.raises(ValueError):
        PrecipitationIntensity.classify(-1.0)


def test_zr_round_trip_consistency():
    rate = 10.0
    z = PrecipitationIntensity.reflectivity_from_rain_rate(rate)
    rate_back = PrecipitationIntensity.rain_rate_from_reflectivity_dbz(10.0 * __import__("math").log10(z))
    assert rate_back == pytest.approx(rate, rel=1e-3)


def test_hydrometeor_rain():
    assert HydrometeorType.classify(surface_temperature_c=10.0, surface_wet_bulb_c=8.0) == "Rain"


def test_hydrometeor_snow():
    assert HydrometeorType.classify(surface_temperature_c=-5.0, surface_wet_bulb_c=-3.0) == "Snow"


def test_hydrometeor_freezing_rain_or_ice_pellets():
    assert (
        HydrometeorType.classify(surface_temperature_c=-2.0, surface_wet_bulb_c=0.5)
        == "Freezing Rain / Ice Pellets"
    )


def test_hydrometeor_wet_snow_mix_when_surface_above_freezing():
    assert HydrometeorType.classify(surface_temperature_c=1.0, surface_wet_bulb_c=-0.2) == "Wet Snow/Mix"
