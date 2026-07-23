#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "=========================================="
echo " ACF Sprint 06 - Part 4"
echo " GRIB Reader"
echo "=========================================="

cat > "$PROJECT/src/acf/data/readers/grib_reader.py" << 'EOF'
"""
GRIB Reader
"""

from pathlib import Path

import xarray as xr

from acf.data.dataset import Dataset


class GRIBReader:
    """
    Lecteur de fichiers GRIB.
    """

    SUPPORTED_EXTENSIONS = (".grib", ".grb", ".grib2")

    def can_read(self, filename):

        return Path(filename).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def read(self, filename):

        filename = Path(filename)

        if not filename.exists():
            raise FileNotFoundError(filename)

        ds = xr.open_dataset(
            filename,
            engine="cfgrib"
        )

        dataset = Dataset(
            name=filename.stem,
            filepath=filename,
            filetype="GRIB",
        )

        for variable in ds.data_vars:
            dataset.add_variable(variable)

        for dim, size in ds.sizes.items():
            dataset.set_dimension(dim, int(size))

        for key, value in ds.attrs.items():
            dataset.set_metadata(key, value)

        ds.close()

        return dataset
EOF

cat > "$PROJECT/tests/test_grib_reader.py" << 'EOF'
from pathlib import Path

import pytest

from acf.data.readers.grib_reader import GRIBReader


def test_can_read_extensions():

    reader = GRIBReader()

    assert reader.can_read("demo.grib")
    assert reader.can_read("demo.grb")
    assert reader.can_read("demo.grib2")
    assert not reader.can_read("demo.nc")


def test_missing_file():

    reader = GRIBReader()

    with pytest.raises(FileNotFoundError):
        reader.read(Path("/tmp/file_that_does_not_exist.grib"))
EOF

echo
echo "GRIB Reader installed successfully."

