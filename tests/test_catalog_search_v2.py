from acf.catalogs.catalog_manager import CatalogManager
from acf.catalogs.cf.catalog import CFCatalog


def test_catalog_search():

    manager = CatalogManager()

    cf = CFCatalog()
    cf.load()

    manager.register("cf", cf)

    results = manager.search("temperature")

    assert len(results) > 0

