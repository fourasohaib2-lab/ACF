#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "=========================================="
echo " ACF Sprint 06 - Part 3"
echo " NetCDF Reader"
echo "=========================================="

cat > "$PROJECT/src/acf/data/readers/netcdf_reader.py" << 'EOF'
"""
NetCDF Reader
"""

from pathlib import Path

import xarray as xr

from acf.data.dataset import Dataset


class NetCDFReader:
    """
    Lecteur de fichiers NetCDF.
    """

    SUPPORTED_EXTENSIONS = (".nc", ".nc4", ".cdf")

    def can_read(self, filename):

        return Path(filename).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def read(self, filename):

        filename = Path(filename)

        if not filename.exists():
            raise FileNotFoundError(filename)

        ds = xr.open_dataset(filename)

        dataset = Dataset(
            name=filename.stem,
            filepath=filename,
            filetype="NetCDF",
        )

        # Variables
        for variable in ds.data_vars:
            dataset.add_variable(variable)

        # Dimensions
        for dim, size in ds.sizes.items():
            dataset.set_dimension(dim, int(size))

        # Attributs globaux
        for key, value in ds.attrs.items():
            dataset.set_metadata(key, value)

        ds.close()

        return dataset
EOF

cat > "$PROJECT/tests/test_netcdf_reader.py" << 'EOF'
from pathlib import Path

import xarray as xr

from acf.data.readers.netcdf_reader import NetCDFReader


def test_netcdf_reader(tmp_path):

    file = tmp_path / "demo.nc"

    ds = xr.Dataset(
        {
            "temperature": ("time", [20.0, 21.5, 22.3]),
            "pressure": ("time", [1010, 1008, 1006]),
        },
        coords={
            "time": [0, 1, 2],
        },
        attrs={
            "title": "ACF Test Dataset",
        },
    )

    ds.to_netcdf(file)

    reader = NetCDFReader()

    dataset = reader.read(file)

    assert dataset.filetype == "NetCDF"
    assert "temperature" in dataset.variables
    assert "pressure" in dataset.variables
    assert dataset.dimensions["time"] == 3
    assert dataset.metadata["title"] == "ACF Test Dataset"
EOF

echo
echo "NetCDF Reader installed successfully."
