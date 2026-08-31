from acf.standards.ecmwf.manager import ECMWFManager


def test_manager():

    manager = ECMWFManager()

    parameters = manager.load("src/acf/resources/standards/ecmwf/parameters.json")

    assert len(parameters) >= 4
    assert parameters[0].code == "t2m"
