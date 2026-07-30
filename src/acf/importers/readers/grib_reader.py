"""
ACF GRIB Reader

Reader for GRIB1 / GRIB2 meteorological files.
"""

from pathlib import Path
import xarray as xr

from acf.data.dataset import Dataset
from acf.importers.base.base_reader import BaseReader


class GRIBReader(BaseReader):
    """
    Lecteur de données GRIB.
    """

    name = "GRIB Reader"

    SUPPORTED_EXTENSIONS = (
        ".grib",
        ".grb",
        ".grib2",
        ".grb2",
    )

    def can_read(self, filename):
        return (
            Path(filename)
            .suffix
            .lower()
            in self.SUPPORTED_EXTENSIONS
        )

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
            filetype="GRIB2",
            source="cfgrib",
        )

        # Variables
        for variable in ds.data_vars:
            dataset.add_variable(variable)

        # Dimensions
        for dim, size in ds.sizes.items():
            dataset.add_dimension(dim, int(size))

        # Metadata
        for key, value in ds.attrs.items():
            dataset.set_metadata(key, value)

        ds.close()
        dataset.validate()

        return dataset


class GribReader:
    """
    Standalone GRIB Reader (compatibilité).
    """

    def __init__(self):
        self.dataset = None

    def open(self, filename):
        self.dataset = xr.open_dataset(
            filename,
            engine="cfgrib"
        )
        return self.dataset

    def variables(self):
        if self.dataset is None:
            return []
        return list(self.dataset.data_vars)

    def dimensions(self):
        if self.dataset is None:
            return {}
        return dict(self.dataset.sizes)

    def close(self):
        if self.dataset is not None:
            self.dataset.close()
        self.dataset = None

    def __repr__(self):
        return f"GribReader(open={self.dataset is not None})"

    def coordinates(self):
        return list(self.dataset.coords)

    def attributes(self):
        return dict(self.dataset.attrs)

    def times(self):
        if "time" in self.dataset:
            return self.dataset["time"].values
        return None

    def levels(self):
        if "isobaricInhPa" in self.dataset.coords:
            return self.dataset["isobaricInhPa"].values
        return None

    def get_variable(self, name):
        return self.dataset[name]
