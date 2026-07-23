from acf.data.manager import DataManager


def test_available_readers():

    manager = DataManager()

    readers = manager.available_readers()

    assert "NetCDFReader" in readers
    assert "GRIBReader" in readers


def test_unknown_extension():

    manager = DataManager()

    try:
        manager.open("demo.xyz")

    except ValueError:

        return

    assert False
