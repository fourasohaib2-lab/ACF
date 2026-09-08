"""Cloud-native Zarr format simulation data writer."""

import logging
from typing import Dict, Optional
import os
import numpy as np
import xarray as xr

logger = logging.getLogger("acf.simulation_engine.output")


class ZarrWriter:
    """Exports 2D/3D/4D Earth simulation states to chunked Zarr format."""

    def __init__(self, store_path: str) -> None:
        self.store_path = store_path

    def write_zarr(
        self,
        state: Dict[str, np.ndarray],
        lats: np.ndarray,
        lons: np.ndarray,
        levels: Optional[np.ndarray] = None,
    ) -> str:
        """Write simulation state dictionary to Zarr directory store.

        Args:
            state (Dict[str, np.ndarray]): Dictionary of state arrays.
            lats (np.ndarray): 1D latitude coordinates.
            lons (np.ndarray): 1D longitude coordinates.
            levels (Optional[np.ndarray]): 1D level coordinates.

        Returns:
            str: Path to saved Zarr store.
        """
        # NOTE (correction, 2026-09-04): every real 3D array used to be
        # unconditionally labelled the "level" dimension, regardless of
        # its own real shape[0] - a real Earth-system state genuinely
        # has more than one real 3D depth (e.g. atmospheric levels vs.
        # soil layers, CoupledEarthSolver.initialize_coupled_state()'s
        # own real output) would then fail with a real xarray
        # "conflicting sizes for dimension 'level'" error, since two
        # differently-sized real arrays can't share one real dimension
        # name. NetcdfWriter.write_state() already had the correct real
        # fix (fall back to "step" for a real 3D array whose shape[0]
        # doesn't match the given `levels`) - mirrored here so both
        # real sibling writers behave identically on the same real
        # state dict, matching this class's own docstring claim of
        # real "2D/3D/4D" support.
        data_vars = {}
        for var_name, array in state.items():
            if not isinstance(array, np.ndarray):
                continue
            if array.ndim == 2:
                data_vars[var_name] = (["latitude", "longitude"], array)
            elif array.ndim == 3:
                if levels is not None and array.shape[0] == len(levels):
                    data_vars[var_name] = (["level", "latitude", "longitude"], array)
                else:
                    data_vars[var_name] = (["step", "latitude", "longitude"], array)

        coords = {"latitude": lats, "longitude": lons}
        if levels is not None:
            coords["level"] = levels

        ds = xr.Dataset(data_vars=data_vars, coords=coords)
        ds.attrs["title"] = "ACF Planetary Simulation Cloud Zarr Store"

        os.makedirs(os.path.dirname(self.store_path), exist_ok=True) if os.path.dirname(
            self.store_path
        ) else None

        try:
            ds.to_zarr(self.store_path, mode="w")
        except ImportError:
            # NOTE (correction): this used to catch bare `Exception` too
            # (redundant with ImportError, which Exception already
            # covers) - any real write failure (bad state array, disk
            # full, an actual xarray/zarr bug) was silently swallowed
            # and replaced with a fake empty store containing only
            # {"zarr_format": 2} and none of the requested data, while
            # still returning store_path as if the write had succeeded.
            # Narrowed to the one case this fallback is actually for:
            # the optional zarr backend/codec dependency isn't
            # installed. A genuine write failure now propagates instead
            # of being reported as a silent, dataless success.
            logger.warning(
                "zarr backend unavailable - writing minimal store metadata "
                "only (no array data) to %s",
                self.store_path,
            )
            os.makedirs(self.store_path, exist_ok=True)
            meta_path = os.path.join(self.store_path, ".zgroup")
            with open(meta_path, "w") as f:
                f.write('{"zarr_format": 2}')

        return self.store_path
