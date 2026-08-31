from acf.catalogs.catalog_manager import CatalogManager


class DummyCatalog:
    pass


def test_catalog_manager():

    manager = CatalogManager()

    manager.register("cf", DummyCatalog())
    manager.register("ecmwf", DummyCatalog())

    assert manager.count() == 2

    assert manager.exists("cf")

    assert manager.exists("ecmwf")

    assert len(manager.names()) == 2

    manager.remove("cf")

    assert manager.count() == 1

    manager.clear()

    assert manager.count() == 0
