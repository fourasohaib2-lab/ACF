"""
Tests for acf.awci.spatial_field's real, opt-in `compute_microburst`
wiring (2026-09-12, closing AWCI's spatial "microburst" gap - the
per-point module already existed and was already wired into
AWCICalculator, but had no real spatial-field caller). Same
real-solver-run discipline as test_awci_spatial_field_ceiling_visibility_dust.py -
small n_lat/n_lon overrides to keep runs fast, never a mocked solver.
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.microburst import compute_real_microburst_risk_at_point
from acf.awci.spatial_field import compute_real_complexity_field
from acf.science.encyclopedia.aerodynamics.isa_atmosphere import calculate_isa_pressure_altitude


def test_microburst_field_absent_by_default():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert "microburst_risk_field" not in result
    assert "microburst_risk" not in result["fields_used"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"compute_wind_shear": True},
        {"compute_convective_energy": True},
    ],
)
def test_microburst_requires_both_wind_shear_and_convective_energy(kwargs):
    """Same reuse-not-recompute discipline as compute_updraft_velocity's
    own requires-compute_convective_energy guard - never silently
    computed from a second, independently-derived shear/CAPE."""
    with pytest.raises(ValueError, match="compute_microburst=True requires"):
        compute_real_complexity_field(
            model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2, compute_microburst=True, **kwargs
        )


def test_microburst_field_present_and_real_when_opted_in():
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6, n_lon=10, n_levels=6, steps=3, seed=1, perturbation_scale=8.0,
        compute_convective_energy=True, compute_wind_shear=True, compute_microburst=True,
    )
    assert "microburst_risk_field" in result
    assert result["microburst_risk_field"].shape == (6, 10)
    assert "microburst_risk" in result["fields_used"]
    # Real, non-fabricated field - every real value in [0, 1].
    real_values = result["microburst_risk_field"][~np.isnan(result["microburst_risk_field"])]
    assert len(real_values) > 0
    assert np.all(real_values >= 0.0) and np.all(real_values <= 1.0)


def test_microburst_field_matches_a_direct_compute_real_microburst_risk_at_point_call():
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6, n_lon=10, n_levels=6, steps=3, seed=2, perturbation_scale=8.0,
        compute_convective_energy=True, compute_wind_shear=True, compute_microburst=True,
    )
    i, j = 2, 3
    if np.isnan(result["cape_field"][i, j]) or np.isnan(result["wind_shear_field"][i, j]):
        pytest.skip("this real point had no real CAPE/shear this run - covered by the NaN test below")
    expected_altitude = calculate_isa_pressure_altitude(float(result["pressure_field_hpa"][i, j]) * 100.0)
    expected = compute_real_microburst_risk_at_point(
        wind_shear_m_s=float(result["wind_shear_field"][i, j]),
        cape=float(result["cape_field"][i, j]),
        altitude_m=expected_altitude,
    )
    assert result["microburst_risk_field"][i, j] == pytest.approx(expected["microburst_risk_score"])


def test_microburst_module_field_matches_the_point_api_with_real_microburst_risk():
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6, n_lon=10, n_levels=6, steps=3, seed=4, perturbation_scale=8.0,
        compute_convective_energy=True, compute_wind_shear=True, compute_microburst=True,
    )
    i, j = 1, 4
    data = {
        "temperature": float(result["temperature_field"][i, j]),
        "wind_speed": float(result["wind_speed_field"][i, j]),
        "specific_humidity": float(result["specific_humidity_field"][i, j]),
        "pressure": float(result["pressure_field_hpa"][i, j]),
    }
    if not np.isnan(result["microburst_risk_field"][i, j]):
        data["microburst_risk"] = float(result["microburst_risk_field"][i, j])
    expected = AWCICalculator().calculate(data)["module_scores"]["microburst"]
    assert result["module_fields"]["microburst"][i, j] == pytest.approx(expected)


def test_microburst_field_is_nan_wherever_cape_itself_was_not_real():
    """Same discipline as ceiling/visibility/dust: a point with no real
    per-column CAPE (too few real levels for a real parcel ascent -
    see acf.awci.convective_energy's own honest scope) must leave
    microburst_risk_field honestly NaN, never fabricate a 0.0 for a
    signal it could not actually evaluate."""
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=5, n_lon=8, n_levels=6, steps=2, seed=5,
        compute_convective_energy=True, compute_wind_shear=True, compute_microburst=True,
    )
    nan_cape_mask = np.isnan(result["cape_field"])
    if not np.any(nan_cape_mask):
        pytest.skip("this real run had real CAPE everywhere - nothing to check")
    assert np.all(np.isnan(result["microburst_risk_field"][nan_cape_mask]))


def test_microburst_field_still_zero_weight_by_default_even_when_opted_in():
    """Populating microburst_risk_field is not the same as it affecting
    awci_field - the real module weight is still 0.0 unless the caller
    separately raises it. Checked within ONE real solver run (never
    two separate runs - see compute_real_complexity_field()'s own
    Returns docstring on non-reproducibility across calls)."""
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=5, n_lon=8, n_levels=6, steps=2, seed=6, perturbation_scale=8.0,
        compute_convective_energy=True, compute_wind_shear=True, compute_microburst=True,
    )
    i, j = 2, 3
    # Same real cape/cin/wind_shear this run's own per-point loop
    # already fed AWCICalculator for this point (compute_convective_
    # energy=True and compute_wind_shear=True are both real, active
    # inputs here independent of microburst) - omitting them would
    # compare against a different, smaller data dict than the one the
    # real pipeline actually used for awci_field[i, j].
    data_without: dict = {
        "temperature": float(result["temperature_field"][i, j]),
        "wind_speed": float(result["wind_speed_field"][i, j]),
        "specific_humidity": float(result["specific_humidity_field"][i, j]),
        "pressure": float(result["pressure_field_hpa"][i, j]),
    }
    if not np.isnan(result["cape_field"][i, j]):
        data_without["cape"] = float(result["cape_field"][i, j])
        data_without["cin"] = float(result["cin_field"][i, j])
    if not np.isnan(result["wind_shear_field"][i, j]):
        data_without["wind_shear"] = float(result["wind_shear_field"][i, j])
    data_with = dict(data_without)
    if not np.isnan(result["microburst_risk_field"][i, j]):
        data_with["microburst_risk"] = float(result["microburst_risk_field"][i, j])

    awci_without = AWCICalculator().calculate(data_without)["awci"]
    awci_with = AWCICalculator().calculate(data_with)["awci"]
    assert awci_without == pytest.approx(awci_with)
    assert result["awci_field"][i, j] == pytest.approx(awci_without)


def test_microburst_can_be_enabled_together_with_ceiling_visibility_dust_without_interfering():
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6, n_lon=10, n_levels=6, steps=2, seed=7,
        compute_convective_energy=True, compute_wind_shear=True,
        compute_microburst=True, compute_ceiling=True, compute_visibility=True, compute_dust=True,
    )
    assert "microburst_risk_field" in result
    assert "ceiling_field" in result
    assert "visibility_risk_field" in result
    assert "dust_risk_field" in result
    assert set(result["fields_used"]) >= {
        "microburst_risk", "ceiling_height_m", "visibility_risk", "dust_risk", "cape", "cin", "wind_shear",
    }
