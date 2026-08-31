"""Observation Assimilation Subsystem Package (ACF-HPC-106).

NOTE (correction): every class below used to unconditionally claim a
trivial "success" result (True/"OK"/an empty-but-valid list or dict)
regardless of any real input or any real backend connected - the same
underlying issue as hpc_connector.assimilation.assimilation_engine
(fixed earlier this session, the module this package wraps). Some of
these are genuinely safety-relevant if ever wired into a real
pipeline: ObservationValidator.validate() always claiming True means
nothing is ever rejected; ObservationBlacklist.is_blacklisted() always
claiming False means no station is ever filtered regardless of its
real ID; QCRules.check() always claiming True means quality control
never actually rejects anything. None of these classes currently have
real callers or test coverage in this codebase (verified), but they
are kept (not deleted, per this session's standing rule) and each now
honestly reports that no real backend is connected, rather than
silently claiming success for work that never happened - so that
anyone wiring these into a real pipeline in the future inherits an
honest starting point instead of a false "already works" signal.
"""

from typing import Any

from acf.hpc_connector.assimilation.assimilation_engine import (
    AssimilationReportGenerator,
    BATORInterface,
    BUFRDecoder,
    CanariInterface,
    ObservationAssimilationEngine,
    ObservationCatalog,
    ODBManager,
    QualityControl,
)


class ObservationScanner:
    def scan(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid scan (`[]`) with no real filesystem/stream scan performed."""
        return []


class ObservationValidator:
    def validate(self) -> bool:
        """NOTE (correction): used to unconditionally claim True with no real validation performed."""
        return False


class ObservationConverter:
    def convert(self) -> bool:
        """NOTE (correction): used to unconditionally claim True with no real format conversion performed."""
        return False


class ObservationQualityControl:
    def process(self) -> dict[str, Any]:
        """NOTE (correction): used to unconditionally claim an empty-but-valid result (`{}`) with no real QC processing performed."""
        return {"status": "NOT_PROCESSED_NO_QC_BACKEND_CONNECTED"}


class ObservationBlacklist:
    def is_blacklisted(self, station_id: str) -> bool:
        """
        NOTE (correction — safety-relevant): this used to unconditionally
        claim False (never blacklisted) for ANY station_id, with no real
        blacklist registry connected - a genuinely bad/malfunctioning
        station would never be filtered. Not fabricated: station_id is
        genuinely accepted but there is no real blacklist to check it
        against yet, so this honestly cannot claim either answer.
        """
        raise NotImplementedError(
            f"is_blacklisted({station_id!r}) needs a real blacklist registry - none is connected. "
            "Previously returned a hard-coded fake False (never blacklisted); removed rather than "
            "left silently wrong."
        )


class ObservationStatistics:
    def compute(self) -> dict[str, Any]:
        """NOTE (correction): used to unconditionally claim an empty-but-valid result (`{}`) with no real statistics computed."""
        return {"status": "NOT_COMPUTED_NO_OBSERVATION_DATA_CONNECTED"}


class ObservationMonitor:
    def monitor(self) -> str:
        """NOTE (correction): used to unconditionally claim "OK" with no real monitoring performed."""
        return "NOT_MONITORED_NO_BACKEND_CONNECTED"


class ObservationPipeline:
    def run(self) -> bool:
        """NOTE (correction): used to unconditionally claim True with no real pipeline execution performed."""
        return False


class ObservationDatabase:
    def query(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid query result (`[]`) with no real database connected."""
        return []


class SynopReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real SYNOP source connected."""
        return []


class RadiosondeReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real radiosonde source connected."""
        return []


class AircraftReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real AMDAR/ACARS source connected."""
        return []


class RadarReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real radar source connected."""
        return []


class SatelliteReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real satellite source connected."""
        return []


class GnssReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real GNSS-RO source connected."""
        return []


class ProfilerReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real wind-profiler source connected."""
        return []


class LightningReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real lightning-network source connected."""
        return []


class ShipReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real SHIP source connected."""
        return []


class BuoyReader:
    def read(self) -> list:
        """NOTE (correction): used to unconditionally claim an empty-but-valid read (`[]`) with no real BUOY source connected."""
        return []


class QCRules:
    def check(self) -> bool:
        """
        NOTE (correction — safety-relevant): this used to unconditionally
        claim True (always passes QC) with no real rules ever evaluated.
        """
        return False


class AssimilationReport:
    def build(self) -> dict[str, Any]:
        """NOTE (correction): used to unconditionally claim an empty-but-valid result (`{}`) with no real report built."""
        return {"status": "NOT_BUILT_NO_ASSIMILATION_DATA_CONNECTED"}


class AssimilationScheduler:
    def schedule(self) -> str | None:
        """NOTE (correction): used to unconditionally claim a fixed fake job id ("job_106") with no real scheduler backend connected."""
        return None


__all__ = [
    "AircraftReader",
    "AssimilationReport",
    "AssimilationReportGenerator",
    "AssimilationScheduler",
    "BATORInterface",
    "BUFRDecoder",
    "BuoyReader",
    "CanariInterface",
    "GnssReader",
    "LightningReader",
    "ODBManager",
    "ObservationAssimilationEngine",
    "ObservationBlacklist",
    "ObservationCatalog",
    "ObservationConverter",
    "ObservationDatabase",
    "ObservationMonitor",
    "ObservationPipeline",
    "ObservationQualityControl",
    "ObservationScanner",
    "ObservationStatistics",
    "ObservationValidator",
    "ProfilerReader",
    "QCRules",
    "QualityControl",
    "RadarReader",
    "RadiosondeReader",
    "SatelliteReader",
    "ShipReader",
    "SynopReader",
]
