from acf.catalogs.hub import CatalogHub


def test_catalog_hub():

    hub = CatalogHub()

    hub.load_cf()

    assert "cf" in hub.list_catalogs()

    parameter = hub.find("air_temperature")

    assert parameter is not None
