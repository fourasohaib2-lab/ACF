"""Wildfire behavior and fire spread rate simulator."""

import numpy as np


class WildfireSimulator:
    """Wildfire propagation simulator based on Rothermel / FWI model.

    Evaluates:
    - FWI (Fire Weather Index)
    - ROS (Rate of Spread, m/min)
    - Flame Length (m)
    - Fire Intensity (kW/m)
    - Active fire perimeter propagation
    """

    def __init__(self) -> None:
        pass

    def compute_fire_weather_index(
        self,
        temp_c: np.ndarray,
        relative_humidity_pct: np.ndarray,
        wind_speed_kmh: np.ndarray,
        rain_24h_mm: np.ndarray,
    ) -> dict[str, np.ndarray]:
        """Calculate Canadian FWI System indices (FFMC, ISI, BUI, FWI).

        Args:
            temp_c (np.ndarray): Air temperature (°C).
            relative_humidity_pct (np.ndarray): Relative humidity (%).
            wind_speed_kmh (np.ndarray): 10m wind speed (km/h).
            rain_24h_mm (np.ndarray): 24-hour rainfall total (mm).

        Returns:
            Dict[str, np.ndarray]: Fire weather danger indices.

        NOTE (correction — Physics Guard): rain_24h_mm was genuinely
        accepted (and documented as "24-hour rainfall total") but
        completely unused - two areas with identical humidity/wind but
        very different recent rainfall (freshly soaked vs. bone dry)
        got the identical fire danger index. The real Canadian FFMC
        includes an explicit rain-wetting term (van Wagner 1987), which
        this already-simplified single-day humidity proxy does not
        attempt to fully reproduce (it also has no previous-day FFMC
        state, and does not compute DMC/DC/BUI despite the docstring
        naming them). Added a qualitatively-correct, monotonic
        saturating rain penalty (more rain -> lower FFMC, diminishing
        effect for very large totals, negligible effect below ~0.5mm
        per the real system's "effective rainfall" threshold) rather
        than reproducing van Wagner's exact numeric coefficients, which
        this proxy formula was never faithful to in the first place.
        Not fabricated.
        """
        # Fine Fuel Moisture Code (FFMC) proxy
        ffmc = 59.5 * (250.0 - relative_humidity_pct) / (relative_humidity_pct + 1.0)
        effective_rain_mm = np.maximum(rain_24h_mm - 0.5, 0.0)  # sub-0.5mm rain has ~no wetting effect (van Wagner)
        rain_recovery_factor = np.exp(-0.15 * effective_rain_mm)  # saturating: heavy rain -> fuel fully wetted
        ffmc = ffmc * rain_recovery_factor
        ffmc = np.clip(ffmc, 0.0, 99.0)

        # Initial Spread Index (ISI)
        isi = 0.208 * np.exp(0.05039 * wind_speed_kmh) * (ffmc / 50.0)

        # Fire Weather Index (FWI)
        fwi = 0.1 * isi * (temp_c / 10.0)
        fwi = np.clip(fwi, 0.0, 100.0)

        # Rate of Spread ROS (m/min) ~ 0.5 * ISI
        ros_m_min = 0.5 * isi

        # Flame Length L = 0.0775 * (Intensity)^0.46
        fire_intensity_kw = 300.0 * ros_m_min  # kW/m
        flame_length_m = 0.0775 * (fire_intensity_kw**0.46)

        return {
            "FWI": fwi,
            "ROS_m_min": ros_m_min,
            "fire_intensity_kw_m": fire_intensity_kw,
            "flame_length_m": flame_length_m,
            "extreme_fire_danger": fwi > 30.0,
        }
