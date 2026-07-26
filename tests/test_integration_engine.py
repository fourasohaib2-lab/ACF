from pathlib import Path

from acf.data.integration.integration_engine import IntegrationEngine


def test_create_dataset():

    engine = IntegrationEngine()

    ds = engine.create_dataset(
        name="ERA5",
        filepath=Path("/tmp/era5.nc"),
        filetype="NetCDF",
    )

    assert ds.name == "ERA5"
    assert ds.filetype == "NetCDF"
    assert engine.loaded


def test_summary():

    engine = IntegrationEngine()

    engine.create_dataset(
        name="ERA5",
        filepath=Path("/tmp/era5.nc"),
        filetype="NetCDF",
    )

    summary = engine.summary()

    assert summary["name"] == "ERA5"
    assert summary["filetype"] == "NetCDF"


def test_unload():

    engine = IntegrationEngine()

    engine.create_dataset(
        name="ERA5",
        filepath=Path("/tmp/era5.nc"),
        filetype="NetCDF",
    )

    engine.unload()

    assert not engine.loaded
