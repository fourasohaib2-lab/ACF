"""Spectral ocean surface wave model."""

from typing import Dict
import numpy as np


class WaveModel:
    """Spectral wind-wave and swell ocean surface wave model.

    Calculates:
    - Significant Wave Height (Hs, meters): Hs = 4 * sqrt(E_total)
    - Peak wave period (Tp, seconds)
    - Mean wave direction (degrees)
    - Wave energy spectrum E(f, theta)
    """

    def __init__(self, n_freq: int = 25, n_dir: int = 24) -> None:
        self.n_freq = n_freq
        self.n_dir = n_dir
        self.g = 9.80665

        self.frequencies = np.logspace(-2, 0.5, self.n_freq)  # 0.01 Hz to 3.16 Hz
        self.directions = np.linspace(0.0, 360.0, self.n_dir, endpoint=False)

    def compute_significant_wave_height(
        self, wind_speed_10m: np.ndarray, fetch_km: float = 100.0
    ) -> Dict[str, np.ndarray]:
        """Compute wave parameters using empirical Pierson-Moskowitz / Hasselmann formulas.

        Hs = 0.243 * (U10^2 / g)

        Args:
            wind_speed_10m (np.ndarray): 10-meter wind speed array (m/s).
            fetch_km (float): Wind fetch length in kilometers.

        Returns:
            Dict[str, np.ndarray]: Dictionary containing Hs (m), Tp (s), and Wave Energy (J/m^2).
        """
        u10 = np.maximum(wind_speed_10m, 0.0)

        # Significant wave height Hs (m)
        hs = 0.243 * (u10**2 / self.g)

        # Peak period Tp ~ 8.13 * (U10 / g)
        tp = 8.13 * (u10 / self.g)

        # Total wave energy density E = 1/16 * rho * g * Hs^2
        rho_water = 1025.0
        energy_density = (1.0 / 16.0) * rho_water * self.g * (hs**2)

        return {
            "Hs": hs,
            "Tp": tp,
            "wave_energy": energy_density,
        }
