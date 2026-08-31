"""
Atmospheric Complexity Framework (ACF) - Universal Data Reader (ACF-100)

Provides a unified data reader API supporting GRIB1, GRIB2, FA, LFA, LFI, NetCDF,
HDF5, BUFR, GeoTIFF, Shapefile, GeoPackage, CSV, JSON, Zarr, Parquet.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from acf.data.dataset import Dataset
from acf.data.detector import FormatDetector
from acf.data.universal_ingestion import UniversalDataIngestionEngine

logger = logging.getLogger(__name__)


class UniversalReader:
    """
    Universal Data Reader providing a single entry point dataset = reader.open(filepath).
    """

    def __init__(
        self, detector: FormatDetector | None = None, ingestion_engine: UniversalDataIngestionEngine | None = None
    ) -> None:
        self.detector = detector if detector else FormatDetector()
        self.ingestion_engine = ingestion_engine if ingestion_engine else UniversalDataIngestionEngine()

    def open(self, filepath: str | Path, **kwargs: Any) -> Dataset:
        """
        Opens and ingests any supported scientific data file into a canonical Dataset object.
        """
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        fmt = str(self.detector.detect(p)).upper()
        logger.info(f"Opening dataset '{p.name}' with detected format {fmt}")

        dataset = self.ingestion_engine.ingest(p)
        dataset.set_metadata("reader", "UniversalReader")
        dataset.set_metadata("format", fmt)
        return dataset

    def read_metadata(self, filepath: str | Path) -> dict[str, Any]:
        """
        Extracts metadata header without loading full array into memory.
        """
        ds = self.open(filepath)
        return ds.metadata if hasattr(ds, "metadata") else {}
