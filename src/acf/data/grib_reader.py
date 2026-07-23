"""
GRIB Reader
"""

import xarray as xr


class GribReader:

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

    ##################################################

    def coordinates(self):

        return list(self.dataset.coords)

    ##################################################

    def attributes(self):

        return dict(self.dataset.attrs)

    ##################################################

    def times(self):

        if "time" in self.dataset:

            return self.dataset["time"].values

        return None

    ##################################################

    def levels(self):

        if "isobaricInhPa" in self.dataset.coords:

            return self.dataset["isobaricInhPa"].values

        return None

    ##################################################

    def get_variable(self, name):

        return self.dataset[name]
