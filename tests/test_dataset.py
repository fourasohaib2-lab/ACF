from pathlib import Path

from acf.data.dataset import Dataset


def test_dataset_creation():

    ds = Dataset(
        name="WRF",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    assert ds.name == "WRF"
    assert ds.filetype == "NetCDF"


def test_add_variable():

    ds = Dataset(
        name="Demo",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    ds.add_variable("Temperature")
    ds.add_variable("Pressure")

    assert len(ds.variables) == 2


def test_dimension():

    ds = Dataset(
        name="Demo",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    ds.set_dimension("time", 24)

    assert ds.dimensions["time"] == 24


def test_dataset():

    ds = Dataset()

    ds.add_variable("temperature", [290.0])

    assert ds.get_variable("temperature") == [290.0]
