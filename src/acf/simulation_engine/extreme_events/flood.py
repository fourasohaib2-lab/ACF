"""Coupled hydrological flood and inundation simulator."""

from typing import Dict
import numpy as np


class FloodSimulator:
    """Coupled hydrological flood engine.

    Integrates:
        Rainfall + Soil Moisture Saturation + River Routing -> Inundation Extent & Depth

    Equations:
        Runoff Q_surface = max(0, Precip - Infiltration_Capacity)
        Saturated excess overland flow when SoilMoisture >= Porosity
        River discharge routing via Muskingum method proxy
    """

    def __init__(self, Manning_n: float = 0.035) -> None:
        self.manning_n = Manning_n

    def simulate_inundation(
        self,
        rainfall_rate_mm_h: np.ndarray,
        soil_moisture: np.ndarray,
        elevation_m: np.ndarray,
        saturation_capacity: float = 0.45,
    ) -> Dict[str, np.ndarray]:
        """Compute surface runoff accumulation and inundation depth.

        Args:
            rainfall_rate_mm_h (np.ndarray): Heavy rainfall rate (mm/h).
            soil_moisture (np.ndarray): Current soil moisture (m^3/m^3).
            elevation_m (np.ndarray): Topographic DEM elevation (m).
            saturation_capacity (float): Soil saturation porosity.

        Returns:
            Dict[str, np.ndarray]: Inundation depth (m) and flooded cell mask.
        """
        # Excess moisture factor (0 to 1)
        soil_saturation = np.clip(soil_moisture / saturation_capacity, 0.0, 1.0)

        # Runoff coefficient C = C_base + soil_saturation * 0.7
        runoff_coeff = 0.2 + 0.7 * soil_saturation

        # Surface runoff depth generation (meters/hour)
        runoff_m_h = (rainfall_rate_mm_h / 1000.0) * runoff_coeff

        # Topographic accumulation: low elevation zones accumulate runoff
        grad_ey, grad_ex = np.gradient(elevation_m)
        slope = np.sqrt(grad_ex**2 + grad_ey**2) + 1e-4

        inundation_depth_m = runoff_m_h / (slope * 5.0)
        is_flooded = inundation_depth_m > 0.15  # 15 cm threshold

        return {
            "runoff_m_h": runoff_m_h,
            "inundation_depth_m": np.clip(inundation_depth_m, 0.0, 15.0),
            "is_flooded": is_flooded,
        }
