from pathlib import Path

from acf.data.integration.adapter_factory import AdapterFactory


def test_factory_netcdf():

    factory = AdapterFactory()

    ds = factory.load(Path("/tmp/test.nc"))

    assert ds.filetype == "NetCDF"


def test_factory_grib():

    factory = AdapterFactory()

    ds = factory.load(Path("/tmp/test.grib"))

    assert ds.filetype == "GRIB"


def test_factory_bufr():

    factory = AdapterFactory()

    ds = factory.load(Path("/tmp/test.bufr"))

    assert ds.filetype == "BUFR"


def test_factory_json():

    factory = AdapterFactory()

    ds = factory.load(Path("/tmp/test.json"))

    assert ds.filetype == "JSON"


def test_factory_csv():

    factory = AdapterFactory()

    ds = factory.load(Path("/tmp/test.csv"))

    assert ds.filetype == "CSV"


def test_factory_unknown():

    factory = AdapterFactory()

    try:

        factory.load(Path("/tmp/test.xyz"))

    except ValueError:

        assert True

    else:

        assert False
