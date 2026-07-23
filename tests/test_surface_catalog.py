from acf.catalog.default_catalog import create_catalog


def test_surface():

    catalog = create_catalog()

    assert catalog.exists("t2m")
    assert catalog.exists("rh")
    assert catalog.exists("tp")
    assert catalog.exists("u10")
    assert catalog.exists("soil_moisture")

    assert len(catalog.all()) >= 16
