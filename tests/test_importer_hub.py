from acf.importers.hub import ImporterHub


def test_importer_hub():

    hub = ImporterHub()

    assert hub.exists("cf")
    assert hub.exists("ecmwf")
    assert hub.exists("wmo")

    assert hub.get("cf") is not None
    assert hub.get("ecmwf") is not None
    assert hub.get("wmo") is not None

    assert hub.names() == ["cf", "ecmwf", "wmo"]
