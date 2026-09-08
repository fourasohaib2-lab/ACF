"""
StorageWriter: a real unified facade over ACF's existing real writers.
"""

import csv
import os

import numpy as np

from acf.simulation_engine.output.netcdf_writer import NetcdfWriter
from acf.simulation_engine.output.zarr_writer import ZarrWriter

SUPPORTED_FORMATS = ("netcdf", "zarr", "csv")


class StorageWriter:
    """
    Write an ACF state dict (variable name -> 2D/3D numpy array, same
    shape convention as NetcdfWriter/ZarrWriter and everywhere else in
    ACF that writes gridded output - see acf.forecast.engine,
    acf.awci.spatial_field) to one of SUPPORTED_FORMATS.

    NetCDF and Zarr are handed off to ACF's existing real writers
    (acf.simulation_engine.output.{netcdf_writer,zarr_writer}) - not
    reimplemented. CSV is a real, new writer (stdlib csv module, no
    pandas) producing a "long format" table: one row per (variable,
    level, lat, lon) grid point - the standard tabular representation
    for gridded data, not an invented format.
    """

    def __init__(self, path: str) -> None:
        self.path = path

    def write(
        self,
        state: dict[str, np.ndarray],
        lats: np.ndarray,
        lons: np.ndarray,
        levels: np.ndarray | None = None,
        format: str = "netcdf",  # noqa: A002 - matches NetcdfWriter/ZarrWriter's own vocabulary; shadowing builtin `format` is a stylistic tradeoff, not a bug
        time_step: int = 0,
    ) -> str:
        """
        Write `state` to self.path in the requested `format`.

        Parameters
        ----------
        state : dict[str, np.ndarray]
            Variable name -> 2D (lat, lon) or 3D (level, lat, lon)
            array.
        lats, lons : 1D coordinate arrays.
        levels : 1D vertical level array, optional (required for any
            3D variable in `state`).
        format : "netcdf", "zarr", or "csv".
        time_step : passed through to NetcdfWriter (see its own
            NOTE on why this is recorded as a real global attribute).

        Returns
        -------
        str
            Path/store actually written - NetcdfWriter/ZarrWriter's
            own return value for those formats, self.path for csv.

        Raises
        ------
        ValueError
            For an unrecognized format - never silently falls back to
            a different one.
        """
        if format == "netcdf":
            return NetcdfWriter(self.path).write_state(state, lats, lons, levels=levels, time_step=time_step)
        if format == "zarr":
            return ZarrWriter(self.path).write_zarr(state, lats, lons, levels=levels)
        if format == "csv":
            return self._write_csv(state, lats, lons, levels)
        raise ValueError(f"Unknown format {format!r} - expected one of {SUPPORTED_FORMATS}")

    def _write_csv(
        self, state: dict[str, np.ndarray], lats: np.ndarray, lons: np.ndarray, levels: np.ndarray | None
    ) -> str:
        """
        Real CSV export via the stdlib csv module (no pandas - removed
        from ACF's dependencies 2026-09-02 as unused). Long format: one
        row per (variable, level, lat, lon) - level is empty for a 2D
        variable, not a fabricated 0.
        """
        parent = os.path.dirname(self.path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(self.path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["variable", "level", "lat", "lon", "value"])

            for var_name, array in state.items():
                if not isinstance(array, np.ndarray):
                    continue

                if array.ndim == 2:
                    for i, lat in enumerate(lats):
                        for j, lon in enumerate(lons):
                            writer.writerow([var_name, "", float(lat), float(lon), float(array[i, j])])
                elif array.ndim == 3:
                    level_labels = levels if levels is not None else range(array.shape[0])
                    for k, level in enumerate(level_labels):
                        for i, lat in enumerate(lats):
                            for j, lon in enumerate(lons):
                                writer.writerow(
                                    [var_name, float(level), float(lat), float(lon), float(array[k, i, j])]
                                )

        return self.path
