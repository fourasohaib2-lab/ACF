"""
Tests for the Model Adapter Protocol extension of
acf.models.base_model.BaseWeatherModel (explicit user request "vas-y,
construis le Model Adapter Protocol" - reports/ACF_MASTER_AUDIT_v2.md
found the real adapters used inconsistent method names, e.g.
read_arome_file()/read_aladin_file()/read_arpege_file() for the same
real logic, forcing model-specific branching to use them generically).
"""

from pathlib import Path

import pytest

from acf.models.aladin import ALADINIngestionAdapter
from acf.models.arome import AROMEIngestionAdapter
from acf.models.arpege import ARPEGEIngestionAdapter
from acf.models.implementations.era5 import ERA5Model


# ------------------------------------------------------- identify/vertical_levels


def test_identify_is_a_real_alias_for_detect(tmp_path: Path):
    adapter = AROMEIngestionAdapter()
    arome_file = tmp_path / "arome_run.fa"
    assert adapter.identify(arome_file) == adapter.detect(arome_file) is True
    assert adapter.identify(tmp_path / "wrf_run.fa") == adapter.detect(tmp_path / "wrf_run.fa") is False


def test_vertical_levels_is_a_real_alias_for_levels():
    adapter = ARPEGEIngestionAdapter()
    assert adapter.vertical_levels() == adapter.levels()
    assert len(adapter.vertical_levels()) == 105


# ----------------------------------------------------------------------- read()


@pytest.mark.parametrize(
    "adapter_cls,filename,expected_model,model_specific_method",
    [
        (AROMEIngestionAdapter, "arome_run.fa", "AROME", "read_arome_file"),
        (ALADINIngestionAdapter, "aladin_run.fa", "ALADIN", "read_aladin_file"),
        (ARPEGEIngestionAdapter, "arpege_run.fa", "ARPEGE", "read_arpege_file"),
    ],
)
def test_read_genuinely_delegates_to_the_model_specific_method(
    tmp_path, adapter_cls, filename, expected_model, model_specific_method
):
    """read() must return the EXACT same real result as the pre-existing model-specific method - a real delegation, not a second implementation."""
    real_file = tmp_path / filename
    real_file.write_text(f"{expected_model} TEST DATA", encoding="utf-8")
    adapter = adapter_cls()

    via_protocol = adapter.read(real_file)
    via_model_specific = getattr(adapter, model_specific_method)(real_file)

    assert via_protocol == via_model_specific
    assert via_protocol["model"] == expected_model


def test_read_raises_honestly_for_a_model_with_no_real_backend():
    """ERA5Model never had real file-reading logic - read() must say so honestly, not silently return an empty dict."""
    adapter = ERA5Model()
    with pytest.raises(NotImplementedError, match="no real file-reading backend"):
        adapter.read("some_file.nc")


# ------------------------------------------------------------ metadata/coordinates


def test_metadata_and_coordinates_use_the_adapters_own_filepath(tmp_path):
    real_file = tmp_path / "arome_run.fa"
    real_file.write_text("AROME TEST DATA", encoding="utf-8")
    adapter = AROMEIngestionAdapter(filepath=real_file)

    metadata = adapter.metadata()
    coordinates = adapter.coordinates()

    assert metadata["model"] == "AROME"
    assert coordinates["resolution_x_meters"] == 1300.0


def test_metadata_raises_honestly_without_a_filepath():
    adapter = AROMEIngestionAdapter()  # no filepath constructed
    with pytest.raises(NotImplementedError, match="needs a real file"):
        adapter.metadata()


def test_coordinates_raises_honestly_without_a_filepath():
    adapter = ARPEGEIngestionAdapter()
    with pytest.raises(NotImplementedError, match="needs a real file"):
        adapter.coordinates()


# ------------------------------------------------------------------ forecast_times


def test_forecast_times_raises_honestly_for_every_adapter():
    """No adapter in this project has real forecast-cycle-time discovery logic - must say so, not guess a cycle schedule."""
    for adapter in (AROMEIngestionAdapter(), ALADINIngestionAdapter(), ARPEGEIngestionAdapter(), ERA5Model()):
        with pytest.raises(NotImplementedError):
            adapter.forecast_times()


# -------------------------------------------------------------------- capabilities


def test_capabilities_real_introspection_for_arome():
    adapter = AROMEIngestionAdapter()
    caps = adapter.capabilities()

    assert caps["name"] == "AROME"
    assert caps["variable_count"] == len(adapter.variables())
    assert caps["level_count"] == 90
    # AROME genuinely has a real read() backend now (this session's own work).
    assert caps["has_real_read_backend"] is True
    # Neither AROME nor any adapter has a real run/verify solver connected - honest, not fabricated.
    assert caps["has_real_run_backend"] is False
    assert caps["has_real_verify_backend"] is False


def test_capabilities_reports_no_real_read_backend_for_era5():
    caps = ERA5Model().capabilities()
    assert caps["has_real_read_backend"] is False


def test_capabilities_level_count_none_for_non_list_levels():
    """ERA5Model.levels() returns the string 'pressure', not a list - capabilities() must not crash on that, and must honestly report None rather than len('pressure')=8."""
    caps = ERA5Model().capabilities()
    assert caps["level_count"] is None


# ------------------------------------------------------------------------ normalize


def test_normalize_era5_maps_known_ecmwf_short_names():
    """ERA5Model's real variable names (t2m, u10, v10, msl) genuinely match resources/standards/ecmwf/parameters.json's real table."""
    result = ERA5Model().normalize()

    assert "t2m" in result["mapped"]
    assert result["mapped"]["t2m"]["standard_name"] == "air_temperature"
    assert "u10" in result["mapped"]
    assert "v10" in result["mapped"]
    assert "msl" in result["mapped"]


def test_normalize_era5_honestly_reports_unmapped_variables():
    """d2m/sp/tp/z/r/q are real ERA5 variables but have no entry in the small real parameters.json table today - must be reported as unmapped, not silently dropped or guessed."""
    result = ERA5Model().normalize()
    assert "d2m" in result["unmapped"]
    assert "sp" in result["unmapped"]


def test_normalize_arome_has_no_real_crosswalk_for_fa_field_names():
    """AROME's FA-format internal names (S090TEMPERATURE, SURFPRESSION, ...) have no real CF crosswalk anywhere in ACF - normalize() must not invent one."""
    result = AROMEIngestionAdapter().normalize()
    assert result["mapped"] == {}
    assert set(result["unmapped"]) == set(AROMEIngestionAdapter().variables())
