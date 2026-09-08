"""
Unit test suite for hpc_connector.assimilation's package-level stub
classes (ACF-HPC-106).

REWRITTEN: every class in this package used to unconditionally claim a
trivial "success" result (True/"OK"/an empty-but-valid list or dict)
regardless of any real input or backend connected - the same fake-stub
pattern found and fixed throughout this session, here in classes with
no real callers or prior test coverage (verified) but genuinely
safety-relevant if ever wired into a real pipeline (a station that
should be blacklisted would never be filtered; QC that should reject
bad data would never reject anything). See
hpc_connector/assimilation/__init__.py's NOTE (correction) docstrings
for what each used to fabricate.
"""

import pytest

from acf.hpc_connector.assimilation import (
    AircraftReader,
    AssimilationReport,
    AssimilationScheduler,
    BuoyReader,
    GnssReader,
    LightningReader,
    ObservationBlacklist,
    ObservationConverter,
    ObservationDatabase,
    ObservationMonitor,
    ObservationPipeline,
    ObservationQualityControl,
    ObservationScanner,
    ObservationStatistics,
    ObservationValidator,
    ProfilerReader,
    QCRules,
    RadarReader,
    RadiosondeReader,
    SatelliteReader,
    ShipReader,
    SynopReader,
)


def test_readers_no_longer_claim_a_successful_read():
    for reader_cls in (
        SynopReader,
        RadiosondeReader,
        AircraftReader,
        RadarReader,
        SatelliteReader,
        GnssReader,
        ProfilerReader,
        LightningReader,
        ShipReader,
        BuoyReader,
    ):
        assert reader_cls().read() == []


def test_scanner_and_database_return_empty_not_fabricated_results():
    assert ObservationScanner().scan() == []
    assert ObservationDatabase().query() == []


def test_validator_and_converter_no_longer_claim_success():
    # CORRECTED: used to unconditionally claim True regardless of any
    # real validation/conversion performed.
    assert ObservationValidator().validate() is False
    assert ObservationConverter().convert() is False


def test_quality_control_and_statistics_no_longer_fabricate():
    qc = ObservationQualityControl().process()
    assert qc["status"] == "NOT_PROCESSED_NO_QC_BACKEND_CONNECTED"

    stats = ObservationStatistics().compute()
    assert stats["status"] == "NOT_COMPUTED_NO_OBSERVATION_DATA_CONNECTED"


def test_blacklist_no_longer_silently_says_never_blacklisted():
    """
    CORRECTED (safety-relevant): used to unconditionally claim False
    (never blacklisted) for ANY station_id, with no real blacklist
    registry connected - a genuinely bad station would never be
    filtered. Now honestly raises rather than silently answering.
    """
    with pytest.raises(NotImplementedError):
        ObservationBlacklist().is_blacklisted("00000")


def test_qc_rules_no_longer_always_pass():
    """CORRECTED (safety-relevant): used to unconditionally claim True (always passes QC)."""
    assert QCRules().check() is False


def test_monitor_pipeline_report_and_scheduler_no_longer_fabricate():
    assert ObservationMonitor().monitor() == "NOT_MONITORED_NO_BACKEND_CONNECTED"
    assert ObservationPipeline().run() is False
    assert AssimilationReport().build()["status"] == "NOT_BUILT_NO_ASSIMILATION_DATA_CONNECTED"
    assert AssimilationScheduler().schedule() is None
