from acf.catalogs.catalog_manager import CatalogManager


def test_catalog_manager():

    manager = CatalogManager()

    manager.register("cf", object())

    assert manager.exists("cf")
    assert manager.count() == 1
    assert "cf" in manager.list_catalogs()
