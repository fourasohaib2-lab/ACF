from acf.catalog.default_catalog import create_catalog


def test_satellite_catalog():

    catalog = create_catalog()

    assert catalog.exists("bt_ir108")
    assert catalog.exists("cth")
    assert catalog.exists("dbz")
    assert catalog.exists("vrad")
    assert catalog.exists("zdr")
    assert catalog.exists("kdp")
    assert catalog.exists("rhohv")

    assert len(catalog.all()) >= 50
