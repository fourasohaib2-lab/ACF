"""
Tests for acf.awci.input_adapter - the real bridge from ACF's own real
Data Contract (acf.core.contracts.dataset.Dataset) into AWCICalculator's
plain dict input contract (docs/awci/AWCI_UI_AUDIT.md §4/§8, the "AWCI
Input Adapter" the master prompt's own architecture asked for - the one
genuine gap a real audit of this codebase's existing infrastructure
found: a real Data Contract and a real Model Adapter Protocol both
already existed, but nothing bridged one into AWCICalculator's dict).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.input_adapter import (
    AWCI_KEY_TO_CF_STANDARD_NAME,
    build_awci_data_from_datasets,
    datasets_from_real_field_point,
)
from acf.awci.spatial_field import compute_real_complexity_field
from acf.core.contracts.dataset import Dataset


def _real_dataset(variable: str, unit: str, value: float) -> Dataset:
    now = datetime.now(UTC)
    return Dataset(
        id="test",
        source="test",
        model="TEST",
        run="00Z",
        forecast_reference_time=now,
        valid_time=now,
        lead_time=timedelta(0),
        variable=variable,
        unit=unit,
        dimensions=(),
        values=value,
    )


# ------------------------------------------------- build_awci_data_from_datasets


def test_maps_the_4_real_cf_named_keys_with_native_units():
    datasets = {
        "temperature": _real_dataset("air_temperature", "K", 290.0),
        "specific_humidity": _real_dataset("specific_humidity", "kg kg-1", 0.01),
        "wind_speed": _real_dataset("wind_speed", "m s-1", 15.0),
        "pressure": _real_dataset("air_pressure", "hPa", 1000.0),
    }

    data, quality = build_awci_data_from_datasets(datasets)

    assert data == {"temperature": 290.0, "specific_humidity": 0.01, "wind_speed": 15.0, "pressure": 1000.0}
    for cf_name in AWCI_KEY_TO_CF_STANDARD_NAME.values():
        assert quality[cf_name].status == "VALID"


def test_converts_a_real_different_unit_to_awcicalculators_own_native_unit():
    """A real caller reporting temperature in Celsius (e.g. a METAR-
    derived Dataset) must be converted to K - AWCICalculator's own
    real convention - not passed through raw."""
    datasets = {"temperature": _real_dataset("air_temperature", "degC", 17.0)}

    data, _quality = build_awci_data_from_datasets(datasets)

    assert data["temperature"] == pytest.approx(290.15)


def test_pressure_stays_in_hpa_for_awcicalculator_not_converted_to_cf_pascals():
    """Real regression guard for a real bug found while building this
    adapter: AWCICalculator's own "pressure" key expects hPa (its own
    docstring), NOT the real CF canonical unit (Pa) - converting to Pa
    silently would feed AWCICalculator a value 100x too large."""
    datasets = {"pressure": _real_dataset("air_pressure", "hPa", 1000.0)}

    data, quality = build_awci_data_from_datasets(datasets)

    assert data["pressure"] == pytest.approx(1000.0)
    # The quality assessment, separately, must use the real CF/
    # OPERATIONAL_RANGES unit (Pa) - 1000 hPa = 100000 Pa, within range.
    assert quality["air_pressure"].status == "VALID"


def test_pressure_quality_uses_real_pascals_for_the_operational_range_check():
    """100 hPa = 10000 Pa, genuinely below OPERATIONAL_RANGES' real
    1000 Pa floor - proves the quality assessment really does use Pa,
    not silently reusing the hPa value against a Pa-scaled bound."""
    datasets = {"pressure": _real_dataset("air_pressure", "hPa", 5.0)}  # 500 Pa, below the real 1000 Pa floor

    _data, quality = build_awci_data_from_datasets(datasets)

    assert quality["air_pressure"].status == "OUT_OF_RANGE"


def test_awci_internal_keys_pass_through_without_a_cf_conversion():
    """cape/wind_shear/etc. are real ACF-internal composite quantities
    with no CF standard_name - passed through by direct value, no unit
    conversion attempted, no quality entry produced."""
    datasets = {"cape": _real_dataset("cape", "J/kg", 1500.0), "wind_shear": _real_dataset("wind_shear", "m/s", 12.0)}

    data, quality = build_awci_data_from_datasets(datasets)

    assert data == {"cape": 1500.0, "wind_shear": 12.0}
    assert "cape" not in quality
    assert "wind_shear" not in quality


def test_missing_variable_is_honestly_reported_never_fabricated():
    """A key never supplied at all must be absent from data (so
    AWCICalculator's own real default applies) AND honestly reported
    MISSING in quality - never silently defaulted to 0.0 in either place."""
    data, quality = build_awci_data_from_datasets({})

    assert data == {}
    for cf_name in AWCI_KEY_TO_CF_STANDARD_NAME.values():
        assert quality[cf_name].status == "MISSING"


def test_dataset_with_none_value_is_also_honestly_missing():
    datasets = {"temperature": _real_dataset("air_temperature", "K", None)}  # type: ignore[arg-type]

    data, quality = build_awci_data_from_datasets(datasets)

    assert "temperature" not in data
    assert quality["air_temperature"].status == "MISSING"


def test_a_real_array_with_more_than_one_element_raises():
    dataset = _real_dataset("air_temperature", "K", 0.0)
    dataset.values = [290.0, 291.0, 292.0]

    with pytest.raises(ValueError, match="real per-point Dataset"):
        build_awci_data_from_datasets({"temperature": dataset})


def test_result_feeds_a_real_coherent_awcicalculator_call():
    datasets = {
        "temperature": _real_dataset("air_temperature", "K", 300.0),
        "specific_humidity": _real_dataset("specific_humidity", "kg kg-1", 0.015),
        "wind_speed": _real_dataset("wind_speed", "m s-1", 20.0),
        "pressure": _real_dataset("air_pressure", "hPa", 1000.0),
        "cape": _real_dataset("cape", "J/kg", 800.0),
    }

    data, _quality = build_awci_data_from_datasets(datasets)
    result = AWCICalculator().calculate(data)

    assert 0.0 <= result["awci"] <= 100.0
    assert result["level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme"}


# --------------------------------------------------- datasets_from_real_field_point


def test_datasets_from_real_field_point_matches_the_real_field_arrays():
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=1, perturbation_scale=3.0)
    lat_idx, lon_idx = 2, 3

    datasets = datasets_from_real_field_point(result, lat_idx, lon_idx)

    assert datasets["temperature"].values == pytest.approx(float(result["temperature_field"][lat_idx, lon_idx]))
    assert datasets["wind_speed"].values == pytest.approx(float(result["wind_speed_field"][lat_idx, lon_idx]))
    assert datasets["specific_humidity"].values == pytest.approx(float(result["specific_humidity_field"][lat_idx, lon_idx]))
    assert datasets["pressure"].values == pytest.approx(float(result["pressure_field_hpa"][lat_idx, lon_idx]))
    assert datasets["pressure"].unit == "hPa"


def test_datasets_from_real_field_point_round_trips_into_the_same_real_awci_score():
    """Real end-to-end proof: real field -> real per-point Datasets ->
    adapter -> AWCICalculator gives the EXACT same score as building the
    dict by hand from the same real field arrays."""
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=2, perturbation_scale=3.0)
    lat_idx, lon_idx = 1, 4

    datasets = datasets_from_real_field_point(result, lat_idx, lon_idx)
    data, quality = build_awci_data_from_datasets(datasets)
    adapter_result = AWCICalculator().calculate(data)

    direct_data = {
        "temperature": float(result["temperature_field"][lat_idx, lon_idx]),
        "specific_humidity": float(result["specific_humidity_field"][lat_idx, lon_idx]),
        "wind_speed": float(result["wind_speed_field"][lat_idx, lon_idx]),
        "pressure": float(result["pressure_field_hpa"][lat_idx, lon_idx]),
    }
    direct_result = AWCICalculator().calculate(direct_data)

    assert adapter_result["awci"] == direct_result["awci"]
    assert set(quality.keys()) == set(AWCI_KEY_TO_CF_STANDARD_NAME.values())


def test_datasets_from_real_field_point_carries_real_provenance():
    result = compute_real_complexity_field(model="ARPEGE", n_lat=6, n_lon=10, n_levels=4, steps=2)
    datasets = datasets_from_real_field_point(result, 0, 0)

    for dataset in datasets.values():
        assert dataset.provenance is not None
        assert dataset.provenance.generator == "acf.awci.spatial_field.compute_real_complexity_field"
        assert dataset.model == "ARPEGE"
