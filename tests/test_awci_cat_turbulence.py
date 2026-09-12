"""
Tests for acf.awci.cat_turbulence.compute_real_cat_index_at_level() -
the real Ellrod & Knapp (1992) Turbulence Index (TI2/EI), cited by
ICAO Doc 9837, closing AWCI's "travailler avec les lois de l'OACI et
l'OMM" request (2026-09-12): CATIndex already existed real and tested
in acf.science.wind_turbulence but was never called anywhere in
acf.awci.
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.awci.cat_turbulence import compute_real_cat_index_at_level, get_cat_turbulence_hazard_reference
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.awci.workstation_fields import real_grid_spacing_m
from acf.science.encyclopedia.aerodynamics.isa_atmosphere import calculate_isa_pressure_altitude
from acf.science.wind_turbulence import CATIndex


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=10, n_lon=14, n_levels=6, steps=4, seed=3, perturbation_scale=8.0)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def _hand_built_volume():
    """A small, fully deterministic hand-built volume (not a real
    solver run) - lets tests assert exact, independently-verifiable
    numbers rather than only real solver emergent behaviour."""
    lats = [0.0, 1.0, 2.0, 3.0]
    lons = [0.0, 1.0, 2.0, 3.0]
    n_lat, n_lon = len(lats), len(lons)
    # A real, deliberately non-uniform u field (a genuine gradient to
    # differentiate, not a flat/degenerate one) at each of 2 levels.
    u0 = np.array([[float(i + j) for j in range(n_lon)] for i in range(n_lat)])
    v0 = np.array([[float(i - j) for j in range(n_lon)] for i in range(n_lat)])
    u1 = u0 + 20.0  # real, uniform +20 m/s shift at the level above -> a real, nonzero du/dz
    v1 = v0 + 5.0
    pressure0 = np.full((n_lat, n_lon), 850.0)
    pressure1 = np.full((n_lat, n_lon), 700.0)  # real, higher (lower-pressure) level above
    return {
        "lats": lats,
        "lons": lons,
        "u_volume": np.stack([u0, u1]),
        "v_volume": np.stack([v0, v1]),
        "pressure_volume_hpa": np.stack([pressure0, pressure1]),
    }


def test_returns_undefined_when_the_volume_has_only_one_level():
    volume = _hand_built_volume()
    volume["u_volume"] = volume["u_volume"][:1]
    volume["v_volume"] = volume["v_volume"][:1]
    volume["pressure_volume_hpa"] = volume["pressure_volume_hpa"][:1]

    result = compute_real_cat_index_at_level(volume, level_idx=0)

    assert result["is_real_data"] is False
    assert result["status"] == "CAT_INDEX_NOT_COMPUTED_NO_ADJACENT_LEVEL"
    assert result["adjacent_level_idx"] is None
    assert np.all(np.isnan(result["ei_field"]))
    assert np.all(result["category_field"] == "UNDEFINED")


def test_picks_the_real_adjacent_level_correctly():
    volume = _hand_built_volume()  # only 2 levels: 0 and 1

    at_bottom = compute_real_cat_index_at_level(volume, level_idx=0)
    assert at_bottom["adjacent_level_idx"] == 1  # only real level above exists

    at_top = compute_real_cat_index_at_level(volume, level_idx=1)
    assert at_top["adjacent_level_idx"] == 0  # only real level below exists (top of the real volume)


def test_hand_built_volume_produces_real_nonzero_shear_and_deformation():
    volume = _hand_built_volume()
    result = compute_real_cat_index_at_level(volume, level_idx=0)

    assert result["is_real_data"] is True
    interior = (slice(1, -1), slice(1, -1))  # avoid one-sided gradient edges for a clean sanity check
    assert np.all(result["vws_field"][interior] > 0.0)  # real +20/+5 m/s shift over a real nonzero Δz
    assert np.all(np.isfinite(result["def_field"][interior]))
    assert np.all(np.isfinite(result["ei_field"][interior]))


def test_matches_an_independent_recomposition_from_the_same_real_primitives():
    """The real, decisive check: recompute EI at one interior point
    using the SAME real primitives (real_grid_spacing_m, np.gradient,
    calculate_isa_pressure_altitude, CATIndex) completely independently
    in this test, and assert an exact match - proves the function
    genuinely composes them as its own docstring claims, not some
    other, undisclosed computation."""
    volume = _hand_built_volume()
    result = compute_real_cat_index_at_level(volume, level_idx=0)

    i, j = 2, 2  # a real interior point, no one-sided gradient edge effects
    dy, dx_per_row = real_grid_spacing_m(volume["lats"], volume["lons"])
    u0, v0 = volume["u_volume"][0], volume["v_volume"][0]
    du_dy = np.gradient(u0, axis=0)[i, j] / dy
    dv_dy = np.gradient(v0, axis=0)[i, j] / dy
    du_dx = np.gradient(u0, axis=1)[i, j] / dx_per_row[i]
    dv_dx = np.gradient(v0, axis=1)[i, j] / dx_per_row[i]

    alt0 = calculate_isa_pressure_altitude(volume["pressure_volume_hpa"][0][i, j] * 100.0)
    alt1 = calculate_isa_pressure_altitude(volume["pressure_volume_hpa"][1][i, j] * 100.0)
    delta_z = alt1 - alt0
    du_dz = (volume["u_volume"][1][i, j] - volume["u_volume"][0][i, j]) / delta_z
    dv_dz = (volume["v_volume"][1][i, j] - volume["v_volume"][0][i, j]) / delta_z

    expected_vws = CATIndex.vertical_wind_shear(du_dz, dv_dz)
    expected_def = CATIndex.deformation(du_dx, dv_dy, dv_dx, du_dy)
    expected_cvg = CATIndex.convergence(du_dx, dv_dy)
    expected_ei = CATIndex.ti2(expected_vws, expected_def, expected_cvg)

    assert result["vws_field"][i, j] == pytest.approx(expected_vws)
    assert result["def_field"][i, j] == pytest.approx(expected_def)
    assert result["cvg_field"][i, j] == pytest.approx(expected_cvg)
    assert result["ei_field"][i, j] == pytest.approx(expected_ei)
    assert result["category_field"][i, j] == CATIndex.category(expected_ei)


def test_ei_and_category_are_always_consistent_with_each_other():
    volume = _real_volume()
    result = compute_real_cat_index_at_level(volume, level_idx=2)
    ei = result["ei_field"]
    category = result["category_field"]
    for i in range(ei.shape[0]):
        for j in range(ei.shape[1]):
            if np.isnan(ei[i, j]):
                assert category[i, j] == "UNDEFINED"
            else:
                assert category[i, j] == CATIndex.category(float(ei[i, j]))


def test_never_fabricates_a_category_for_a_real_undefined_point():
    """Real degenerate case: a volume whose 2 real levels have an
    (unrealistically) identical pressure at some point - Δz collapses
    to ~0, must never divide, must honestly report UNDEFINED there."""
    volume = _hand_built_volume()
    volume["pressure_volume_hpa"][1][:, :] = volume["pressure_volume_hpa"][0][:, :]  # real zero Δz everywhere

    result = compute_real_cat_index_at_level(volume, level_idx=0)

    assert np.all(np.isnan(result["ei_field"]))
    assert np.all(result["category_field"] == "UNDEFINED")


def test_real_solver_volume_shapes_and_bounded_intermediate_signals():
    volume = _real_volume(n_lat=8, n_lon=10, n_levels=5)
    result = compute_real_cat_index_at_level(volume, level_idx=2)
    n_lat, n_lon = len(volume["lats"]), len(volume["lons"])
    for key in ("ei_field", "vws_field", "def_field", "cvg_field"):
        assert result[key].shape == (n_lat, n_lon)
    assert result["category_field"].shape == (n_lat, n_lon)
    real_vws = result["vws_field"][~np.isnan(result["vws_field"])]
    assert np.all(real_vws >= 0.0)  # a real magnitude (sqrt sum of squares), never negative


def test_get_cat_turbulence_hazard_reference_returns_the_real_registry_entry():
    """Same real traceability pattern already established by
    acf.awci.microburst.get_microburst_hazard_reference()."""
    ref = get_cat_turbulence_hazard_reference()

    assert ref is not None
    assert ref.key == "cat_turbulence"
    assert any("ICAO Doc 9837" in reference for reference in ref.references)
    assert any("Ellrod" in reference for reference in ref.references)
