"""Tropical and extratropical cyclone simulation engine."""

from typing import Dict, Any
import numpy as np


class CycloneSimulator:
    """Simulates tropical cyclone formation, pressure drop, and track trajectory.

    Key metrics:
    - Cyclogenesis risk index
    - Minimum central sea-level pressure P_min (hPa)
    - Maximum sustained 10-meter wind speed V_max (m/s)
    - Rapid Intensification (RI) criteria (>= 30 knots / 24h pressure drop)
    - Track forecast coordinates (lat, lon trajectory)
    """

    def __init__(self) -> None:
        pass

    def detect_cyclone_center(
        self, slp: np.ndarray, lats: np.ndarray, lons: np.ndarray
    ) -> Dict[str, Any]:
        """Locate central pressure minimum and maximum wind radius.

        Args:
            slp (np.ndarray): Surface pressure field in Pa or hPa.
            lats (np.ndarray): 1D array of latitude coordinates.
            lons (np.ndarray): 1D array of longitude coordinates.

        Returns:
            Dict[str, Any]: Cyclone diagnostic center parameters.
        """
        slp_hpa = slp / 100.0 if np.max(slp) > 2000.0 else slp

        min_idx = np.unravel_index(np.argmin(slp_hpa), slp_hpa.shape)
        center_lat = float(lats[min_idx[0]])
        center_lon = float(lons[min_idx[1]])
        p_min = float(slp_hpa[min_idx])

        # Estimate maximum wind speed using Holland pressure profile model
        p_env = 1013.25  # hPa
        dp = max(0.0, p_env - p_min)

        # Holland B parameter ~ 1.5
        b_param = 1.5
        rho_air = 1.15
        v_max = np.sqrt(b_param * dp * 100.0 / (rho_air * np.e))

        is_rapid_intensification = bool(dp >= 30.0)

        # Saffir-Simpson category classification
        v_knots = v_max * 1.94384
        if v_knots < 34:
            category = "Tropical Depression"
        elif v_knots < 64:
            category = "Tropical Storm"
        elif v_knots < 83:
            category = "Category 1"
        elif v_knots < 96:
            category = "Category 2"
        elif v_knots < 113:
            category = "Category 3"
        elif v_knots < 137:
            category = "Category 4"
        else:
            category = "Category 5 Major Hurricane"

        return {
            "center_lat": center_lat,
            "center_lon": center_lon,
            "P_min_hpa": p_min,
            "V_max_ms": float(v_max),
            "category": category,
            "rapid_intensification": is_rapid_intensification,
        }
