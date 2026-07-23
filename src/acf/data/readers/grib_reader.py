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
