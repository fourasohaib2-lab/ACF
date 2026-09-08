"""Spectral ocean surface wave model."""

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
    ) -> dict[str, np.ndarray]:
        """Compute wave parameters using the SMB/SPM fetch-limited wave growth formulas.

        NOTE (correction — Physics Guard): fetch_km was genuinely
        accepted (with a docstring citing fetch-dependent "Hasselmann
        formulas") but unused - the formula actually implemented,
        Hs = 0.243*(U10^2/g), is the *fully-developed sea* (infinite
        fetch/duration) Pierson-Moskowitz limit, so any short-fetch
        case (an enclosed bay, a developing storm) got the same,
        systematically too-high wave height as an open-ocean fully-
        developed sea. Replaced with the standard fetch-limited SMB
        formula (Shore Protection Manual / Coastal Engineering Manual,
        US Army Corps of Engineers):
            g*Hs/U^2 = 0.283 * tanh[0.0125*(g*F/U^2)^0.42]
            g*Tp/U   = 7.54  * tanh[0.077 *(g*F/U^2)^0.25]
        which correctly reduces to the fully-developed limit
        (tanh -> 1) as fetch_km -> infinity, matching the previous
        formula's coefficient (0.283 here vs 0.243 previously - both
        values appear in the literature depending on drag-coefficient
        assumptions; 0.283 is kept as the SMB formula's own internal
        fully-developed limit for consistency with its Tp term).

        Args:
            wind_speed_10m (np.ndarray): 10-meter wind speed array (m/s).
            fetch_km (float): Wind fetch length in kilometers.

        Returns:
            Dict[str, np.ndarray]: Dictionary containing Hs (m), Tp (s), and Wave Energy (J/m^2).
        """
        u10 = np.maximum(wind_speed_10m, 0.01)  # avoid divide-by-zero in the dimensionless fetch term
        fetch_m = max(fetch_km, 0.0) * 1000.0

        dimensionless_fetch = self.g * fetch_m / (u10**2)

        # Significant wave height Hs (m) - fetch-limited SMB formula
        hs = 0.283 * (u10**2 / self.g) * np.tanh(0.0125 * dimensionless_fetch**0.42)

        # Peak period Tp (s) - fetch-limited SMB formula
        tp = 7.54 * (u10 / self.g) * np.tanh(0.077 * dimensionless_fetch**0.25)

        # Total wave energy density E = 1/16 * rho * g * Hs^2
        rho_water = 1025.0
        energy_density = (1.0 / 16.0) * rho_water * self.g * (hs**2)

        return {
            "Hs": hs,
            "Tp": tp,
            "wave_energy": energy_density,
        }
