"""
Regression tests for a second batch of EncyclopediaEntry compute_func gaps
found by the repo-wide AST scan (see the first batch in
test_atmospheric_encyclopedia_expansion.py's
test_thermodynamics_encyclopedia_entries_missing_compute_func_now_wired).

Each entry below already documented a fully explicit, directly computable
"equation" field but had no compute_func at all - .calculate() unnecessarily
raised NotImplementedError. Fixed across aerodynamics/isa_atmosphere.py,
encyclopedia/dynamics.py, radar.py, aerosols_chemistry.py, and
severe_weather.py.
"""

import math

import pytest

from acf.science.cyclones import GradientWind
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_reynolds_number_and_drag_reuse_canonical_aeronautics_formulas():
    """
    reynolds_number_flow / aerodynamic_drag_force are algebraically
    identical to science/laws/aeronautics.py's 'reynolds_number' /
    'aerodynamic_drag' entries (single source of truth, re-expressed
    locally rather than duplicated with different logic).
    """
    re_law = EncyclopediaRegistry.get("reynolds_number_flow")
    re_value = re_law.calculate(density=1.225, velocity=250.0, length=3.5, dynamic_viscosity=1.789e-5)
    assert re_value == pytest.approx((1.225 * 250.0 * 3.5) / 1.789e-5)

    drag_law = EncyclopediaRegistry.get("aerodynamic_drag_force")
    drag_value = drag_law.calculate(density=1.225, velocity=250.0, surface_area=120.0, drag_coefficient=0.03)
    assert drag_value == pytest.approx(0.5 * 1.225 * 250.0**2 * 120.0 * 0.03)


def test_hydrostatic_equilibrium_law():
    law = EncyclopediaRegistry.get("hydrostatic_equilibrium_law")
    assert law.calculate(rho=1.225) == pytest.approx(-1.225 * 9.80665)


def test_thermal_wind_shear_per_height_matches_northern_hemisphere_physics():
    """
    A poleward-decreasing temperature (dT/dy < 0, y northward) must give
    a westerly shear increasing with height (d(ug)/dz > 0) in the
    Northern Hemisphere - the textbook explanation for jet streams near
    the tropopause (Holton & Hakim 2012).
    """
    law = EncyclopediaRegistry.get("thermal_wind_relation")
    dug_dz, dvg_dz = law.calculate(dt_dx=0.0, dt_dy=-1e-5, coriolis_f=1e-4, mean_temperature_k=260.0)
    assert dug_dz > 0.0
    assert dvg_dz == pytest.approx(0.0)


def test_gradient_wind_balance_reuses_science_cyclones_gradientwind():
    """gradient_wind_balance must delegate to (not duplicate) GradientWind.calculate()."""
    law = EncyclopediaRegistry.get("gradient_wind_balance")
    via_encyclopedia = law.calculate(
        radius_m=100000.0, coriolis_f=1e-4, density=1.2, radial_pressure_gradient_pa_m=0.01, cyclonic=True
    )
    via_direct = GradientWind.calculate(
        radius_m=100000.0, coriolis_f=1e-4, density=1.2, radial_pressure_gradient_pa_m=0.01, cyclonic=True
    )
    assert via_encyclopedia == via_direct


def test_doppler_radial_velocity():
    law = EncyclopediaRegistry.get("doppler_radial_velocity")
    c = 2.99792458e8
    value = law.calculate(doppler_shift_hz=1000.0, transmit_frequency_hz=3e9)
    assert value == pytest.approx((1000.0 * c) / (2.0 * 3e9))


def test_ozone_photostationary_state_and_dry_deposition_velocity():
    ozone_law = EncyclopediaRegistry.get("tropospheric_ozone_photostationary_state")
    # Simple, self-consistent illustrative values (not real rate constants -
    # the point is verifying the formula's arithmetic, not atmospheric realism).
    assert ozone_law.calculate(j_no2=1.0, no2_conc=10.0, k_o3_no=2.0, no_conc=5.0) == pytest.approx(1.0)

    deposition_law = EncyclopediaRegistry.get("dry_deposition_velocity")
    assert deposition_law.calculate(ra=50.0, rb=20.0, rc=100.0) == pytest.approx(1.0 / 170.0)


def test_hail_growth_model_and_tornado_vortex_dynamics():
    hail_law = EncyclopediaRegistry.get("hail_growth_model")
    expected = math.pi * (0.01**2) * 0.8 * abs(20.0 - 25.0) * 0.003
    assert hail_law.calculate(
        radius_m=0.01, collection_efficiency=0.8, fall_velocity_m_s=20.0, updraft_velocity_m_s=25.0, lwc_kg_m3=0.003
    ) == pytest.approx(expected)

    # Collection rate must stay non-negative even when the hailstone falls
    # SLOWER than the updraft (Vh < w) - a naive signed (Vh-w) form would
    # go negative and misrepresent growth as loss.
    assert hail_law.calculate(
        radius_m=0.01, collection_efficiency=0.8, fall_velocity_m_s=15.0, updraft_velocity_m_s=25.0, lwc_kg_m3=0.003
    ) > 0.0

    vortex_law = EncyclopediaRegistry.get("tornado_vortex_dynamics")
    assert vortex_law.calculate(angular_momentum_constant=5000.0, radius_m=100.0) == pytest.approx(50.0)
    # v_theta must decrease with increasing radius (v ~ 1/r), the whole
    # physical point of angular-momentum conservation in a free vortex.
    assert vortex_law.calculate(
        angular_momentum_constant=5000.0, radius_m=200.0
    ) < vortex_law.calculate(angular_momentum_constant=5000.0, radius_m=100.0)
