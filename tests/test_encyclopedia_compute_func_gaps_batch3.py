"""
Regression tests for a third batch of EncyclopediaEntry compute_func gaps
found by the repo-wide AST scan (see batch 1 in
test_atmospheric_encyclopedia_expansion.py and batch 2 in
test_encyclopedia_compute_func_gaps_batch2.py).
"""

import math

import pytest

from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_ekman_spiral_limits():
    """u(0)=v(0)=0 (no-slip surface BC); u(z->inf)->Ug, v(z->inf)->0 (approaches geostrophic wind)."""
    law = EncyclopediaRegistry.get("ekman_spiral")
    u0, v0 = law.calculate(geostrophic_wind_ug=15.0, ekman_parameter_a=0.001, height_m=0.0)
    assert u0 == pytest.approx(0.0)
    assert v0 == pytest.approx(0.0)

    u_far, v_far = law.calculate(geostrophic_wind_ug=15.0, ekman_parameter_a=0.001, height_m=20000.0)
    assert u_far == pytest.approx(15.0, abs=1e-4)
    assert v_far == pytest.approx(0.0, abs=1e-4)


def test_snow_albedo_formulas_are_consistently_the_same_underlying_model():
    """
    cryosphere.py's snow_albedo_feedback and cryosphere_extended.py's
    snow_albedo_aging_metamorphism are algebraically the same formula
    (verified during the fix) - both must now share one implementation
    and agree exactly for equivalent parameters.
    """
    feedback = EncyclopediaRegistry.get("snow_albedo_feedback")
    aging = EncyclopediaRegistry.get("snow_albedo_aging_metamorphism")
    v1 = feedback.calculate(alpha_fresh=0.85, alpha_wet=0.50, k=0.1, age=5.0)
    v2 = aging.calculate(alpha_fresh=0.85, alpha_min=0.50, k_aging=0.1, t=5.0)
    assert v1 == v2
    assert 0.50 < v1 < 0.85  # decayed partway between fresh and aged/wet


def test_sea_ice_growth_rate():
    law = EncyclopediaRegistry.get("sea_ice_thermodynamics_cice")
    # Colder surface temperature (bigger Tf - Tsurface) must grow ice faster.
    slow = law.calculate(
        thermal_conductivity_ice=2.0, ice_density=917.0, latent_heat_fusion=3.34e5,
        freezing_temp_c=-1.8, surface_temp_c=-5.0, ice_thickness_m=0.5,
    )
    fast = law.calculate(
        thermal_conductivity_ice=2.0, ice_density=917.0, latent_heat_fusion=3.34e5,
        freezing_temp_c=-1.8, surface_temp_c=-20.0, ice_thickness_m=0.5,
    )
    assert fast > slow > 0.0


def test_dutton_cat_index_is_distinct_from_ellrod_knapp():
    """A genuinely different, independently-cited CAT formula from science/wind_turbulence.py's CATIndex."""
    law = EncyclopediaRegistry.get("clear_air_turbulence_index")
    assert law.calculate(horizontal_shear=0.01, vertical_shear=0.02) == pytest.approx(1.25 * 0.01 + 0.25 * 0.02**2)


def test_mountain_wave_froude_number_and_wake_vortex_circulation():
    froude_law = EncyclopediaRegistry.get("mountain_waves_rotors")
    assert froude_law.calculate(
        wind_speed_perpendicular=20.0, brunt_vaisala_n=0.02, mountain_height_m=1500.0
    ) == pytest.approx(20.0 / (0.02 * 1500.0))

    wake_law = EncyclopediaRegistry.get("wake_turbulence_decay")
    gamma = wake_law.calculate(
        aircraft_mass_kg=560000.0, g=9.80665, air_density=1.225, wingspan_m=80.0, flight_velocity_m_s=75.0
    )
    assert gamma == pytest.approx((4.0 * 560000.0 * 9.80665) / (math.pi * 1.225 * 80.0 * 75.0))


def test_subcloud_evaporation_rejects_percentage_rh():
    law = EncyclopediaRegistry.get("subcloud_evaporation")
    value = law.calculate(evaporation_coefficient=0.001, relative_humidity=0.4, rainwater_content=0.002)
    assert value > 0.0
    with pytest.raises(ValueError):
        law.calculate(evaporation_coefficient=0.001, relative_humidity=40.0, rainwater_content=0.002)


def test_bernoulli_total_head_is_conserved_between_two_equivalent_states():
    """The whole point of Bernoulli's theorem: two states on the same streamline with the same
    total head must evaluate to the same constant, even with different p/V/z trade-offs."""
    law = EncyclopediaRegistry.get("bernoulli_principle_flow")
    state_a = law.calculate(static_pressure_pa=101325.0, density=1.225, velocity=50.0, height_m=0.0)
    # Faster flow (higher V) at the same height must have LOWER static pressure to conserve total head.
    faster_pressure = 101325.0 - 0.5 * 1.225 * (80.0**2 - 50.0**2)
    state_b = law.calculate(static_pressure_pa=faster_pressure, density=1.225, velocity=80.0, height_m=0.0)
    assert state_a == pytest.approx(state_b)


def test_gps_radio_occultation_refractivity_is_physically_plausible():
    """Real near-surface atmospheric refractivity N is typically 250-400 N-units."""
    law = EncyclopediaRegistry.get("gps_radio_occultation_gnss_pwv")
    n = law.calculate(pressure_hpa=1000.0, temperature_k=280.0, vapor_pressure_hpa=10.0)
    assert 250.0 < n < 400.0


def test_downdraft_cold_pool_returns_signed_downdraft_and_positive_gust():
    law = EncyclopediaRegistry.get("downdraft_cold_pool")
    result = law.calculate(dcape=800.0, reduced_gravity=0.05, cold_pool_depth_m=1000.0, gust_front_coefficient=1.0)
    assert result["w_down_m_s"] == pytest.approx(-math.sqrt(2.0 * 800.0))
    assert result["w_down_m_s"] < 0.0  # downward
    assert result["v_gust_m_s"] == pytest.approx(math.sqrt(0.05 * 1000.0))
    assert result["v_gust_m_s"] > 0.0


def test_entrainment_detrainment_mass_flux_gradient():
    law = EncyclopediaRegistry.get("entrainment_detrainment_convection")
    # More entrainment than detrainment -> the updraft's mass flux grows with height.
    growing = law.calculate(entrainment_rate=0.0005, detrainment_rate=0.0002, mass_flux=1e6)
    assert growing > 0.0
    # More detrainment than entrainment -> the updraft's mass flux shrinks with height.
    shrinking = law.calculate(entrainment_rate=0.0002, detrainment_rate=0.0005, mass_flux=1e6)
    assert shrinking < 0.0


def test_vad_radial_velocity_recovers_wind_components_at_cardinal_azimuths():
    """
    At azimuth=0 the radial velocity along the beam equals the U
    component; at azimuth=pi/2 it equals V - the whole basis of VAD
    wind retrieval (Browning & Wexler 1968).
    """
    law = EncyclopediaRegistry.get("vad_velocity_azimuth_display")
    vr_east = law.calculate(mean_u=10.0, mean_v=5.0, mean_w=0.0, azimuth_rad=0.0, elevation_rad=0.0)
    assert vr_east == pytest.approx(10.0)
    vr_north = law.calculate(mean_u=10.0, mean_v=5.0, mean_w=0.0, azimuth_rad=math.pi / 2.0, elevation_rad=0.0)
    assert vr_north == pytest.approx(5.0)


def test_rayleigh_scattering_cross_section_is_order_of_magnitude_correct():
    """
    Real molecular Rayleigh cross-section at 500nm is documented in
    atmospheric optics literature as ~4-5e-31 m^2; the classical
    (uncorrected-for-anisotropy) formula this entry documents should
    land within the same order of magnitude.
    """
    law = EncyclopediaRegistry.get("rayleigh_scattering_cross_section")
    sigma = law.calculate(refractive_index=1.000293, number_density=2.546e25, wavelength_m=500e-9)
    assert 1e-31 < sigma < 1e-30

    # sigma_R ~ 1/lambda^4: halving the wavelength must increase sigma by 2^4 = 16x.
    sigma_half_wavelength = law.calculate(refractive_index=1.000293, number_density=2.546e25, wavelength_m=250e-9)
    assert sigma_half_wavelength == pytest.approx(sigma * 16.0, rel=1e-6)
