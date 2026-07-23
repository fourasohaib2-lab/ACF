from acf.importers.manager import ImporterManager


def test_importers():

    manager = ImporterManager()

    assert manager.exists("cf")
    assert manager.exists("ecmwf")
    assert manager.exists("wmo")

    assert manager.get("cf") is not None
    assert manager.get("ecmwf") is not None
    assert manager.get("wmo") is not None

    assert manager.names() == ["cf", "ecmwf", "wmo"]

