from typing import ClassVar

from acf.io.base_reader import BaseReader
from acf.io.factory import ReaderFactory
from acf.io.registry import ReaderRegistry


class DummyReader(BaseReader):
    extensions: ClassVar[list[str]] = [".abc"]

    def can_read(self, filename):

        return filename.endswith(".abc")

    def read(self, filename):

        return {"file": filename}


def test_registry():

    registry = ReaderRegistry()

    registry.register(DummyReader())

    assert registry.count() == 1


def test_factory():

    registry = ReaderRegistry()

    registry.register(DummyReader())

    factory = ReaderFactory(registry)

    reader = factory.get_reader("sample.abc")

    assert reader is not None


def test_reader():

    registry = ReaderRegistry()

    registry.register(DummyReader())

    factory = ReaderFactory(registry)

    reader = factory.get_reader("sample.abc")

    data = reader.read("sample.abc")

    assert data["file"] == "sample.abc"
