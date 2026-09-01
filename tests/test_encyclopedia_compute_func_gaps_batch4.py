"""
Regression tests for a fourth batch of EncyclopediaEntry compute_func gaps
found by the repo-wide AST scan (see batches 1-3 in
test_atmospheric_encyclopedia_expansion.py,
test_encyclopedia_compute_func_gaps_batch2.py and
test_encyclopedia_compute_func_gaps_batch3.py).
"""

import math

import pytest

from acf.science.constants import UNIVERSAL_GAS_CONSTANT
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_first_law_thermodynamics_encyclopedia_matches_the_two_other_entries():
    """Third entry in ACF with the exact same dq=cp*dT-alpha*dp formula - must agree."""
    law = EncyclopediaRegistry.get("first_law_thermodynamics_encyclopedia")
    assert law.calculate(cp=1004.0, dT=5.0, alpha=0.8, dp=-500.0) == pytest.approx(5420.0)


def test_heterogeneous_nucleation_ice_shares_functional_form_but_not_values_with_fletcher():
    """Meyers/DeMott scheme - same exp(a*subcooling) shape as Fletcher 1962, different scheme."""
    law = EncyclopediaRegistry.get("heterogeneous_nucleation_ice")
    assert law.calculate(n0=1.0, activation_rate=0.6, subzero_temp_c=10.0) == pytest.approx(math.exp(6.0))
    # More subcooling -> more active ice nucleating particles.
    warmer = law.calculate(n0=1.0, activation_rate=0.6, subzero_temp_c=5.0)
    colder = law.calculate(n0=1.0, activation_rate=0.6, subzero_temp_c=15.0)
    assert colder > warmer


def test_cloud_condensation_process_never_goes_negative():
    law = EncyclopediaRegistry.get("cloud_condensation_process")
    assert law.calculate(specific_humidity=0.012, saturation_specific_humidity=0.010, timescale_s=100.0) == pytest.approx(2e-5)
    # Subsaturated air must clamp to exactly 0, not a negative "condensation".
    assert law.calculate(specific_humidity=0.008, saturation_specific_humidity=0.010, timescale_s=100.0) == 0.0


def test_hydrometeor_mixing_ratios_share_one_generic_ratio_implementation():
    for key in ("hydrometeor_cloud_water", "hydrometeor_cloud_ice", "hydrometeor_rain", "hydrometeor_snow", "hydrometeor_graupel"):
        law = EncyclopediaRegistry.get(key)
        assert law.calculate(species_mass_kg=0.003, air_mass_kg=1.0) == pytest.approx(0.003)
    with pytest.raises(ValueError):
        EncyclopediaRegistry.get("hydrometeor_rain").calculate(species_mass_kg=0.003, air_mass_kg=0.0)


def test_heterogeneous_aerosol_uptake_is_a_negative_loss_rate():
    law = EncyclopediaRegistry.get("heterogeneous_aerosol_interaction")
    rate = law.calculate(uptake_coefficient=0.1, thermal_velocity=300.0, aerosol_surface_area=1e-6, gas_concentration=1e10)
    assert rate == pytest.approx(-0.25 * 0.1 * 300.0 * 1e-6 * 1e10)
    assert rate < 0.0
    with pytest.raises(ValueError):
        law.calculate(uptake_coefficient=1.5, thermal_velocity=300.0, aerosol_surface_area=1e-6, gas_concentration=1e10)


def test_mineral_dust_aerosol_stays_honestly_uncomputable():
    """
    CORRECTED: the plain equation text used RH, inconsistent with the
    entry's own latex form (friction-velocity threshold) - fixed the
    text, but deliberately did NOT add a compute_func (no single
    precisely-citable numeric form was verified against the primary
    literature).
    """
    law = EncyclopediaRegistry.get("mineral_dust_aerosol")
    assert law is not None
    assert law.compute_func is None
    assert "u_star_t/u_star" in law.equation or "u_star_t" in law.equation
    assert "RH" not in law.equation


def test_lidar_backscatter_signal_includes_range_dilution():
    law = EncyclopediaRegistry.get("lidar_atmospheric_profiling")
    near = law.calculate(system_constant=1e6, molecular_backscatter=1e-6, aerosol_backscatter=1e-5, optical_depth=0.1, range_m=1000.0)
    far = law.calculate(system_constant=1e6, molecular_backscatter=1e-6, aerosol_backscatter=1e-5, optical_depth=0.1, range_m=2000.0)
    # 1/z^2 dilution: doubling range must quarter the signal (same optical depth).
    assert far == pytest.approx(near / 4.0)


def test_radiative_transfer_equation_derivative():
    law = EncyclopediaRegistry.get("radiative_transfer_equation")
    assert law.calculate(intensity=10.0, source_function=15.0, cos_zenith_angle=0.7) == pytest.approx((15.0 - 10.0) / 0.7)


def test_aerodynamic_stall_hazard_boolean():
    law = EncyclopediaRegistry.get("aerodynamic_stall_hazard")
    assert law.calculate(angle_of_attack_deg=20.0, critical_angle_deg=15.0) is True
    assert law.calculate(angle_of_attack_deg=10.0, critical_angle_deg=15.0) is False


def test_van_der_waals_reduces_to_ideal_gas_law_when_a_and_b_are_zero():
    """The defining sanity check for any real-gas equation of state: a=b=0 must recover pV=RT."""
    law = EncyclopediaRegistry.get("van_der_waals_real_gas")
    molar_volume = 0.0224  # m^3/mol, ~STP
    temperature_k = 273.15
    ideal_limit = law.calculate(
        molar_volume=molar_volume, temperature_k=temperature_k, attraction_constant_a=0.0, covolume_b=0.0
    )
    assert ideal_limit == pytest.approx((UNIVERSAL_GAS_CONSTANT * temperature_k) / molar_volume)

    # A positive attraction constant 'a' must REDUCE pressure below the ideal value
    # (attractive intermolecular forces pull molecules together, softening impacts).
    real_gas = law.calculate(
        molar_volume=molar_volume, temperature_k=temperature_k, attraction_constant_a=0.1358, covolume_b=3.183e-5
    )
    assert real_gas < ideal_limit

    with pytest.raises(ValueError):
        law.calculate(molar_volume=0.00001, temperature_k=273.15, attraction_constant_a=0.1, covolume_b=0.0001)
