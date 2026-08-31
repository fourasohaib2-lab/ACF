from acf.standards.manager import StandardsManager


def test_manager():

    manager = StandardsManager()

    manager.register("cf", object())
    manager.register("ecmwf", object())

    assert manager.exists("cf")
    assert manager.exists("ecmwf")
    assert manager.count() == 2
    assert manager.names() == ["cf", "ecmwf"]
