"""
Tests for acf.normalization - the Normalization & Interoperability
Engine (docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md's layer 3, explicit
user request "vas-y, construis normalization/").
"""

import pytest

from acf.normalization.normalizer import normalize_variable
from acf.normalization.units import (
    convert_precipitation_kg_m2_to_mm,
    convert_precipitation_mm_to_kg_m2,
    convert_unit,
)
from acf.normalization.variable_names import cf_canonical_unit, to_cf_standard_name


def test_convert_unit_temperature():
    assert convert_unit(273.15, "K", "degC") == pytest.approx(0.0, abs=1e-6)
    assert convert_unit(0.0, "degC", "K") == pytest.approx(273.15, abs=1e-6)


def test_convert_unit_pressure():
    assert convert_unit(1013.25, "hPa", "Pa") == pytest.approx(101325.0, abs=1e-3)


def test_convert_unit_wind_speed_cf_notation():
    """CF's space-separated exponent notation ('m s-1') must parse directly - not a hand-rolled table."""
    knots = convert_unit(10.0, "m s-1", "kt")
    assert knots == pytest.approx(19.438, abs=1e-3)


def test_convert_unit_specific_humidity_ratio():
    assert convert_unit(0.01, "kg kg-1", "g kg-1") == pytest.approx(10.0, abs=1e-6)


def test_convert_unit_raises_for_dimensionally_incompatible_units():
    """A genuine unit mismatch must fail loudly, not return a meaningless number."""
    with pytest.raises(Exception):  # noqa: B017 - pint's own DimensionalityError, not asserting the exact type
        convert_unit(1.0, "K", "m s-1")


def test_precipitation_kg_m2_mm_round_trip():
    assert convert_precipitation_kg_m2_to_mm(5.0) == pytest.approx(5.0, abs=1e-9)
    assert convert_precipitation_mm_to_kg_m2(5.0) == pytest.approx(5.0, abs=1e-9)
    # Real round-trip identity, not just each direction individually.
    original = 12.7
    assert convert_precipitation_mm_to_kg_m2(convert_precipitation_kg_m2_to_mm(original)) == pytest.approx(
        original, abs=1e-9
    )


def test_to_cf_standard_name_real_table_lookup():
    result = to_cf_standard_name("t2m", source="ecmwf")
    assert result["standard_name"] == "air_temperature"
    assert result["unit"] == "K"
    assert "temperature" in result["description"].lower()


def test_to_cf_standard_name_wind_components():
    u = to_cf_standard_name("u10", source="ecmwf")
    v = to_cf_standard_name("v10", source="ecmwf")
    assert u["standard_name"] == "eastward_wind"
    assert v["standard_name"] == "northward_wind"


def test_to_cf_standard_name_unknown_short_name_raises_not_guesses():
    with pytest.raises(ValueError, match="not in"):
        to_cf_standard_name("totally_made_up_variable", source="ecmwf")


def test_to_cf_standard_name_unsupported_source_raises():
    with pytest.raises(ValueError, match="No real reference table"):
        to_cf_standard_name("t2m", source="noaa")


def test_cf_canonical_unit_real_lookup():
    assert cf_canonical_unit("air_temperature") == "K"
    assert cf_canonical_unit("eastward_wind") == "m s-1"


def test_cf_canonical_unit_unknown_raises():
    with pytest.raises(ValueError, match="not in"):
        cf_canonical_unit("totally_made_up_standard_name")


def test_normalize_variable_no_conversion_needed():
    result = normalize_variable("t2m", 288.15)
    assert result["standard_name"] == "air_temperature"
    assert result["value"] == pytest.approx(288.15)
    assert result["unit"] == "K"


def test_normalize_variable_real_unit_conversion():
    """Value supplied in Celsius must be genuinely converted to the table's native Kelvin, not just relabeled."""
    result = normalize_variable("t2m", 15.0, source_unit="degC")
    assert result["standard_name"] == "air_temperature"
    assert result["unit"] == "K"
    assert result["value"] == pytest.approx(288.15, abs=1e-2)


def test_normalize_variable_wind_conversion_from_knots():
    result = normalize_variable("u10", 10.0, source_unit="kt")
    assert result["standard_name"] == "eastward_wind"
    assert result["unit"] == "m s-1"
    assert result["value"] == pytest.approx(5.144, abs=1e-3)
