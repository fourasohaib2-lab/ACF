from pathlib import Path

from acf.data.integration.grib_adapter import GRIBAdapter


def test_adapter():

    adapter = GRIBAdapter()

    adapter.open(Path("/tmp/file.grib"))

    assert adapter.suffix == ".grib"

    assert adapter.is_grib()


def test_not_existing():

    adapter = GRIBAdapter()

    adapter.open(Path("/tmp/model.grb2"))

    assert adapter.exists is False

    assert adapter.is_grib()


def test_load_honestly_discloses_it_is_not_a_real_decode():
    """Regression guard (2026-09-12 ICAO/WMO compliance audit): load()
    used to silently return an empty-but-well-formed Dataset with no
    disclosure - a future real caller could mistake this for genuinely
    decoded (but empty) GRIB content."""
    adapter = GRIBAdapter()

    dataset = adapter.load(Path("/tmp/model.grib"))

    assert dataset.metadata["is_real_data"] is False
    assert dataset.variables == {}
