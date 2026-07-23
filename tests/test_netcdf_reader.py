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
