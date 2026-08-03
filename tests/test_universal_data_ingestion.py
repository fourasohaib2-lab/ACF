"""
Atmospheric Complexity Framework (ACF)

Universal Earth Observation Data Ingestion Test Suite (MISSION ACF-026)
"""

from pathlib import Path
from acf.data.detector import FormatDetector
from acf.data.universal_ingestion import UniversalDataIngestionEngine
from acf.science.query_engine import ScientificQueryEngine, ask


def test_format_detector_extensions():
    """Test du détecteur automatique de formats Earth Observation."""
    assert FormatDetector.detect("sample.grib2") == "GRIB2"
    assert FormatDetector.detect("sample.nc4") == "NETCDF"
    assert FormatDetector.detect("sample.bufr") == "BUFR"
    assert FormatDetector.detect("sample.h5") == "HDF5"
    assert FormatDetector.detect("sample.cog") == "GEOTIFF"
    assert FormatDetector.detect("sample.geojson") == "JSON"
    assert FormatDetector.detect("sample.kml") == "XML"
    assert FormatDetector.detect("sample.zarr") == "ZARR"
    assert FormatDetector.detect("sample.parquet") == "PARQUET"
    assert FormatDetector.detect("sample.arrow") == "ARROW"


def test_universal_data_ingestion_engine():
    """Test de l'ingestion universelle et création du Dataset canonique."""
    engine = UniversalDataIngestionEngine()
    dataset = engine.ingest("sample_ifs_forecast.grib2", dataset_name="IFS_Global_12Z")

    assert dataset.name == "IFS_Global_12Z"
    assert dataset.filetype == "GRIB2"
    assert dataset.validated is True
    assert len(dataset.variables) >= 5
    assert dataset.has_variable("temperature")
    assert dataset.has_variable("CAPE")

    # Métadonnées extraites
    spatial_meta = dataset.get_metadata("spatial")
    assert spatial_meta["crs"] == "EPSG:4326"
    assert "bounding_box" in spatial_meta

    # Cartographie automatique des paramètres
    mappings = dataset.get_metadata("parameter_mappings")
    assert "temperature" in mappings
    assert mappings["temperature"]["cf_standard_name"] == "air_temperature"
    assert mappings["temperature"]["grib2_code"] == "0,0,0"

    assert "CAPE" in mappings
    assert mappings["CAPE"]["cf_standard_name"] == "atmosphere_convective_available_potential_energy"


def test_query_engine_phase14_ingestion_questions():
    """Test le ScientificQueryEngine sur les questions d'ingestion de données de la mission ACF-026."""
    q_engine = ScientificQueryEngine()

    # 1. Which variables exist in this GRIB?
    r1 = q_engine.ask("Which variables exist in this GRIB?")
    assert "grib_variables" in r1
    assert any("Temperature" in v for v in r1["grib_variables"])

    # 2. What CF standard names are available?
    r2 = q_engine.ask("What CF standard names are available?")
    assert "available_cf_standard_names" in r2
    assert "air_temperature (K)" in r2["available_cf_standard_names"]

    # 3. Which datasets contain CAPE?
    r3 = q_engine.ask("Which datasets contain CAPE?")
    assert "datasets_with_cape" in r3
    assert any("ERA5" in d or "AROME" in d for d in r3["datasets_with_cape"])

    # 4. Which files contain radar reflectivity?
    r4 = q_engine.ask("Which files contain radar reflectivity?")
    assert "radar_file_formats" in r4
    assert any("HDF5" in f for f in r4["radar_file_formats"])

    # 5. Which observations come from METAR?
    r5 = q_engine.ask("Which observations come from METAR?")
    assert "metar_variables" in r5
    assert any("Visibility" in v or "Cloud" in v for v in r5["metar_variables"])
