"""NetCDF4 format simulation data writer."""

from typing import Dict, Optional
import os
import numpy as np
import xarray as xr


class NetcdfWriter:
    """Exports 2D/3D/4D Earth simulation states to CF-compliant NetCDF4 files."""

    def __init__(self, filename: str) -> None:
        self.filename = filename

    def write_state(
        self,
        state: Dict[str, np.ndarray],
        lats: np.ndarray,
        lons: np.ndarray,
        levels: Optional[np.ndarray] = None,
        time_step: int = 0,
    ) -> str:
        """Write simulation state dictionary to NetCDF file.

        Args:
            state (Dict[str, np.ndarray]): Dictionary of state arrays.
            lats (np.ndarray): 1D latitude coordinates.
            lons (np.ndarray): 1D longitude coordinates.
            levels (Optional[np.ndarray]): 1D vertical level coordinates.
            time_step (int): Simulation timestep index.

        Returns:
            str: Path to saved file.
        """
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
        ds.attrs["title"] = "ACF Planetary Simulation Engine Output (ACF-DT-003)"
        ds.attrs["institution"] = "Atmospheric Complexity Framework"
        ds.attrs["conventions"] = "CF-1.8"

        os.makedirs(os.path.dirname(self.filename), exist_ok=True) if os.path.dirname(
            self.filename
        ) else None
        ds.to_netcdf(self.filename)
        return self.filename
