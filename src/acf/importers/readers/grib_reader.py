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

    NOTE (correction, found while testing this reader against real
    ECMWF Open Data / NOAA GFS GRIB2 files): `read()` used to call
    `dataset.add_variable(variable)` with only the variable's real
    NAME, never its real decoded array (`Dataset.add_variable()`'s own
    `value` parameter defaults to `None`) - so `dataset.get_variable(x)`
    returned `None` for every real variable in every real file this
    reader ever read, silently. Coordinate arrays (latitude/longitude,
    any vertical level coordinate) were also never registered at all -
    only `ds.data_vars` was iterated, never `ds.coords`.
    `awci.data.model_import.extract_awci_point_inputs()`/
    `compute_awci_from_imported_dataset()` (the real engine behind the
    GUI's "📂 Import Model File" button) depend on exactly these two
    things (`dataset.get_variable(name)` returning a real array,
    `dataset.get_variable("latitude"/"longitude")` returning real
    coordinate arrays) - with this bug, importing any real GRIB file
    through this reader could never actually compute a real AWCI
    score from it; every point extraction silently found nothing.
    Existing tests never caught this because they only asserted
    variable NAMES were present (`"x" in dataset.variables`), never
    that `get_variable("x")` returned real data. Fixed: real decoded
    values (`variable.values`) and real coordinate arrays are now both
    stored.

    NOTE (correction, same pass): `read()` also never resolved each
    real variable through ACF's own `ParameterMapper`, nor recorded
    its own real `units`/`standard_name`/`long_name` GRIB attributes
    (cfgrib decodes all 3 from the real GRIB message - confirmed by
    inspection) as `<name>_acf`/`<name>_units`/`<name>_standard_name`/
    `<name>_long_name` metadata - `NetCDFReader.read()` already does
    this. Without it, `awci.data.model_import.
    extract_awci_point_inputs()` could match a variable by name but
    then treat its unit as absent (`_canonical_variable_name()`'s own
    docstring already disclosed the missing `_acf` half of this before
    this fix; the missing `_units` half was not previously disclosed).
    Now mirrors `NetCDFReader.read()`'s real metadata convention
    exactly.
    """

    name = "GRIB Reader"

    SUPPORTED_EXTENSIONS = (
        ".grib",
        ".grb",
        ".grib2",
        ".grb2",
    )

    def __init__(self):
        from acf.catalog.default_mapping import create_default_mapper

        self.mapper = create_default_mapper()

    def can_read(self, filename):
        return Path(filename).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def read(self, filename):
        filename = Path(filename)

        if not filename.exists():
            raise FileNotFoundError(filename)

        ds = xr.open_dataset(filename, engine="cfgrib")

        dataset = Dataset(
            name=filename.stem,
            filepath=filename,
            filetype="GRIB2",
            source="cfgrib",
        )

        # Variables - real decoded values, not just names.
        for name, variable in ds.data_vars.items():
            dataset.add_variable(name, variable.values)

            dataset.set_metadata(f"{name}_acf", self.mapper.resolve(name))
            dataset.set_metadata(f"{name}_units", variable.attrs.get("units"))
            dataset.set_metadata(f"{name}_standard_name", variable.attrs.get("standard_name"))
            dataset.set_metadata(f"{name}_long_name", variable.attrs.get("long_name"))

        # Coordinates (latitude/longitude, any vertical level
        # coordinate) - real arrays, needed by any real point-sampling
        # caller (e.g. awci.data.model_import).
        for name, coord in ds.coords.items():
            if name in ds.data_vars:
                continue
            dataset.add_variable(name, coord.values)

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
        self.dataset = xr.open_dataset(filename, engine="cfgrib")
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
