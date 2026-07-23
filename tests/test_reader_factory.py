from acf.data.factory import ReaderFactory


def test_factory_creation():

    factory = ReaderFactory()

    assert len(factory.readers()) >= 2


def test_factory_reader():

    factory = ReaderFactory()

    reader = factory.get_reader("demo.nc")

    assert reader is not None


def test_factory_unknown():

    factory = ReaderFactory()

    reader = factory.get_reader("demo.abc")

    assert reader is None
