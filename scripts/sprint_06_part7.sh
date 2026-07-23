#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "=========================================="
echo " Sprint 06 - Partie 7"
echo " Reader Plugin Loader"
echo "=========================================="

####################################################
# FACTORY
####################################################

cat > "$PROJECT/src/acf/data/factory.py" << 'EOF'
"""
ACF Reader Factory
"""

import inspect
import pkgutil
import importlib

import acf.data.readers as readers_package


class ReaderFactory:

    def __init__(self):

        self._readers = []

        self.discover()

    ##################################################

    def discover(self):
        """
        Recherche automatiquement tous les lecteurs.
        """

        for _, module_name, _ in pkgutil.iter_modules(
            readers_package.__path__
        ):

            module = importlib.import_module(
                f"acf.data.readers.{module_name}"
            )

            for _, cls in inspect.getmembers(
                module,
                inspect.isclass
            ):

                if cls.__module__ != module.__name__:
                    continue

                if cls.__name__.endswith("Reader"):

                    try:
                        self.register(cls())

                    except Exception:
                        pass

    ##################################################

    def register(self, reader):

        self._readers.append(reader)

    ##################################################

    def readers(self):

        return self._readers

    ##################################################

    def get_reader(self, filename):

        for reader in self._readers:

            if reader.can_read(filename):

                return reader

        return None
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_reader_discovery.py" << 'EOF'
from acf.data.factory import ReaderFactory


def test_discovery():

    factory = ReaderFactory()

    readers = [
        reader.__class__.__name__
        for reader in factory.readers()
    ]

    assert "NetCDFReader" in readers
    assert "GRIBReader" in readers
EOF

echo
echo "Reader Plugin Loader installed successfully."
