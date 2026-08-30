"""
Tests for acf.science.radiation.
"""

import math

import pytest

from acf.science.radiation import BeerLambert, PlanckLaw, SolarPosition, StefanBoltzmann


def test_stefan_boltzmann_blackbody():
    # Sun's effective temperature (~5778K) should give a plausible
    # solar surface emittance (~63 MW/m^2 order of magnitude).
    e = StefanBoltzmann.calculate(5778.0)
    assert 6.0e7 < e < 6.5e7


def test_stefan_boltzmann_emissivity_scales_linearly():
    full = StefanBoltzmann.calculate(300.0, emissivity=1.0)
    half = StefanBoltzmann.calculate(300.0, emissivity=0.5)
    assert half == pytest.approx(full / 2)


def test_stefan_boltzmann_invalid_temperature():
    with pytest.raises(ValueError):
        StefanBoltzmann.calculate(0.0)


def test_stefan_boltzmann_invalid_emissivity():
    with pytest.raises(ValueError):
        StefanBoltzmann.calculate(300.0, emissivity=1.5)


def test_planck_law_positive():
    # Visible light (~500nm) at solar temperature.
    b = PlanckLaw.calculate(wavelength_m=500e-9, temperature_k=5778.0)
    assert b > 0


def test_planck_law_peaks_near_wien_wavelength():
    # Wien's displacement law: lambda_max ~ 2898/T micrometers.
    # At 5778K, peak should be near ~501nm (visible light) — verify
    # radiance is higher there than far in the wings (e.g. 100nm or 5000nm).
    t = 5778.0
    b_peak = PlanckLaw.calculate(wavelength_m=501e-9, temperature_k=t)
    b_uv = PlanckLaw.calculate(wavelength_m=100e-9, temperature_k=t)
    b_ir = PlanckLaw.calculate(wavelength_m=5000e-9, temperature_k=t)
    assert b_peak > b_uv
    assert b_peak > b_ir


def test_planck_law_invalid_wavelength():
    with pytest.raises(ValueError):
        PlanckLaw.calculate(wavelength_m=0.0, temperature_k=300.0)


def test_beer_lambert_full_transmission_at_zero_optical_depth():
    assert BeerLambert.calculate(100.0, 0.0) == pytest.approx(100.0)


def test_beer_lambert_attenuates():
    assert BeerLambert.calculate(100.0, 1.0) == pytest.approx(100.0 * math.exp(-1.0))


def test_beer_lambert_invalid_negative_optical_depth():
    with pytest.raises(ValueError):
        BeerLambert.calculate(100.0, -1.0)


def test_declination_at_june_solstice():
    # ~day 172 (June 21): declination should be close to +23.44 deg (Earth's axial tilt).
    dec_deg = math.degrees(SolarPosition.declination_spencer71(172))
    assert dec_deg == pytest.approx(23.44, abs=0.1)


def test_declination_at_december_solstice():
    dec_deg = math.degrees(SolarPosition.declination_spencer71(355))
    assert dec_deg == pytest.approx(-23.44, abs=0.1)


def test_declination_at_march_equinox_near_zero():
    dec_deg = math.degrees(SolarPosition.declination_spencer71(80))
    assert dec_deg == pytest.approx(0.0, abs=0.5)


def test_equation_of_time_small_magnitude():
    # Equation of time never exceeds ~17 minutes in magnitude.
    for day in [1, 45, 90, 135, 180, 225, 270, 315, 360]:
        eot = SolarPosition.equation_of_time_spencer71(day)
        assert abs(eot) < 20.0


def test_hour_angle_zero_at_solar_noon():
    assert SolarPosition.hour_angle_deg(12.0) == pytest.approx(0.0)


def test_hour_angle_sign_convention():
    assert SolarPosition.hour_angle_deg(9.0) < 0  # morning
    assert SolarPosition.hour_angle_deg(15.0) > 0  # afternoon


def test_zenith_angle_overhead_at_equator_equinox_noon():
    # At the equator, on the equinox, at solar noon: sun should be
    # (nearly) directly overhead, zenith ~ 0 deg.
    dec = SolarPosition.declination_spencer71(80)  # ~equinox
    zenith = SolarPosition.zenith_angle_deg(latitude_deg=0.0, declination_rad=dec, hour_angle_deg=0.0)
    assert zenith == pytest.approx(0.0, abs=1.0)


def test_zenith_angle_invalid_latitude():
    with pytest.raises(ValueError):
        SolarPosition.zenith_angle_deg(latitude_deg=100.0, declination_rad=0.0, hour_angle_deg=0.0)


def test_toa_irradiance_max_when_overhead():
    irr = SolarPosition.toa_irradiance(zenith_angle_deg=0.0)
    assert irr == pytest.approx(1361.0)


def test_toa_irradiance_zero_below_horizon():
    irr = SolarPosition.toa_irradiance(zenith_angle_deg=100.0)
    assert irr == 0.0
