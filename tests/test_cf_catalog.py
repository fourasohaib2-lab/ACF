from acf.catalogs.cf.catalog import CFCatalog


def test_cf_catalog():

    catalog = CFCatalog()

    catalog.load()

    assert catalog.count() > 0

    assert catalog.exists("air_temperature")

    assert catalog.get("air_temperature")["unit"] == "K"

    assert "air_temperature" in catalog.list()
