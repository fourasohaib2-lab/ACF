"""
Tests for acf.core.contracts - the Data Contract requested by the
user's "Prompt Maître ACF v2.0" (reports/ACF_MASTER_AUDIT_v2.md found
this genuinely absent before this work).
"""

from datetime import datetime, timedelta

import numpy as np
import pytest

from acf.awci.spatial_field import compute_real_complexity_field
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.core.contracts import Dataset, Provenance, QualityInfo, UncertaintyInfo, VariableContract


# ------------------------------------------------------------------ Provenance


def test_provenance_defaults_are_honestly_incomplete():
    prov = Provenance(generator="TestGenerator")
    assert prov.is_complete() is False


def test_provenance_complete_when_all_versions_supplied():
    prov = Provenance(
        generator="TestGenerator", algorithm_version="1.0", science_version="2026.09", config_version="default"
    )
    assert prov.is_complete() is True


def test_provenance_new_fields_default_to_the_same_honest_unknown_sentinel():
    """docs/ACF_MASTER_PROMPT.md sections 57-58 fields, added 2026-09-03 -
    purely additive, same honest default as the pre-existing fields."""
    prov = Provenance(generator="TestGenerator")
    assert prov.run_identifier == "unknown"
    assert prov.calibration_version == "unknown"
    assert prov.dataset_version == "unknown"
    assert prov.software_environment == "unknown"
    assert prov.input_files == []


def test_provenance_is_complete_unaffected_by_the_new_fields():
    """A real, pre-existing contract: is_complete() must keep meaning
    exactly what it always did (the original 3 fields), not silently
    grow stricter when new fields are added - a caller who already
    relies on is_complete() must not see it start returning False for
    an object it used to call complete."""
    prov = Provenance(
        generator="TestGenerator", algorithm_version="1.0", science_version="2026.09", config_version="default"
    )
    assert prov.is_complete() is True
    assert prov.is_fully_specified() is False  # the 5 newer fields are still "unknown"


def test_provenance_is_fully_specified_requires_every_real_version_field():
    prov = Provenance(
        generator="TestGenerator",
        algorithm_version="1.0",
        science_version="2026.09",
        config_version="default",
        run_identifier="run-2026-09-03-001",
        calibration_version="test-2026.09",
        dataset_version="golden-v1",
        software_environment="python-3.12",
    )
    assert prov.is_fully_specified() is True


def test_provenance_is_fully_specified_does_not_require_input_files():
    """An empty input_files list is a real, valid state (no file
    inputs - e.g. a pure in-memory solver run), not an "unfilled"
    field that should block is_fully_specified()."""
    prov = Provenance(
        generator="TestGenerator",
        algorithm_version="1.0",
        science_version="2026.09",
        config_version="default",
        run_identifier="run-2026-09-03-001",
        calibration_version="test-2026.09",
        dataset_version="golden-v1",
        software_environment="python-3.12",
        input_files=[],
    )
    assert prov.is_fully_specified() is True


# -------------------------------------------------------------------- Quality


def test_quality_defaults_to_not_assessed_never_pass():
    quality = QualityInfo()
    assert quality.status == "NOT_ASSESSED"


def test_quality_rejects_unknown_status():
    with pytest.raises(ValueError, match="status"):
        QualityInfo(status="MOSTLY_FINE")


def test_quality_rejects_out_of_range_completeness():
    with pytest.raises(ValueError, match="completeness_fraction"):
        QualityInfo(status="PASS", completeness_fraction=1.5)


# --------------------------------------------------------------- Uncertainty


def test_uncertainty_defaults_to_not_assessed():
    unc = UncertaintyInfo()
    assert unc.kind == "not_assessed"
    assert unc.value is None


def test_uncertainty_requires_a_real_value_for_a_real_kind():
    with pytest.raises(ValueError, match="requires a real value"):
        UncertaintyInfo(kind="ensemble")  # no value - would silently imply 0 uncertainty


def test_uncertainty_accepts_a_real_ensemble_value():
    unc = UncertaintyInfo(kind="ensemble", value=1.73, unit="K")
    assert unc.value == 1.73


def test_uncertainty_rejects_unknown_kind():
    with pytest.raises(ValueError, match="kind"):
        UncertaintyInfo(kind="made_up_kind", value=1.0)


# ----------------------------------------------------------- VariableContract


def test_variable_contract_from_registry_uses_real_cf_data():
    var = VariableContract.from_registry("temperature", "air_temperature", dimensions=("lat", "lon"))
    assert var.unit == "K"  # from the real CF table, not guessed
    assert var.valid_range == (173.15, 333.15)  # from the real physics_guard range table


def test_variable_contract_from_registry_raises_for_unknown_standard_name():
    with pytest.raises(ValueError):
        VariableContract.from_registry("bogus", "totally_made_up_standard_name", dimensions=("lat", "lon"))


def test_variable_contract_overrides_apply():
    var = VariableContract.from_registry(
        "temperature", "air_temperature", dimensions=("lat", "lon"), description="2m temperature"
    )
    assert var.description == "2m temperature"


# ---------------------------------------------------------------------- Dataset


def _minimal_dataset(**overrides):
    now = datetime(2026, 9, 2, 0, 0)
    defaults = dict(
        id="test-1",
        source="CoupledEarthSolver",
        model="ARPEGE",
        run="00Z",
        forecast_reference_time=now,
        valid_time=now + timedelta(hours=6),
        lead_time=timedelta(hours=6),
        variable="air_temperature",
        unit="K",
        dimensions=("lat", "lon"),
        coordinates={"lats": [10.0, 20.0], "lons": [0.0, 5.0]},
        values=np.array([[288.0, 289.0], [290.0, 291.0]]),
    )
    defaults.update(overrides)
    return Dataset(**defaults)


def test_dataset_is_fully_documented_false_by_default():
    ds = _minimal_dataset()
    assert ds.is_fully_documented() is False  # provenance/quality not supplied


def test_dataset_is_fully_documented_true_when_complete():
    ds = _minimal_dataset(
        provenance=Provenance(generator="Test", algorithm_version="1", science_version="1", config_version="1"),
        quality=QualityInfo(status="PASS"),
    )
    assert ds.is_fully_documented() is True


def test_dataset_validate_passes_on_real_valid_data():
    ds = _minimal_dataset()
    report = ds.validate()
    assert report.passed is True
    assert set(report.checks_run) == {"coordinate", "range", "time"}


def test_dataset_validate_catches_swapped_lat_lon():
    """Same real bug class already caught in gui/dashboard/awci_dashboard.py - the Data Contract layer must catch it too."""
    ds = _minimal_dataset(coordinates={"lats": [0.0, 5.0], "lons": [10.0, 200.0]})
    report = ds.validate()
    assert report.passed is False
    assert any("Longitude" in v for v in report.violations)


def test_dataset_validate_catches_out_of_range_values():
    ds = _minimal_dataset(values=np.array([[15.0, 16.0], [17.0, 18.0]]))  # Celsius mistaken for Kelvin
    report = ds.validate()
    assert report.passed is False
    assert any("air_temperature" in v for v in report.violations)


def test_dataset_validate_catches_bad_time_ordering():
    now = datetime(2026, 9, 2, 6, 0)
    ds = _minimal_dataset(forecast_reference_time=now, valid_time=now - timedelta(hours=1))
    report = ds.validate()
    assert report.passed is False
    assert any("valid_time" in v for v in report.violations)


def test_dataset_validate_skips_range_check_for_non_registered_variable():
    ds = _minimal_dataset(variable="awci_composite_score", unit="")
    report = ds.validate()
    assert "range" not in report.checks_run


# -------------------------------------------------------- real-data bridges


def test_dataset_from_real_field_uses_real_solver_output():
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2)
    ds = Dataset.from_real_field(result, field_key="awci_field", dataset_id="ds-1", variable="awci")

    assert ds.model == "ALADIN"
    np.testing.assert_array_equal(ds.values, result["awci_field"])
    assert ds.dimensions == ("lat", "lon")
    assert ds.provenance is not None
    assert ds.provenance.generator == "acf.awci.spatial_field.compute_real_complexity_field"


def test_dataset_from_real_field_temperature_validates_against_real_range():
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2)
    ds = Dataset.from_real_field(
        result, field_key="temperature_field", dataset_id="ds-2", variable="air_temperature", unit="K"
    )
    report = ds.validate()
    # Real solver output at this scale should be well within the operational range.
    assert report.passed is True
    assert "range" in report.checks_run


def test_dataset_from_real_volume_uses_real_solver_output():
    result = compute_real_complexity_volume(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2)
    ds = Dataset.from_real_volume(result, field_key="awci_volume", dataset_id="ds-3", variable="awci")

    assert ds.dimensions == ("level", "lat", "lon")
    np.testing.assert_array_equal(ds.values, result["awci_volume"])
    assert len(ds.coordinates["levels"]) == result["n_levels"]
