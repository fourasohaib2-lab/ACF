from acf.importers.manager import ImporterManager


def test_importer_manager():

    manager = ImporterManager()

    assert manager.exists("cf")

    importer = manager.get("cf")

    assert importer is not None

    assert "cf" in manager.names()
