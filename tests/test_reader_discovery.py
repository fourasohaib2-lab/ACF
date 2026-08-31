from acf.data.factory import ReaderFactory


def test_discovery():

    factory = ReaderFactory()

    readers = [reader.__class__.__name__ for reader in factory.readers()]

    assert "NetCDFReader" in readers
    assert "GRIBReader" in readers
