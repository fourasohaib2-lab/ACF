from acf.catalog.default_catalog import create_catalog


def test_ocean_catalog():

    catalog = create_catalog()

    assert catalog.exists("sst")
    assert catalog.exists("sss")
    assert catalog.exists("uo")
    assert catalog.exists("vocean")
    assert catalog.exists("swh")
    assert catalog.exists("mwd")
    assert catalog.exists("mwp")
    assert catalog.exists("sic")
    assert catalog.exists("sit")

    assert len(catalog.all()) >= 39

