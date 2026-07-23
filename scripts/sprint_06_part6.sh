#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "=========================================="
echo " Sprint 06 - Partie 6"
echo " ReaderFactory"
echo "=========================================="

####################################################
# FACTORY
####################################################

cat > "$PROJECT/src/acf/data/factory.py" << 'EOF'
"""
Reader Factory
"""

from pathlib import Path

from acf.data.readers.netcdf_reader import NetCDFReader
from acf.data.readers.grib_reader import GRIBReader


class ReaderFactory:

    def __init__(self):

        self._readers = []

        self.register(NetCDFReader())
        self.register(GRIBReader())

    ##################################################

    def register(self, reader):

        self._readers.append(reader)

    ##################################################

    def readers(self):

        return self._readers

    ##################################################

    def get_reader(self, filename):

        filename = Path(filename)

        for reader in self._readers:

            if reader.can_read(filename):

                return reader

        return None
EOF

####################################################
# DATA MANAGER
####################################################

cat > "$PROJECT/src/acf/data/manager.py" << 'EOF'
"""
Scientific Data Manager
"""

from acf.data.factory import ReaderFactory


class DataManager:

    def __init__(self):

        self.factory = ReaderFactory()

    def available_readers(self):

        return [
            reader.__class__.__name__
            for reader in self.factory.readers()
        ]

    def open(self, filename):

        reader = self.factory.get_reader(filename)

        if reader is None:

            raise ValueError(
                f"No reader available for '{filename}'."
            )

        return reader.read(filename)
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_reader_factory.py" << 'EOF'
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
EOF

echo
echo "ReaderFactory installed successfully."
