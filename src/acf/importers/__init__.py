"""
Atmospheric Complexity Framework (ACF)

IMPORTERS - Canonical Package Init

Purpose:
--------
Data importer managers, scientific file readers, format conversion pipelines, and I/O factories.
"""

from typing import Any

from acf.importers.base.base_importer import BaseImporter
from acf.importers.base.base_reader import BaseReader
from acf.importers.factory import ReaderFactory
from acf.importers.hub import ImporterHub
from acf.importers.manager import DataManager, ImporterManager
from acf.importers.readers.bufr_reader import BufrReader
from acf.importers.readers.cf_detector import CFDetector
from acf.importers.registry import ReaderRegistry

__all__ = [
    "BaseImporter",
    "BaseReader",
    "BufrReader",
    "CFDetector",
    "DataManager",
    "ImporterHub",
    "ImporterManager",
    "ReaderFactory",
    "ReaderRegistry",
]

# GRIBReader and NetCDFReader depend on optional third-party libraries
# (cfgrib/eccodes and xarray respectively) that are not always installed.
# ReaderFactory.discover() already tolerates their absence when scanning
# this package dynamically (it wraps each submodule import in try/except),
# but until this fix, importing them unconditionally here meant a missing
# optional dependency raised ImportError partway through this package's
# __init__, leaving `acf.importers` partially initialized in sys.modules.
# That in turn caused an order-dependent import failure observed during the
# August 2026 audit (test_cf_importer.py passed or failed to even collect
# depending on what had already imported `acf.importers` beforehand).
# Importing them defensively here mirrors the factory's tolerance and keeps
# `import acf.importers` reliable regardless of which optional format
# backends are installed.
GRIBReader: type[Any] | None
GribReader: type[Any] | None
NetCDFReader: type[Any] | None

try:
    from acf.importers.readers.grib_reader import GRIBReader, GribReader

    __all__ += ["GRIBReader", "GribReader"]
except ImportError:
    GRIBReader = None
    GribReader = None

try:
    from acf.importers.readers.netcdf_reader import NetCDFReader

    __all__.append("NetCDFReader")
except ImportError:
    NetCDFReader = None
