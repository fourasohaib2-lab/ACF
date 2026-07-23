#!/usr/bin/env bash

set -e

PROJECT="$HOME/ACF"

echo "==========================================="
echo " Sprint 11 - Partie 1"
echo " Universal Reader Framework"
echo "==========================================="

mkdir -p "$PROJECT/src/acf/io/readers"

touch "$PROJECT/src/acf/io/__init__.py"
touch "$PROJECT/src/acf/io/readers/__init__.py"

####################################################
# BASE READER
####################################################

cat > "$PROJECT/src/acf/io/base_reader.py" << 'EOF'
from abc import ABC, abstractmethod


class BaseReader(ABC):

    extensions = []

    @abstractmethod
    def can_read(self, filename: str) -> bool:
        pass

    @abstractmethod
    def read(self, filename: str):
        pass
EOF

####################################################
# REGISTRY
####################################################

cat > "$PROJECT/src/acf/io/registry.py" << 'EOF'
class ReaderRegistry:

    def __init__(self):

        self._readers = []

    def register(self, reader):

        self._readers.append(reader)

    def readers(self):

        return list(self._readers)

    def count(self):

        return len(self._readers)
EOF

####################################################
# FACTORY
####################################################

cat > "$PROJECT/src/acf/io/factory.py" << 'EOF'
class ReaderFactory:

    def __init__(self, registry):

        self.registry = registry

    def get_reader(self, filename):

        for reader in self.registry.readers():

            if reader.can_read(filename):
                return reader

        return None
EOF

####################################################
# DATA MANAGER
####################################################

cat > "$PROJECT/src/acf/io/manager.py" << 'EOF'
from acf.io.factory import ReaderFactory


class DataManager:

    def __init__(self, registry):

        self.factory = ReaderFactory(registry)

    def open(self, filename):

        reader = self.factory.get_reader(filename)

        if reader is None:
            raise ValueError(f"No reader available for {filename}")

        return reader.read(filename)
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_io_framework.py" << 'EOF'
from acf.io.base_reader import BaseReader
from acf.io.registry import ReaderRegistry
from acf.io.factory import ReaderFactory


class DummyReader(BaseReader):

    extensions = [".abc"]

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
EOF

echo
echo "Universal Reader Framework installed successfully."
