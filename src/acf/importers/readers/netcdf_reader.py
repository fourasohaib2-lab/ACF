"""
ACF NetCDF Reader

Reader for NetCDF meteorological datasets.
"""

from pathlib import Path

import xarray as xr

from acf.catalog.default_mapping import create_default_mapper
from acf.data.dataset import Dataset
from acf.importers.base.base_reader import BaseReader
from acf.importers.readers.cf_detector import CFDetector


class NetCDFReader(BaseReader):
    """
    Lecteur de fichiers NetCDF.

    Compatible avec :
    - WRF
    - ICON
    - ERA5
    - données climatiques
    - sorties scientifiques
    """

    name = "NetCDF Reader"

    SUPPORTED_EXTENSIONS = (
        ".nc",
        ".nc4",
        ".cdf",
    )

    # NOTE (correction, found alongside the identical real bug in
    # acf.importers.readers.grib_reader.GRIBReader while testing
    # against real GRIB2 data): `read()` used to call
    # `dataset.add_variable(name)` with only the variable's real NAME,
    # never its real decoded array - `Dataset.add_variable()`'s own
    # `value` parameter defaults to `None`, so `dataset.get_variable(x)`
    # returned `None` for every real variable in every real NetCDF
    # file this reader ever read. Coordinate arrays (latitude/
    # longitude, any vertical level coordinate) were also never
    # registered - only `ds.coords`'s NAMES were recorded as metadata
    # (`dataset.set_metadata("coordinates", list(ds.coords))`), never
    # their real values. `awci.data.model_import.
    # extract_awci_point_inputs()` depends on both being real arrays -
    # this bug meant importing any real NetCDF file could never
    # actually compute a real AWCI score from it. The existing test
    # (tests/test_netcdf_reader.py) never caught this because it only
    # asserted variable NAMES were present, never that
    # `get_variable(name)` returned real data. Fixed below: real
    # decoded values and real coordinate arrays are now both stored,
    # before `ds.close()` (the array is materialized into memory via
    # `.values` first - reading from the file after `close()` would
    # otherwise silently fail).

    def __init__(self):
        self.mapper = create_default_mapper()
        self.detector = CFDetector()

    def can_read(self, filename):
        return Path(filename).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def read(self, filename):
        filename = Path(filename)

        if not filename.exists():
            raise FileNotFoundError(filename)

        ds = xr.open_dataset(filename)

        try:
            dataset = Dataset(
                name=filename.stem,
                filepath=filename,
                filetype="NetCDF",
                source="xarray",
            )

            # Variables - real decoded values, not just names.
            for name, variable in ds.data_vars.items():
                dataset.add_variable(name, variable.values)

                dataset.set_metadata(
                    f"{name}_acf",
                    self.mapper.resolve(name),
                )
                dataset.set_metadata(
                    f"{name}_units",
                    variable.attrs.get("units"),
                )
                dataset.set_metadata(
                    f"{name}_standard_name",
                    variable.attrs.get("standard_name"),
                )
                dataset.set_metadata(
                    f"{name}_long_name",
                    variable.attrs.get("long_name"),
                )
                dataset.set_metadata(
                    f"{name}_dtype",
                    str(variable.dtype),
                )
                dataset.set_metadata(
                    f"{name}_shape",
                    tuple(variable.shape),
                )

            # Dimensions
            for dim, size in ds.sizes.items():
                dataset.set_dimension(
                    dim,
                    int(size),
                )

            # Global metadata
            for key, value in ds.attrs.items():
                dataset.set_metadata(
                    key,
                    value,
                )

            # Coordinates - real arrays (not just names), needed by any
            # real point-sampling caller (e.g. awci.data.model_import).
            for name, coord in ds.coords.items():
                if name in ds.data_vars:
                    continue
                dataset.add_variable(name, coord.values)

            dataset.set_metadata(
                "coordinates",
                list(ds.coords),
            )

            dataset.set_metadata(
                "dimensions",
                dict(ds.sizes),
            )

            # CF Detection
            try:
                dataset.set_metadata(
                    "cf_detected",
                    self.detector.detect(ds),
                )
            except Exception:
                pass

            dataset.validate()
            return dataset

        finally:
            ds.close()
