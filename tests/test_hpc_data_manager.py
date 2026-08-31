"""Unit test suite for the ACF Operational Data Management System (ACF-HPC-107).

hpc_connector.data_management.data_manager.DataManagerEngine and its
helper classes used to fabricate a cascade of fake "validated" data-
processing output (fixed file-processing counts, a fake SHA256 hash,
fake storage metrics, "SUCCESS"/"CATALOGED"/"VALIDATED" statuses)
presented as a real, operational data-management pipeline - the same
fake-stub pattern found and fixed throughout this session, here in a
second, self-contained module of the same shape as
hpc_connector.assimilation.assimilation_engine (also fixed this
session). See data_manager.py's NOTE (correction) docstrings for what
each stage used to fabricate.

(This is a separate test file from tests/test_data_manager.py, which
covers the genuinely real acf.data.manager.DataManager - a different,
unrelated class of the same name in a different module. A prior
uncommitted working-tree change had silently repointed
tests/test_data_manager.py at this hpc_connector module instead,
dropping coverage of the real DataManager; that repointing was
reverted as part of this fix and this dedicated file added instead, so
both real modules keep their own test coverage.)
"""

from acf.hpc_connector.data_management.data_manager import (
    CompressionEngine,
    DataArchiveManager,
    DataIntegrityVerifier,
    DataManagerEngine,
    DataReportGenerator,
    DataTransferManager,
    DatasetCatalog,
    FormatDetector,
    MetadataManager,
    StorageMonitor,
)


def test_format_detector_is_genuinely_real():
    """FormatDetector's extension-based detection is real - confirm it responds to its own input."""
    detector = FormatDetector()
    assert detector.detect_format("file.grib2") == "GRIB2"
    assert detector.detect_format("file.nc") == "NetCDF4"
    assert detector.detect_format("file.bufr") == "BUFR"
    assert detector.detect_format("file.fa") == "FA"
    assert detector.detect_format("file.odb") == "ODB"


def test_metadata_manager_no_longer_fabricates():
    """CORRECTED: used to unconditionally claim fixed AROME/Algerie_Nord metadata for ANY file."""
    meta = MetadataManager()
    m = meta.extract_metadata("file.nc")
    assert m["status"] == "NOT_EXTRACTED_NO_METADATA_READER_INVOKED"
    assert "model" not in m


def test_data_manager_engine_process_file():
    """CORRECTED: used to claim overall "SUCCESS" while metadata extraction was itself fake."""
    engine = DataManagerEngine()
    res = engine.process_file("/tmp/forecast.nc")
    assert res["status"] == "FORMAT_DETECTED_ONLY_NO_METADATA_READER_INVOKED"
    assert res["format"] == "NetCDF4"


def test_storage_and_integrity_no_longer_fabricate():
    """CORRECTED: used to claim fixed storage metrics and a fake SHA256 hash regardless of input."""
    storage = StorageMonitor()
    s = storage.get_storage_metrics()
    assert s["total_files"] is None
    assert s["status"] == "NOT_QUERIED_NO_STORAGE_BACKEND_CONNECTED"

    verifier = DataIntegrityVerifier()
    assert verifier.verify_sha256("/tmp/forecast.nc") is None


def test_archive_transfer_compress_catalog_no_longer_fabricate():
    """CORRECTED: these used to unconditionally claim True/a fake compressed filename/"CATALOGED"."""
    assert DataArchiveManager().archive_dataset("/tmp/forecast.nc") is False
    assert DataTransferManager().transfer("/tmp/a.nc", "/tmp/b.nc") is False
    assert CompressionEngine().compress("/tmp/forecast.nc") is None

    cat = DatasetCatalog().catalog_file("/tmp/forecast.nc")
    assert cat["status"] == "NOT_CATALOGED_NO_CATALOG_REGISTRY_CONNECTED"
    assert cat["file"] == "/tmp/forecast.nc"


def test_report_generator_no_longer_fabricates_or_writes_a_file():
    """CORRECTED: used to claim "8421 files processed, SUCCESS" and write it to /tmp regardless of any real run."""
    report = DataReportGenerator().generate_json_report()
    assert report["status"] == "NOT_GENERATED_NO_FILE_PROCESSING_RUN"
    assert "files_processed" not in report
