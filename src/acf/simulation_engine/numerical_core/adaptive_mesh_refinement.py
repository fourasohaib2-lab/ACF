"""Dynamic Adaptive Mesh Refinement (AMR) engine."""

from typing import List, Dict
import numpy as np
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid


class AdaptiveMeshRefinement:
    """Dynamic AMR controller.

    Evaluates spatial field gradients (pressure, temperature, wind shear, moisture)
    to automatically flag high-resolution sub-grid refinement regions.
    Target phenomena:
    - Cyclones (pressure drop & vorticity)
    - Atmospheric fronts (temperature gradients)
    - Severe convection (vertical shear & moisture flux)
    - Wildfires (heat anomalies)
    - Critical ocean eddies/fronts
    """

    def __init__(self, base_grid: EarthGrid, max_refinement_level: int = 3) -> None:
        self.base_grid = base_grid
        self.max_refinement_level = max_refinement_level

    def evaluate_refinement_masks(
        self,
        pressure: np.ndarray,
        temperature: np.ndarray,
        vorticity: np.ndarray,
        grad_threshold: float = 2.0,
    ) -> np.ndarray:
        """Compute boolean refinement mask (True where resolution must be refined).

        Args:
            pressure (np.ndarray): Surface/atmospheric pressure field.
            temperature (np.ndarray): Temperature field.
            vorticity (np.ndarray): Vorticity field.
            grad_threshold (float): Standard deviation multiplier threshold for flagging cells.

        Returns:
            np.ndarray: Boolean 2D mask matching (n_lat, n_lon).
        """
        # Gradient magnitude of pressure and temperature
        dp_y, dp_x = np.gradient(pressure)
        grad_p = np.sqrt(dp_x**2 + dp_y**2)

        dt_y, dt_x = np.gradient(temperature)
        grad_t = np.sqrt(dt_x**2 + dt_y**2)

        # Normalized feature scores
        norm_grad_p = (grad_p - np.mean(grad_p)) / (np.std(grad_p) + 1e-8)
        norm_grad_t = (grad_t - np.mean(grad_t)) / (np.std(grad_t) + 1e-8)
        norm_vort = (np.abs(vorticity) - np.mean(np.abs(vorticity))) / (
            np.std(np.abs(vorticity)) + 1e-8
        )

        combined_score = norm_grad_p + norm_grad_t + norm_vort
        refinement_mask = combined_score > grad_threshold
        return refinement_mask

    def get_refined_subgrid_bounds(self, refinement_mask: np.ndarray) -> List[Dict[str, float]]:
        """Identify bounding boxes for regions requiring AMR high-resolution sub-grids.

        Returns:
            List[Dict[str, float]]: List of region dicts with keys 'lat_min', 'lat_max', 'lon_min', 'lon_max'.
        """
        indices = np.argwhere(refinement_mask)
        if len(indices) == 0:
            return []

        lat_indices = indices[:, 0]
        lon_indices = indices[:, 1]

        lat_min = float(self.base_grid.lats[np.min(lat_indices)])
        lat_max = float(self.base_grid.lats[np.max(lat_indices)])
        lon_min = float(self.base_grid.lons[np.min(lon_indices)])
        lon_max = float(self.base_grid.lons[np.max(lon_indices)])

        return [
            {
                "lat_min": lat_min,
                "lat_max": lat_max,
                "lon_min": lon_min,
                "lon_max": lon_max,
                "refinement_ratio": 4,  # e.g., 4x resolution increase
            }
        ]
