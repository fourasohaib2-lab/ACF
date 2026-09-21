"""
Tests for acf.importers.readers.grib_reader.GRIBReader against real
GRIB2 data - added while investigating the explicit user request "je
veux que tu ajoutes le dossier RESTOR pour testé tout le projet acf et
awci avec des vrais données" (RESTOR itself is machine-local, not
reachable from this remote session - see docs/awci/AWCI_REAL_ARCHIVE_DATA.md
and this session's own conversation; ECMWF Open Data / NOAA GFS were
used instead as a genuinely real, freely-licensed, network-downloadable
alternative NWP data source).

Running this reader against a real file (not the pre-existing
tests/test_grib_reader.py, which only exercises a different,
never-opens-a-real-file compatibility class,
acf.data.grib_reader.GribReader) surfaced 2 real, previously
undetected bugs in GRIBReader.read(), now fixed (see that method's own
"NOTE (correction)" docstrings):

1. `dataset.add_variable(variable)` was called with only the
   variable's real NAME, never its real decoded array - every real
   variable's value was silently `None`. Coordinate arrays (latitude/
   longitude) were never registered at all.
2. Per-variable `units`/`standard_name`/`long_name` metadata (cfgrib
   decodes all 3 from the real GRIB message) was never recorded,
   unlike the sibling `NetCDFReader`.

Together, these meant `awci.data.model_import.
compute_awci_from_imported_dataset()` (the real engine behind the
GUI's "📂 Import Model File" button) could never actually compute a
real AWCI score from any real GRIB file - every point extraction
silently found nothing. This file locks in the fix with a real,
downloaded GRIB2 file.

All tests here require a real, downloaded GRIB2 file to be present
under data/real_nwp/ (gitignored - not part of the repository, session-
local only) and are honestly SKIPPED, not faked or mocked, when it is
absent - matching tests/test_awci_archive_field.py's own established
"real data or an honest gap, never a substitute" discipline for RESTOR.

To (re)download a real, small, free NOAA GFS subset covering a
North-Africa/Europe subregion (~300KB, no API key required)::

    D=$(date -u +%Y%m%d); R=00
    curl -o data/real_nwp/noaa_gfs/gfs_${D}_${R}z_f000_europe_nafrica.grib2 \\
      "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t${R}z.pgrb2.0p25.f000&lev_2_m_above_ground=on&lev_10_m_above_ground=on&lev_surface=on&lev_mean_sea_level=on&var_TMP=on&var_UGRD=on&var_VGRD=on&var_PRMSL=on&var_RH=on&subregion=&leftlon=-15&rightlon=40&toplat=55&bottomlat=10&dir=%2Fgfs.${D}%2F${R}%2Fatmos"
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from acf.importers.readers.grib_reader import GRIBReader

_REAL_NWP_DIR = Path(__file__).resolve().parents[1] / "data" / "real_nwp"
_REAL_GFS_FILES = sorted(_REAL_NWP_DIR.glob("noaa_gfs/gfs_*_f000_*.grib2")) if _REAL_NWP_DIR.exists() else []
REAL_GFS_FILE = _REAL_GFS_FILES[0] if _REAL_GFS_FILES else None

pytestmark = pytest.mark.skipif(
    REAL_GFS_FILE is None,
    reason="No real, downloaded GFS GRIB2 file present under data/real_nwp/noaa_gfs/ "
    "(session-local, not part of the repository) - see this module's own docstring to fetch one",
)


@pytest.fixture(scope="module")
def real_dataset():
    return GRIBReader().read(REAL_GFS_FILE)


def test_real_grib_file_is_genuinely_grib2():
    with open(REAL_GFS_FILE, "rb") as fh:
        header = fh.read(4)
    assert header == b"GRIB"


def test_grib_reader_stores_real_variable_values_not_just_names(real_dataset):
    real_t2m = real_dataset.get_variable("t2m")
    assert real_t2m is not None
    arr = np.asarray(real_t2m, dtype=float)
    # Real 2m temperature over a Europe/North-Africa domain: a sane
    # real-world Kelvin range, not a fabricated/placeholder constant.
    assert arr.size > 0
    assert 230.0 < arr.mean() < 330.0


def test_grib_reader_stores_real_coordinate_arrays(real_dataset):
    lat = real_dataset.get_variable("latitude")
    lon = real_dataset.get_variable("longitude")
    assert lat is not None
    assert lon is not None
    lat_arr = np.asarray(lat, dtype=float)
    lon_arr = np.asarray(lon, dtype=float)
    assert lat_arr.min() >= 10.0 - 1e-6
    assert lat_arr.max() <= 55.0 + 1e-6
    assert lon_arr.size > 1


def test_grib_reader_stores_real_units_metadata(real_dataset):
    assert real_dataset.metadata.get("t2m_units") == "K"
    assert real_dataset.metadata.get("prmsl_units") == "Pa"
    assert real_dataset.metadata.get("t2m_standard_name") == "air_temperature"


def test_real_grib_dataset_feeds_a_real_awci_computation(real_dataset):
    """End-to-end: a real, freshly-downloaded GFS GRIB2 file, read
    through the real GRIBReader, feeds a real awci.data.model_import.
    compute_awci_from_imported_dataset() call at a real point (Paris,
    inside this file's real subregion) - proving the full
    read -> extract -> AWCICalculator chain works with genuine,
    externally-sourced real data."""
    from awci.data.model_import import compute_awci_from_imported_dataset

    output = compute_awci_from_imported_dataset(real_dataset, lat=48.85, lon=2.35, level_hpa=850.0)

    matched = output["extraction"]["matched_variables"]
    assert "temperature" in matched
    assert "pressure" in matched

    temperature_k = output["extraction"]["inputs"]["temperature"]
    assert 230.0 < temperature_k < 330.0  # a real, physically sane 2m temperature

    assert 0.0 <= output["result"]["awci"] <= 100.0
    assert output["result"]["level"] in {
        "Very Low",
        "Low",
        "Moderate",
        "High",
        "Very High",
        "Extreme",
    }
