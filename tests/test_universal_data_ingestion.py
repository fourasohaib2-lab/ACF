"""
Atmospheric Complexity Framework (ACF)

Universal Earth Observation Data Ingestion Test Suite (MISSION ACF-026)
"""

from acf.data.detector import FormatDetector
from acf.data.universal_ingestion import UniversalDataIngestionEngine
from acf.science.query_engine import ScientificQueryEngine


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
    """
    Test de l'ingestion universelle et création du Dataset canonique.

    REWRITTEN: this used to assert that ingesting a GRIB2 path that
    doesn't even exist on disk ("sample_ifs_forecast.grib2" is a bare
    string, not a real file - no tmp_path used) produced a fully
    "validated" dataset with 6 specific variables (temperature,
    pressure, humidity, CAPE, wind_u, wind_v) and a global 1deg grid -
    the exact same fixed metadata regardless of what file was actually
    named, because _extract_spatial_metadata()/
    _extract_temporal_metadata()/_detect_and_map_variables() (fixed
    this session) never looked at the file at all. No real GRIB2
    reader is wired up here (unlike the FA/LFA/LFI path, which
    genuinely uses EPyGrAMReader, also fixed this session), so
    ingestion now honestly reports that nothing was extracted.
    """
    engine = UniversalDataIngestionEngine()
    dataset = engine.ingest("sample_ifs_forecast.grib2", dataset_name="IFS_Global_12Z")

    assert dataset.name == "IFS_Global_12Z"
    assert dataset.filetype == "GRIB2"
    assert dataset.validated is False  # no variables were genuinely detected
    assert dataset.errors == ["No variables ingested"]
    assert dataset.variables == {}

    # Métadonnées extraites (honnêtement vides - aucun lecteur GRIB2 réel connecté)
    spatial_meta = dataset.get_metadata("spatial")
    assert spatial_meta["crs"] is None
    assert spatial_meta["status"] == "NOT_EXTRACTED_NO_GRID_READER_WIRED_FOR_THIS_FORMAT"

    # Cartographie automatique des paramètres : rien à cartographier
    mappings = dataset.get_metadata("parameter_mappings")
    assert mappings == {}


def test_universal_data_ingestion_provenance_echoes_real_input():
    """provenance's source_file/format are genuinely derived from the real call arguments."""
    engine = UniversalDataIngestionEngine()
    dataset = engine.ingest("another_sample.nc4", dataset_name="Another_Dataset")

    provenance = dataset.get_metadata("provenance")
    assert provenance["source_file"] == "another_sample.nc4"
    assert provenance["format"] == dataset.filetype
    assert provenance["institution"] is None  # no longer a fabricated guess


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
