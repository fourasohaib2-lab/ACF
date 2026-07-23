#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================="
echo " Sprint 06 - Partie 5"
echo " DataManager"
echo "========================================="

cat > "$PROJECT/src/acf/data/manager.py" << 'EOF'
"""
ACF Data Manager
"""

from pathlib import Path

from acf.data.readers.netcdf_reader import NetCDFReader
from acf.data.readers.grib_reader import GRIBReader


class DataManager:
    """
    Gestionnaire central des données scientifiques.
    """

    def __init__(self):

        self.readers = [
            NetCDFReader(),
            GRIBReader(),
        ]

    def available_readers(self):

        return [
            reader.__class__.__name__
            for reader in self.readers
        ]

    def open(self, filename):

        filename = Path(filename)

        for reader in self.readers:

            if reader.can_read(filename):

                return reader.read(filename)

        raise ValueError(
            f"Aucun lecteur disponible pour : {filename}"
        )
EOF

cat > "$PROJECT/tests/test_data_manager.py" << 'EOF'
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
EOF

echo
echo "DataManager successfully created."

