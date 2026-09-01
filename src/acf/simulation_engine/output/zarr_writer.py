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
        data_vars = {}
        for var_name, array in state.items():
            if not isinstance(array, np.ndarray):
                continue
            if array.ndim == 2:
                data_vars[var_name] = (["latitude", "longitude"], array)
            elif array.ndim == 3:
                data_vars[var_name] = (["level", "latitude", "longitude"], array)

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
