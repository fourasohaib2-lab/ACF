from acf.catalogs.catalog_manager import CatalogManager
from acf.catalogs.cf.catalog import CFCatalog


def test_catalog_search():

    manager = CatalogManager()

    cf = CFCatalog()
    cf.load()

    manager.register("cf", cf)

    parameter = manager.find("air_temperature")

    assert parameter is not None
