"""
Unit test suite for ACF EPyGrAM Reader Integration (MISSION ACF-NWP-EPYGRAM-001).
"""

from pathlib import Path

import epygram
import pytest

from acf.data.detector import FormatDetector
from acf.data.readers.epygram_reader import (
    EPyGrAMFileNotFoundError,
    EPyGrAMNotInstalledError,
    EPyGrAMReader,
)
from acf.data.readers.epygram_reader import (
    close as epy_close,
)
from acf.data.readers.epygram_reader import (
    domain as epy_domain,
)
from acf.data.readers.epygram_reader import (
    geometry as epy_geometry,
)
from acf.data.readers.epygram_reader import (
    list_fields as epy_list_fields,
)
from acf.data.readers.epygram_reader import (
    metadata as epy_metadata,
)
from acf.data.readers.epygram_reader import (
    open as epy_open,
)
from acf.data.readers.epygram_reader import (
    projection as epy_projection,
)
from acf.data.readers.epygram_reader import (
    read_field as epy_read_field,
)
from acf.data.readers.epygram_reader import (
    read_fields as epy_read_fields,
)
from acf.data.readers.epygram_reader import (
    time_validity as epy_time_validity,
)
from acf.data.readers.epygram_reader import (
    vertical_levels as epy_vertical_levels,
)
from acf.data.universal_ingestion import UniversalDataIngestionEngine
from acf.models.aladin import ALADINIngestionAdapter
from acf.models.arome import AROMEIngestionAdapter
from acf.models.arpege import ARPEGEIngestionAdapter


def test_epygram_import():
    """Verify that epygram can be imported successfully."""
    assert epygram is not None


def test_format_detector_fa_lfa():
    """Verify FormatDetector recognizes FA and LFA extensions."""
    assert FormatDetector.detect("arome_00h.fa") == "FA"
    assert FormatDetector.detect("aladin_run.lfa") == "LFA"
    assert FormatDetector.detect("gfs.grib2") == "GRIB2"
    assert FormatDetector.is_supported("sample.fa") is True
    assert FormatDetector.is_supported("sample.lfa") is True


def test_epygram_reader_nonexistent_file(tmp_path: Path):
    """Test explicit FileNotFoundError when attempting to open a non-existent file."""
    non_existent = tmp_path / "does_not_exist.fa"
    reader = EPyGrAMReader(non_existent)
    with pytest.raises(EPyGrAMFileNotFoundError):
        reader.open()


def test_epygram_reader_unopened_state():
    """Test that calling data extraction methods on unopened reader raises RuntimeError."""
    reader = EPyGrAMReader()
    with pytest.raises(RuntimeError):
        reader.list_fields()
    with pytest.raises(RuntimeError):
        reader.read_field("SURFPRESSION")
    with pytest.raises(RuntimeError):
        reader.metadata()


def test_epygram_reader_strict_not_installed_error(tmp_path: Path, monkeypatch):
    """Test explicit EPyGrAMNotInstalledError when strict_epygram=True and library is missing."""
    fa_file = tmp_path / "dummy.fa"
    fa_file.write_text("DUMMY", encoding="utf-8")

    from acf.data.readers import epygram_reader

    monkeypatch.setattr(epygram_reader, "EPYGRAM_AVAILABLE", False)

    reader = EPyGrAMReader(fa_file)
    with pytest.raises(EPyGrAMNotInstalledError):
        reader.open(strict_epygram=True)


def test_epygram_reader_class_instance(tmp_path: Path):
    """
    Test EPyGrAMReader class methods, context manager, and reading routines
    against a file that is NOT real FA data (dummy text content).

    REWRITTEN: this used to assert a full battery of fabricated data
    (a fixed 6-field list, 90 fake hybrid-pressure levels, and -
    critically - np.random.uniform(...) random "field data" under the
    real field's name) as if it had genuinely been read from this
    dummy text file. Two real bugs made that possible: (1) the reader
    called the non-existent epygram.resources.open(...), so the "real"
    epygram path could never once succeed even with epygram installed
    (fixed: the real API is epygram.open(filename, openmode)); (2)
    every method silently substituted fabricated data on any failure
    instead of reporting the failure. With both fixed, epygram
    genuinely attempts to parse this file, genuinely fails (it is not
    real FA data), and every method now honestly reports that no real
    data was read.
    """
    fa_file = tmp_path / "test_arome.fa"
    fa_file.write_text("DUMMY FA CONTENT", encoding="utf-8")

    reader = EPyGrAMReader(fa_file)
    assert reader.can_read(fa_file) is True

    with reader.open(must_exist=True) as r:
        meta = r.metadata()
        geom = r.geometry()
        proj = r.projection()
        tval = r.time_validity()
        dom = r.domain()
        vlevels = r.vertical_levels()
        fields = r.list_fields()
        f_data = r.read_field("S090TEMPERATURE")
        multi_data = r.read_fields(["S090TEMPERATURE", "SURFPRESSION"])

        assert meta["format"] == "FA"
        assert meta["is_real_data"] is False
        assert "open_failure_reason" in meta  # the genuine epygram parse error is captured
        assert geom["grid_type"] is None
        assert proj is None
        assert tval["valid_time"] is None
        assert dom["bounds"] is None
        assert vlevels == []
        assert fields == []
        assert f_data["field_id"] == "S090TEMPERATURE"  # the request is echoed
        assert f_data["data"] is None  # but no data was fabricated
        assert f_data["status"] == "NOT_READ_NO_REAL_RESOURCE_OPENED"
        assert multi_data["S090TEMPERATURE"]["data"] is None
        assert multi_data["SURFPRESSION"]["data"] is None

    # Ensure reader resource is closed
    assert r._is_open is False


def test_epygram_reader_module_functions(tmp_path: Path):
    """
    Test module-level convenience functions of epygram_reader against a
    file that is NOT real LFA data.

    REWRITTEN: see test_epygram_reader_class_instance's docstring -
    same underlying two bugs, same fix.
    """
    lfa_file = tmp_path / "test_aladin.lfa"
    lfa_file.write_text("DUMMY LFA CONTENT", encoding="utf-8")

    epy_open(lfa_file)
    try:
        fields = epy_list_fields()
        meta = epy_metadata()
        geom = epy_geometry()
        proj = epy_projection()
        tval = epy_time_validity()
        dom = epy_domain()
        vlevels = epy_vertical_levels()
        f_data = epy_read_field("SURFPRESSION")
        multi_data = epy_read_fields(["SURFPRESSION"])

        assert meta["format"] == "LFA"
        assert meta["is_real_data"] is False
        assert fields == []
        assert geom["n_lat"] is None
        assert proj is None
        assert tval["basis_time"] is None
        assert dom["n_lat"] is None
        assert vlevels == []
        assert f_data["field_id"] == "SURFPRESSION"
        assert f_data["data"] is None
        assert multi_data["SURFPRESSION"]["status"] == "NOT_READ_NO_REAL_RESOURCE_OPENED"
    finally:
        epy_close()


def test_epygram_reader_uses_the_real_epygram_api():
    """
    Regression guard: confirm the reader calls a real epygram function
    (epygram.open) rather than the non-existent epygram.resources.open
    that made real reads impossible even with epygram installed.
    """
    assert hasattr(epygram, "open")
    assert not hasattr(epygram.resources, "open")


def test_universal_ingestion_with_epygram(tmp_path: Path):
    """Test universal ingestion engine with FA file."""
    fa_path = tmp_path / "arome_test_cycle.fa"
    fa_path.write_text("ACF AROME TEST DATA", encoding="utf-8")

    ingestion = UniversalDataIngestionEngine()
    dataset = ingestion.ingest(fa_path)

    assert dataset.filetype == "FA"
    assert dataset.has_metadata("epygram")
    assert dataset.has_metadata("geometry")
    assert dataset.has_metadata("fields")


def test_arpege_ingestion_adapter(tmp_path: Path):
    """Test ARPEGE NWP model adapter."""
    arpege_file = tmp_path / "arpege_run.fa"
    arpege_file.write_text("ARPEGE GLOBAL FA DATA", encoding="utf-8")

    adapter = ARPEGEIngestionAdapter()
    assert adapter.detect(arpege_file) is True
    assert "S105TEMPERATURE" in adapter.variables()
    assert len(adapter.levels()) == 105

    res = adapter.read_arpege_file(arpege_file)
    assert res["model"] == "ARPEGE"
    assert res["format"] == "FA"


def test_arome_ingestion_adapter(tmp_path: Path):
    """Test AROME NWP model adapter."""
    arome_file = tmp_path / "arome_run.fa"
    arome_file.write_text("AROME HIGH RES FA DATA", encoding="utf-8")

    adapter = AROMEIngestionAdapter()
    assert adapter.detect(arome_file) is True
    assert "S090TEMPERATURE" in adapter.variables()
    assert len(adapter.levels()) == 90

    res = adapter.read_arome_file(arome_file)
    assert res["model"] == "AROME"
    assert res["geometry"]["resolution_x_meters"] == 1300.0


def test_aladin_ingestion_adapter(tmp_path: Path):
    """Test ALADIN NWP model adapter."""
    aladin_file = tmp_path / "aladin_run.fa"
    aladin_file.write_text("ALADIN REGIONAL FA DATA", encoding="utf-8")

    adapter = ALADINIngestionAdapter()
    assert adapter.detect(aladin_file) is True
    assert "S070TEMPERATURE" in adapter.variables()
    assert len(adapter.levels()) == 70

    res = adapter.read_aladin_file(aladin_file)
    assert res["model"] == "ALADIN"
    assert res["geometry"]["resolution_x_meters"] == 7500.0


def test_fa_adapters_do_not_false_positive_on_shared_extension(tmp_path: Path):
    """
    CORRECTED: ARPEGE, AROME and ALADIN all share the same FA/LFA file
    format, but each adapter's detect() used to also match on that
    bare extension alone (in addition to the model-name substring) -
    so all three would return True for the same ambiguous filename
    with no model name in it, making a shared ModelDetector's result
    depend on arbitrary registry iteration order rather than the
    file's actual model. See each adapter's ingestion_adapter.py.
    """
    ambiguous_file = tmp_path / "run_20260801.fa"
    ambiguous_file.write_text("GENERIC FA DATA", encoding="utf-8")

    assert ARPEGEIngestionAdapter().detect(ambiguous_file) is False
    assert AROMEIngestionAdapter().detect(ambiguous_file) is False
    assert ALADINIngestionAdapter().detect(ambiguous_file) is False

    # The model-name substring itself still works, unaffected.
    assert ARPEGEIngestionAdapter().detect(tmp_path / "arpege_run.fa") is True


def test_can_read_rejects_a_genuine_non_meteorological_extensionless_file(tmp_path: Path):
    """
    NOTE (correction, 2026-09-07): can_read() used to match by
    extension only. Confirmed against a real Météo-France operational
    archive (RESTOR/ALADIN's own FULLPOS_* output, which has no
    extension at all) that this made a genuinely-readable real FA file
    unreachable via ReaderFactory. The fix adds a content-based
    fallback (epygram.formats.guess()) for extensionless files - this
    test checks the fallback doesn't turn into a false-positive trap:
    a real, ordinary non-meteorological file with no extension must
    still be rejected (real epygram, no mocking - it genuinely fails
    to parse this as any known format).
    """
    plain_file = tmp_path / "README"
    plain_file.write_text("just a plain text file, not meteorological data", encoding="utf-8")

    reader = EPyGrAMReader()
    assert reader.can_read(plain_file) is False


def test_can_read_accepts_a_real_fa_file_with_no_extension(tmp_path: Path, monkeypatch):
    """
    Same fix as above, positive case: an extensionless file that
    content-detection genuinely identifies as FA format (the exact
    real-world shape of RESTOR's own FULLPOS_2026083100_0000 - verified
    manually against that real file: epygram.formats.guess() returns
    "FA" for it) must now be recognized. epygram.formats.guess() is
    mocked here only because no real binary FA fixture ships in this
    repo - the real file this is modeled on was independently verified
    by hand, not fabricated from this test's own expectations.
    """
    import epygram.formats

    monkeypatch.setattr(epygram.formats, "guess", lambda filename: "FA")

    extensionless_file = tmp_path / "FULLPOS_2026083100_0000"
    extensionless_file.write_bytes(b"\x00" * 64)

    reader = EPyGrAMReader()
    assert reader.can_read(extensionless_file) is True


def test_read_returns_a_real_dataset_object_not_a_dict(tmp_path: Path):
    """
    NOTE (correction, 2026-09-07 - real bug found one step past the
    can_read() fix above, on the same real RESTOR file): read() used
    to return a plain dict. Every other reader in this factory
    (GRIBReader, NetCDFReader, ...) returns a real
    acf.data.dataset.Dataset, and DatasetRegistry.register() assumes
    one (`dataset.modified = ...`) - a dict has no settable attributes,
    so DataManager.open() crashed with AttributeError on the real file
    even after can_read() correctly found this reader. Uses the same
    dummy-content-so-epygram-honestly-fails pattern as this file's
    other tests (real epygram, real failure, 0 real fields) - proving
    the TYPE of what comes back is now correct without needing a real
    binary FA fixture.
    """
    from acf.data.dataset import Dataset

    fa_file = tmp_path / "arome_test.fa"
    fa_file.write_text("DUMMY FA CONTENT", encoding="utf-8")

    reader = EPyGrAMReader()
    dataset = reader.read(fa_file)

    assert isinstance(dataset, Dataset)
    assert dataset.name == "arome_test"
    assert dataset.filetype == "FA"
    assert dataset.source == "epygram"
    # Real dataset.register() must be able to touch it like any other -
    # this is the exact call that used to crash with AttributeError.
    dataset.touch()
