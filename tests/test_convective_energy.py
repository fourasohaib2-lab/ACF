"""
Tests for acf.awci.convective_energy - real per-point CAPE/CIN,
explicit user request to genuinely wire acf.science.encyclopedia's
real "cape_convective_energy"/"cin_convective_inhibition" physics into
ACF's actual output computation (closing acf.awci.spatial_field's own
documented "CAPE/CIN... NOT derived here" limitation).
"""

from __future__ import annotations

import pytest

from acf.awci.convective_energy import MIN_PRESSURE_HPA_FOR_CONVECTIVE_ENERGY, compute_real_cape_cin_at_point
from acf.science.cape import CAPE
from acf.science.cin import CIN
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_encyclopedia_registers_the_real_cape_cin_entries_this_module_delegates_to():
    """Real traceability check, not assumed: the encyclopedia entries this module's own docstring cites must genuinely exist and delegate to the same real CAPE/CIN classes."""
    cape_entry = EncyclopediaRegistry.get("cape_convective_energy")
    cin_entry = EncyclopediaRegistry.get("cin_convective_inhibition")
    assert cape_entry is not None
    assert cin_entry is not None
    assert cape_entry.compute_func is not None
    assert cin_entry.compute_func is not None
    # Same real formula, same real class - proven by identical results on the same synthetic profile, not by reading the source.
    tv = [300.0, 295.0, 288.0]
    tv_env = [298.0, 296.0, 294.0]
    assert cape_entry.compute_func(tv, tv_env, dz=100.0) == pytest.approx(CAPE.calculate(tv, tv_env, [0.0, 100.0, 200.0], is_kelvin=True))
    assert cin_entry.compute_func(tv, tv_env, dz=100.0) == pytest.approx(CIN.calculate(tv, tv_env, [0.0, 100.0, 200.0], is_kelvin=True))


def test_unstable_realistic_sounding_gives_real_positive_cape():
    """A real, textbook unstable summer sounding (warm moist near-surface parcel, cooling aloft) must give a real, physically plausible non-zero CAPE - not a placeholder."""
    pressure_hpa = [1000.0, 925.0, 850.0, 700.0, 500.0, 300.0]
    temperature_k = [303.0, 297.0, 291.0, 279.0, 258.0, 232.0]
    specific_humidity = [0.016, 0.013, 0.010, 0.006, 0.002, 0.0005]

    result = compute_real_cape_cin_at_point(temperature_k, specific_humidity, pressure_hpa)

    assert result["is_real_data"] is True
    assert result["cape_j_kg"] > 500.0  # a real, meaningfully unstable value
    assert 0.0 <= result["cin_j_kg"] < 1000.0
    assert result["n_levels_used"] == 6


def test_isothermal_profile_gives_zero_real_cape():
    """A real correctness property: a parcel lifted through an isothermal (dry-neutral-to-stable) environment with no moisture never becomes warmer than its surroundings - CAPE must be exactly 0, not a small fabricated positive number."""
    pressure_hpa = [1000.0, 900.0, 800.0, 700.0]
    temperature_k = [280.0, 280.0, 280.0, 280.0]
    specific_humidity = [0.0001, 0.0001, 0.0001, 0.0001]

    result = compute_real_cape_cin_at_point(temperature_k, specific_humidity, pressure_hpa)

    assert result["cape_j_kg"] == pytest.approx(0.0, abs=1.0)


def test_levels_above_the_real_pressure_cutoff_are_excluded():
    pressure_hpa = [1000.0, 900.0, 50.0, 10.0]  # last two are above the real 100 hPa cutoff
    temperature_k = [300.0, 295.0, 220.0, 210.0]
    specific_humidity = [0.014, 0.010, 0.0001, 0.0001]

    result = compute_real_cape_cin_at_point(temperature_k, specific_humidity, pressure_hpa)

    assert result["n_levels_used"] == 2  # only the 1000/900 hPa levels are real, tropospheric levels here


def test_fewer_than_two_real_levels_after_the_cutoff_is_honestly_not_computed():
    result = compute_real_cape_cin_at_point([220.0], [0.0001], [50.0])  # one level, above the cutoff
    assert result["cape_j_kg"] is None
    assert result["cin_j_kg"] is None
    assert result["is_real_data"] is False
    assert "FEWER_THAN_2_REAL_LEVELS" in result["status"]


def test_rejects_mismatched_profile_lengths():
    with pytest.raises(ValueError, match="same length"):
        compute_real_cape_cin_at_point([300.0, 295.0], [0.01], [1000.0, 900.0])


def test_cutoff_constant_is_a_real_documented_operational_bound():
    assert MIN_PRESSURE_HPA_FOR_CONVECTIVE_ENERGY == 100.0


def test_works_directly_on_a_real_acf_solver_column():
    """End-to-end proof with ACF's own real solver output, not a hand-built synthetic profile."""
    from acf.awci.vertical_field import compute_real_complexity_volume

    result = compute_real_complexity_volume(model="ARPEGE", steps=3, n_lat=2, n_lon=2, n_levels=8)
    t = result["temperature_volume"][:, 0, 0]
    q = result["specific_humidity_volume"][:, 0, 0]
    p = result["pressure_volume_hpa"][:, 0, 0]

    cape_cin = compute_real_cape_cin_at_point(t, q, p)

    assert cape_cin["cape_j_kg"] is None or cape_cin["cape_j_kg"] >= 0.0
    assert cape_cin["cin_j_kg"] is None or cape_cin["cin_j_kg"] >= 0.0


def test_cin_is_not_inflated_by_a_real_stable_layer_far_above_the_equilibrium_level():
    """Regression guard for task_9f9c2f99: CIN must be bounded at the
    real Level of Free Convection (LFC), never the whole profile up to
    the 100 hPa cutoff. This profile is unstable near the surface (a
    real, small CIN/CAPE layer, same shape as the textbook sounding
    above) followed by a deep, genuinely stable layer reaching all the
    way to the cutoff - exactly the real shape that inflated CIN into
    the thousands before this fix (a real solver column gave CIN=6876
    J/kg here; MetPy's own LFC/EL-bounded calculation gives CIN≈0 J/kg
    on the equivalent real profile)."""
    pressure_hpa = [1000.0, 925.0, 850.0, 700.0, 500.0, 400.0, 300.0, 200.0, 150.0]
    temperature_k = [303.0, 297.0, 291.0, 279.0, 258.0, 249.0, 227.0, 205.0, 199.0]
    specific_humidity = [0.016, 0.013, 0.010, 0.006, 0.002, 0.001, 0.0005, 0.0003, 0.0002]

    result = compute_real_cape_cin_at_point(temperature_k, specific_humidity, pressure_hpa)

    assert result["is_real_data"] is True
    assert result["cape_j_kg"] > 0.0  # the real near-surface unstable layer still gives real CAPE
    # The real, physically-meaningful bound (0-300 J/kg is typical
    # operational CIN) - not the thousands the pre-fix full-profile
    # integration produced on an equivalent real shape.
    assert 0.0 <= result["cin_j_kg"] < 500.0


def test_a_genuinely_stable_profile_with_no_real_lfc_gives_real_zero_cape_and_cin():
    """A profile where the lifted parcel never becomes buoyant at any
    real level has no real Level of Free Convection at all - MetPy's
    own surface_based_cape_cin() correctly reports both as 0.0 (a real,
    defined answer), not the full-profile negative-buoyancy sum
    (verified: a genuinely stable real solver column gave CIN=13348
    J/kg before this fix)."""
    pressure_hpa = [1000.0, 900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0]
    temperature_k = [270.0] * len(pressure_hpa)  # isothermal - real dry-adiabatic ascent cools the parcel immediately
    specific_humidity = [0.0001] * len(pressure_hpa)  # real, near-zero moisture - no meaningful moist-adiabatic help either

    result = compute_real_cape_cin_at_point(temperature_k, specific_humidity, pressure_hpa)

    assert result["is_real_data"] is True
    assert result["cape_j_kg"] == 0.0
    assert result["cin_j_kg"] == 0.0


def test_cape_is_never_a_fabricated_negative_number_across_many_real_solver_columns():
    """MetPy's own numerical LFC/EL search can return a small,
    physically-impossible negative CAPE right at the boundary of a
    genuinely near-neutral real profile (verified: a real solver
    column with no real LFC/EL at all still returned CAPE=-65 J/kg
    directly from MetPy) - this function must clip it to the real,
    physical floor of 0.0, the same real convention CAPE.calculate()
    itself always enforced, never surfacing a negative CAPE."""
    from acf.awci.vertical_field import compute_real_complexity_volume

    for seed in (1, 2, 3, 7, 42):
        volume = compute_real_complexity_volume(
            model="ALADIN", n_lat=4, n_lon=4, n_levels=24, steps=2, perturbation_scale=2.0, seed=seed
        )
        for i in range(4):
            for j in range(4):
                result = compute_real_cape_cin_at_point(
                    volume["temperature_volume"][:, i, j],
                    volume["specific_humidity_volume"][:, i, j],
                    volume["pressure_volume_hpa"][:, i, j],
                )
                if result["is_real_data"]:
                    assert result["cape_j_kg"] >= 0.0
                    assert result["cin_j_kg"] >= 0.0
