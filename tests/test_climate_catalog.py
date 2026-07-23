from acf.catalog.default_catalog import create_catalog


def test_climate_catalog():

    catalog = create_catalog()

    assert catalog.exists("enso")
    assert catalog.exists("nao")
    assert catalog.exists("ao")
    assert catalog.exists("mjo")

    assert catalog.exists("pm25")
    assert catalog.exists("pm10")
    assert catalog.exists("o3")
    assert catalog.exists("no2")
    assert catalog.exists("so2")
    assert catalog.exists("co")

    assert catalog.exists("co2")
    assert catalog.exists("ch4")

    assert catalog.exists("aod550")

    assert len(catalog.all()) >= 63
