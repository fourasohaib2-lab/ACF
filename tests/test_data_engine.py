from pathlib import Path

from acf.data.engine import DataEngine


def test_create_dataset():

    engine = DataEngine()

    ds = engine.create_dataset(
        name="WRF",
        filepath=Path("/tmp/wrfout.nc"),
        filetype="NetCDF",
    )

    assert ds.name == "WRF"
    assert ds.filetype == "NetCDF"
