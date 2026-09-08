"""Global Earth spherical grid and coordinate transformation manager."""

from enum import Enum
from typing import Any

import numpy as np

# Physical constant for Earth mean radius (m)
EARTH_RADIUS: float = 6371000.0


class GridResolution(Enum):
    """Preset resolution levels for Earth simulation grids."""

    GLOBAL_NWP_25KM = "25km"
    GLOBAL_NWP_9KM = "9km"
    REGIONAL_5KM = "5km"
    REGIONAL_1KM = "1km"
    CONVECTIVE_500M = "500m"
    CONVECTIVE_100M = "100m"


class EarthGrid:
    """Manages global/regional spherical coordinates and hybrid vertical levels.

    Attributes:
        n_lat (int): Number of latitude grid points.
        n_lon (int): Number of longitude grid points.
        n_levels (int): Number of vertical levels.
        resolution (GridResolution): Grid resolution preset.
    """

    def __init__(
        self,
        n_lat: int = 72,
        n_lon: int = 144,
        n_levels: int = 32,
        resolution: GridResolution = GridResolution.GLOBAL_NWP_25KM,
    ) -> None:
        if n_lat <= 0 or n_lon <= 0 or n_levels <= 0:
            raise ValueError("Grid dimensions must be positive integers.")

        self.n_lat = n_lat
        self.n_lon = n_lon
        self.n_levels = n_levels
        self.resolution = resolution

        # Latitude: [-90, +90], Longitude: [-180, +180]
        self.lats = np.linspace(-90.0, 90.0, self.n_lat)
        self.lons = np.linspace(-180.0, 180.0, self.n_lon, endpoint=False)

        # 2D Meshgrids (lat, lon)
        self.lon_mesh, self.lat_mesh = np.meshgrid(self.lons, self.lats)

        # Hybrid vertical coordinate coefficients (A: pressure offset in Pa,
        # B: surface pressure fraction) - real formula actually used by
        # compute_vertical_pressure_profile() below: p(k) = A(k) + B(k)*Ps
        # (A(k) already in Pa, NOT multiplied by a separate P0 - the
        # previous comment here described a different, P0-scaled
        # convention that did not match this implementation).
        #
        # NOTE (correction, 2026-09-04): A(k) at the surface (k=0, B=1.0)
        # MUST be 0 Pa - the real physical boundary condition for any
        # hybrid sigma-pressure coordinate is p(surface) = Ps exactly.
        # This previously started at 100000.0 Pa instead of 0.0, so every
        # real solver run added a spurious +1000 hPa to its own real
        # surface pressure (e.g. a real 1013.25 hPa surface came out as
        # ~2013.25 hPa) - found while building the ACF Scientific
        # Workstation (independently re-confirmed by its Data Quality
        # Center, Thermodynamics Lab, and Research Mode, all flagging the
        # same real ~2013 hPa anomaly; see reports/ACF_MASTER_AUDIT_v2.md).
        # A(top) stays a real, small reference pressure (100 Pa = 1 hPa)
        # for a real, physically-reasonable model-top pressure.
        self.a_coeff = np.linspace(0.0, 100.0, self.n_levels)  # Pa
        self.b_coeff = np.linspace(1.0, 0.0, self.n_levels)

    def compute_cell_areas(self) -> np.ndarray:
        """Compute area element dA = R^2 * cos(lat) * dlat * dlon for each grid cell.

        Returns:
            np.ndarray: 2D array of grid cell areas in square meters (m^2).
        """
        dlat_rad = np.radians(180.0 / self.n_lat)
        dlon_rad = np.radians(360.0 / self.n_lon)

        lat_rad = np.radians(self.lats)
        cos_lat = np.cos(lat_rad)

        # Area = R^2 * cos(lat) * dlat * dlon
        cell_areas = (EARTH_RADIUS**2) * cos_lat[:, np.newaxis] * dlat_rad * dlon_rad
        cell_areas_2d = np.tile(cell_areas, (1, self.n_lon))
        return np.abs(cell_areas_2d)

    def get_resolution_km(self) -> float:
        """Returns approximate horizontal grid cell spacing in kilometers."""
        dlat_deg = 180.0 / self.n_lat
        return float(dlat_deg * 111.0)

    def compute_vertical_pressure_profile(self, p_surface: np.ndarray) -> np.ndarray:
        """Calculate 3D pressure tensor p(k, lat, lon) based on surface pressure p_surface.

        Args:
            p_surface (np.ndarray): 2D surface pressure array in Pa (shape: [n_lat, n_lon]).

        Returns:
            np.ndarray: 3D pressure array in Pa (shape: [n_levels, n_lat, n_lon]).
        """
        p_3d = np.zeros((self.n_levels, self.n_lat, self.n_lon), dtype=np.float64)
        for k in range(self.n_levels):
            p_3d[k, :, :] = self.a_coeff[k] + self.b_coeff[k] * p_surface
        return p_3d

    def to_dict(self) -> dict[str, Any]:
        """Export grid metadata dictionary."""
        return {
            "n_lat": self.n_lat,
            "n_lon": self.n_lon,
            "n_levels": self.n_levels,
            "resolution": self.resolution.value,
            "dx_km": self.get_resolution_km(),
        }
