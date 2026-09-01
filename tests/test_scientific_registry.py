"""
Tests for acf.science.registry.ScientificRegistry, focused on the laws
registered alongside the CAPE/CIN physical fix and the canonical
Bolton (1980) equivalent potential temperature.
"""

import pytest

from acf.science.registry import ScientificRegistry


def test_cape_law_registered_and_computes():
    law = ScientificRegistry.get("cape_buoyancy_integral")
    assert law is not None
    value = law.calculate(
        parcel_temperature=[22, 18, 14],
        environment_temperature=[20, 16, 13],
        height=[0, 1000, 2000],
    )
    assert value > 0


def test_cin_law_registered_and_computes():
    law = ScientificRegistry.get("cin_buoyancy_integral")
    assert law is not None
    value = law.calculate(
        parcel_temperature=[18, 15, 10],
        environment_temperature=[20, 17, 12],
        height=[0, 1000, 2000],
    )
    assert value > 0


def test_bolton_equivalent_potential_temperature_law_registered():
    law = ScientificRegistry.get("equivalent_potential_temperature_bolton_1980")
    assert law is not None
    value = law.calculate(temperature_k=300.0, dewpoint_k=290.0, pressure_hpa=1000.0)
    assert value > 300.0


def test_thermodynamics_domain_lists_new_laws():
    keys = {law.key for law in ScientificRegistry.list_laws(domain="Thermodynamique")}
    assert {"cape_buoyancy_integral", "cin_buoyancy_integral", "equivalent_potential_temperature_bolton_1980"} <= keys


def test_clausius_clapeyron_law_returns_es_not_its_derivative():
    """
    CORRECTED: the 'equation' field previously stated only the
    differential relation des/dT=... while calculate() actually returns
    es(T) itself (a different quantity/unit, Pa not Pa/K) via the
    empirical Bolton/Tetens fit - documentation now states both forms.
    This test pins down that calculate() genuinely returns es(T): it
    must match science/saturation_vapor_pressure.py's canonical
    implementation exactly (same underlying Tetens formula, just
    re-expressed directly in Kelvin) and increase with temperature.
    """
    from acf.science.saturation_vapor_pressure import SaturationVaporPressure

    law = ScientificRegistry.get("clausius_clapeyron")
    assert law is not None

    es_290k = law.calculate(temperature=290.0)
    es_300k = law.calculate(temperature=300.0)
    assert es_300k > es_290k > 0

    expected_pa = SaturationVaporPressure.calculate(290.0, is_kelvin=True) * 100.0
    assert es_290k == pytest.approx(expected_pa, rel=1e-9)


def test_ice_crystal_nucleation_law_registered_and_computes():
    """
    CORRECTED: this entry documented a fully explicit, directly-computable
    equation (N_ice = N0*exp(b*(273.15-T))) but had no compute_func at all
    - same class of registry gap already fixed for monin_obukhov_length /
    planck_law / ertel_potential_vorticity / thermal_wind.
    """
    law = ScientificRegistry.get("ice_crystal_nucleation")
    assert law is not None

    # At T = 273.15 K (0 degC) the exponent is zero, so N_ice must equal N0
    # exactly, regardless of b - a direct check of the formula's own algebra.
    assert law.calculate(temperature_k=273.15, n0=1.0, b=0.6) == 1.0

    # Colder temperatures must yield MORE active ice nuclei (monotonically
    # increasing with supercooling - the whole physical point of the
    # formula), never fewer.
    warmer = law.calculate(temperature_k=268.15, n0=1.0, b=0.6)  # -5 degC
    colder = law.calculate(temperature_k=253.15, n0=1.0, b=0.6)  # -20 degC
    assert colder > warmer > 1.0
