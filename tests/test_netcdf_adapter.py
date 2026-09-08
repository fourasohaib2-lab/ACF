from pathlib import Path

from acf.data.integration.netcdf_adapter import NetCDFAdapter


def test_adapter():

    adapter = NetCDFAdapter()

    adapter.open(Path("/tmp/file.nc"))

    assert adapter.suffix == ".nc"

    assert adapter.is_netcdf()


def test_not_existing():

    adapter = NetCDFAdapter()

    adapter.open(Path("/tmp/unknown.nc"))

    assert adapter.exists is False
