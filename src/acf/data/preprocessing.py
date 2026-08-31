"""
Atmospheric Complexity Framework (ACF) - Automated Preprocessing Engine (ACF-NWP-001)

Preprocesses and validates meteorological input datasets (GRIB, GRIB2, NetCDF, BUFR, HDF5,
GeoTIFF, FA, LFI, SYNOP, TEMP, AMDAR, Satellite, Radar) into canonical Dataset objects.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from acf.data.dataset import Dataset
from acf.data.detector import FormatDetector
from acf.data.universal_ingestion import UniversalDataIngestionEngine

logger = logging.getLogger(__name__)

SUPPORTED_DATA_TYPES = [
    "GRIB",
    "GRIB2",
    "NetCDF",
    "BUFR",
    "HDF5",
    "GeoTIFF",
    "FA",
    "LFI",
    "SYNOP",
    "TEMP",
    "AMDAR",
    "Satellite",
    "Radar",
]


class PreprocessingEngine:
    """
    Automated meteorological data preprocessing and validation engine.
    """

    def __init__(
        self, detector: FormatDetector | None = None, ingestion_engine: UniversalDataIngestionEngine | None = None
    ) -> None:
        self.detector = detector if detector else FormatDetector()
        self.ingestion_engine = ingestion_engine if ingestion_engine else UniversalDataIngestionEngine()

    def detect_format(self, filepath: str | Path) -> str:
        """
        Detects data format using FormatDetector.
        """
        fmt = self.detector.detect(filepath)
        return str(fmt).upper()

    def validate_file(self, filepath: str | Path) -> dict[str, Any]:
        """
        Validates file integrity and existence.
        """
        p = Path(filepath)
        if not p.exists():
            return {"valid": False, "reason": f"File does not exist: {filepath}"}
        if p.stat().st_size == 0:
            return {"valid": False, "reason": f"File is empty (0 bytes): {filepath}"}

        fmt = self.detect_format(p)
        return {
            "valid": True,
            "filepath": str(p),
            "format": fmt,
            "size_bytes": p.stat().st_size,
        }

    def preprocess_dataset(self, filepath: str | Path) -> Dataset:
        """
        Preprocesses and ingests input file into a canonical Dataset object.
        """
        val = self.validate_file(filepath)
        if not val["valid"]:
            raise ValueError(f"Preprocessing failed validation: {val.get('reason')}")

        logger.info(f"Preprocessing file {filepath} (Format: {val['format']})")
        dataset = self.ingestion_engine.ingest(filepath)

        # Set preprocessing metadata
        dataset.set_metadata("preprocessed", True)
        dataset.set_metadata("source_format", val["format"])
        return dataset

    def batch_preprocess(self, filepaths: list[str | Path]) -> list[Dataset]:
        """
        Batch preprocesses multiple observation or model input files.
        """
        datasets: list[Dataset] = []
        for fp in filepaths:
            try:
                ds = self.preprocess_dataset(fp)
                datasets.append(ds)
            except Exception as e:
                logger.warning(f"Batch preprocessing skipped {fp}: {e}")
        return datasets
