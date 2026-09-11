"""
Tests for acf.awci.spatial_field's real, opt-in `compute_ceiling`/
`compute_visibility`/`compute_dust` wiring (post-model4d audit,
2026-09-11, closing AWCI's "visibilité et plafond" and "poussière et
sable" gaps with real per-point field data, not just a caller-supplied
value). Same real-solver-run discipline as test_awci_spatial_field.py -
small n_lat/n_lon overrides to keep runs fast, never a mocked solver.
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.ceiling import compute_real_ceiling_at_point
from acf.awci.dust import compute_real_dust_risk_at_point
from acf.awci.spatial_field import compute_real_complexity_field
from acf.awci.visibility import compute_real_visibility_risk_at_point

# ----------------------------------------------------------- compute_ceiling


def test_ceiling_field_absent_by_default():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert "ceiling_field" not in result
    assert "ceiling_height_m" not in result["fields_used"]


def test_ceiling_field_present_and_real_when_opted_in():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=3, seed=1, perturbation_scale=3.0, compute_ceiling=True
    )
    assert "ceiling_field" in result
    assert result["ceiling_field"].shape == (6, 10)
    assert "ceiling_height_m" in result["fields_used"]
    assert np.nanstd(result["ceiling_field"]) > 0.0


def test_ceiling_field_matches_a_direct_compute_real_ceiling_at_point_call():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_ceiling=True
    )
    i, j = 2, 3
    expected = compute_real_ceiling_at_point(
        temperature_k=float(result["temperature_field"][i, j]),
        specific_humidity=float(result["specific_humidity_field"][i, j]),
        pressure_hpa=float(result["pressure_field_hpa"][i, j]),
    )
    if expected["is_real_data"]:
        assert result["ceiling_field"][i, j] == pytest.approx(expected["ceiling_height_m"])
    else:
        assert np.isnan(result["ceiling_field"][i, j])


def test_ceiling_module_field_matches_the_point_api_with_real_ceiling():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_ceiling=True
    )
    i, j = 1, 4
    data: dict = {
        "temperature": float(result["temperature_field"][i, j]),
        "specific_humidity": float(result["specific_humidity_field"][i, j]),
    }
    if not np.isnan(result["ceiling_field"][i, j]):
        data["ceiling_height_m"] = float(result["ceiling_field"][i, j])
    expected = AWCICalculator().calculate_module_scores(data)
    assert result["module_fields"]["ceiling"][i, j] == pytest.approx(round(expected["ceiling"] * 100, 1))


def test_ceiling_field_still_zero_weight_by_default_even_when_opted_in():
    """Populating ceiling_field is not the same as it affecting awci_field -
    the real module weight is still 0.0 unless the caller separately
    raises it (see AWCICalculator.WeightsManager.DEFAULT_WEIGHTS).
    Checked within ONE real solver run (never two separate runs - even
    with the same seed, compute_real_complexity_field() does not
    reproduce bit-identically across calls, see that function's own
    Returns docstring), by comparing awci_field's own real value at a
    point against AWCICalculator().calculate() fed that exact point's
    data both with and without the real ceiling_height_m key present."""
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2, seed=3, compute_ceiling=True
    )
    i, j = 2, 3
    data_without_ceiling: dict = {
        "temperature": float(result["temperature_field"][i, j]),
        "wind_speed": float(result["wind_speed_field"][i, j]),
        "specific_humidity": float(result["specific_humidity_field"][i, j]),
        "pressure": float(result["pressure_field_hpa"][i, j]),
    }
    data_with_ceiling = dict(data_without_ceiling)
    if not np.isnan(result["ceiling_field"][i, j]):
        data_with_ceiling["ceiling_height_m"] = float(result["ceiling_field"][i, j])

    awci_without = AWCICalculator().calculate(data_without_ceiling)["awci"]
    awci_with = AWCICalculator().calculate(data_with_ceiling)["awci"]
    assert awci_without == pytest.approx(awci_with)
    assert result["awci_field"][i, j] == pytest.approx(awci_without)


# --------------------------------------------------------- compute_visibility


def test_visibility_risk_field_absent_by_default():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert "visibility_risk_field" not in result
    assert "visibility_risk" not in result["fields_used"]


def test_visibility_risk_field_present_and_real_when_opted_in():
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6, n_lon=10, n_levels=4, steps=3, seed=1, perturbation_scale=3.0, compute_visibility=True,
    )
    assert "visibility_risk_field" in result
    assert result["visibility_risk_field"].shape == (6, 10)
    assert "visibility_risk" in result["fields_used"]


def test_visibility_risk_field_matches_a_direct_call_with_zero_precipitation():
    """precipitation_mm_h is always 0.0 here - no real precipitation
    field exists in CoupledEarthSolver's state (see compute_visibility's
    own docstring)."""
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_visibility=True
    )
    i, j = 2, 3
    expected = compute_real_visibility_risk_at_point(
        temperature_k=float(result["temperature_field"][i, j]),
        specific_humidity=float(result["specific_humidity_field"][i, j]),
        pressure_hpa=float(result["pressure_field_hpa"][i, j]),
        precipitation_mm_h=0.0,
    )
    if expected["is_real_data"]:
        assert result["visibility_risk_field"][i, j] == pytest.approx(expected["visibility_risk_score"])
    else:
        assert np.isnan(result["visibility_risk_field"][i, j])


def test_visibility_module_field_matches_the_point_api_with_real_visibility_risk():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_visibility=True
    )
    i, j = 1, 4
    data: dict = {
        "temperature": float(result["temperature_field"][i, j]),
        "specific_humidity": float(result["specific_humidity_field"][i, j]),
    }
    if not np.isnan(result["visibility_risk_field"][i, j]):
        data["visibility_risk"] = float(result["visibility_risk_field"][i, j])
    expected = AWCICalculator().calculate_module_scores(data)
    assert result["module_fields"]["visibility"][i, j] == pytest.approx(round(expected["visibility"] * 100, 1))


# ---------------------------------------------------------------- compute_dust


def test_dust_risk_field_absent_by_default():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert "dust_risk_field" not in result
    assert "dust_risk" not in result["fields_used"]


def test_dust_risk_field_present_and_real_when_opted_in():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=3, seed=1, perturbation_scale=3.0, compute_dust=True
    )
    assert "dust_risk_field" in result
    assert result["dust_risk_field"].shape == (6, 10)
    assert "dust_risk" in result["fields_used"]


def test_dust_risk_field_matches_a_direct_compute_real_dust_risk_at_point_call():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_dust=True
    )
    i, j = 2, 3
    expected = compute_real_dust_risk_at_point(
        temperature_k=float(result["temperature_field"][i, j]),
        specific_humidity=float(result["specific_humidity_field"][i, j]),
        pressure_hpa=float(result["pressure_field_hpa"][i, j]),
        wind_speed_m_s=float(result["wind_speed_field"][i, j]),
    )
    if expected["is_real_data"]:
        assert result["dust_risk_field"][i, j] == pytest.approx(expected["dust_risk_score"])
    else:
        assert np.isnan(result["dust_risk_field"][i, j])


def test_dust_module_field_matches_the_point_api_with_real_dust_risk():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_dust=True
    )
    i, j = 1, 4
    data: dict = {
        "temperature": float(result["temperature_field"][i, j]),
        "specific_humidity": float(result["specific_humidity_field"][i, j]),
        "wind_speed": float(result["wind_speed_field"][i, j]),
    }
    if not np.isnan(result["dust_risk_field"][i, j]):
        data["dust_risk"] = float(result["dust_risk_field"][i, j])
    expected = AWCICalculator().calculate_module_scores(data)
    assert result["module_fields"]["dust"][i, j] == pytest.approx(round(expected["dust"] * 100, 1))


# ------------------------------------------------------- all three together


def test_all_three_can_be_enabled_together_without_interfering():
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6, n_lon=10, n_levels=4, steps=2, seed=2,
        compute_ceiling=True, compute_visibility=True, compute_dust=True,
    )
    assert "ceiling_field" in result
    assert "visibility_risk_field" in result
    assert "dust_risk_field" in result
    assert set(result["fields_used"]) >= {"ceiling_height_m", "visibility_risk", "dust_risk"}
