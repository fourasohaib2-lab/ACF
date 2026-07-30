"""
Tests for ACF-016 Importers Consolidation & Compatibility Shims
"""

import pytest

from acf.importers import (
    BaseImporter,
    BaseReader,
    BufrReader,
    CFDetector,
    DataManager,
    GRIBReader,
    GribReader,
    ImporterHub,
    ImporterManager,
    NetCDFReader,
    ReaderFactory,
    ReaderRegistry,
)

from acf.io import (
    BaseReader as IOBaseReader,
    ReaderFactory as IOReaderFactory,
    ReaderRegistry as IOReaderRegistry,
    DataManager as IODataManager,
)

from acf.data.readers import (
    BaseReader as DataBaseReader,
    NetCDFReader as DataNetCDFReader,
    GRIBReader as DataGRIBReader,
    CFDetector as DataCFDetector,
)

from acf.data.bufr_reader import BufrReader as DirectBufrReader
from acf.data.grib_reader import GribReader as DirectGribReader
from acf.data.netcdf_reader import NetCDFReader as DirectNetCDFReader
from acf.data.factory import ReaderFactory as DirectReaderFactory
from acf.standards.ecmwf.loader import ECMWFLoader


def test_canonical_imports():
    assert BaseImporter is not None
    assert BaseReader is not None
    assert ImporterHub is not None
    assert ImporterManager is not None
    assert ReaderFactory is not None
    assert NetCDFReader is not None
    assert GRIBReader is not None
    assert GribReader is not None
    assert BufrReader is not None
    assert CFDetector is not None
    assert DataManager is not None
    assert ReaderRegistry is not None


def test_compatibility_shims_io():
    assert IOBaseReader is BaseReader
    assert IOReaderFactory is ReaderFactory
    assert IOReaderRegistry is ReaderRegistry
    assert IODataManager is DataManager


def test_compatibility_shims_data_readers():
    assert DataBaseReader is BaseReader
    assert DataNetCDFReader is NetCDFReader
    assert DataGRIBReader is GRIBReader
    assert DataCFDetector is CFDetector


def test_compatibility_shims_direct_data():
    assert DirectBufrReader is BufrReader
    assert DirectGribReader is GribReader
    assert DirectNetCDFReader is NetCDFReader
    assert DirectReaderFactory is ReaderFactory


def test_compatibility_shims_standards():
    loader = ECMWFLoader()
    assert hasattr(loader, "load")
    assert hasattr(loader, "validate")


def test_importer_hub_canonical():
    hub = ImporterHub()
    assert hub.exists("cf")
    assert hub.exists("ecmwf")
    assert hub.exists("wmo")
    assert "cf" in hub.names()


def test_reader_factory_discovery_canonical():
    factory = ReaderFactory()
    readers = [r.__class__.__name__ for r in factory.readers()]
    assert "NetCDFReader" in readers
    assert "GRIBReader" in readers
