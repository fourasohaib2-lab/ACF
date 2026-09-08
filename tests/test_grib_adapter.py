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
