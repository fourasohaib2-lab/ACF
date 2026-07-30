"""
Atmospheric Complexity Framework (ACF)

IMPORTERS - Canonical Package Init

Purpose:
--------
Data importer managers, scientific file readers, format conversion pipelines, and I/O factories.
"""

from acf.importers.base.base_importer import BaseImporter
from acf.importers.base.base_reader import BaseReader
from acf.importers.factory import ReaderFactory
from acf.importers.hub import ImporterHub
from acf.importers.manager import DataManager, ImporterManager
from acf.importers.readers.bufr_reader import BufrReader
from acf.importers.readers.cf_detector import CFDetector
from acf.importers.readers.grib_reader import GRIBReader, GribReader
from acf.importers.readers.netcdf_reader import NetCDFReader
from acf.importers.registry import ReaderRegistry

__all__ = [
    "BaseImporter",
    "BaseReader",
    "BufrReader",
    "CFDetector",
    "DataManager",
    "GRIBReader",
    "GribReader",
    "ImporterHub",
    "ImporterManager",
    "NetCDFReader",
    "ReaderFactory",
    "ReaderRegistry",
]
