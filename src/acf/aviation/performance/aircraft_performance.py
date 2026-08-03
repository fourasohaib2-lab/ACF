"""
Atmospheric Complexity Framework (ACF)

Aircraft Operational Performance & Atmospheric Mechanics Module (ISA, Density Altitude, Crosswind)
"""

import math
from typing import Dict


class AircraftPerformanceEngine:
    """
    Moteur de calcul de l'atmosphère OACI (ISA) et des performances aéronautiques au décollage, en croisière et à l'atterrissage.
    """

    @staticmethod
    def isa_atmosphere(altitude_m: float) -> Dict[str, float]:
        """Calcul des variables de l'Atmosphère Standard Internationale (OACI ISA)."""
        t0 = 288.15  # K (15°C)
        p0 = 101325.0  # Pa (1013.25 hPa)
        g = 9.80665
        r = 287.05
        gamma_lapse = 0.0065  # K/m (6.5 °C / 1000m)

        if altitude_m <= 11000.0:
            temp_k = t0 - gamma_lapse * altitude_m
            press_pa = p0 * ((temp_k / t0) ** (g / (gamma_lapse * r)))
        else:  # Stratosphère isotherme (11-20 km)
            temp_k = 216.65  # -56.5°C
            p11 = p0 * ((temp_k / t0) ** (g / (gamma_lapse * r)))
            press_pa = p11 * math.exp(-g * (altitude_m - 11000.0) / (r * temp_k))

        rho = press_pa / (r * temp_k)
        speed_of_sound = math.sqrt(1.4 * r * temp_k)

        return {
            "temperature_k": temp_k,
            "temperature_c": temp_k - 273.15,
            "pressure_hpa": press_pa / 100.0,
            "density_kg_m3": rho,
            "speed_of_sound_m_s": speed_of_sound,
            "speed_of_sound_kt": speed_of_sound * 1.94384,
        }

    @staticmethod
    def wind_components(runway_heading_deg: float, wind_dir_deg: float, wind_speed_kt: float) -> Dict[str, float]:
        """Calcul des composantes de vent debout/arrière (Headwind/Tailwind) et vent traversier (Crosswind)."""
        angle_rad = math.radians(wind_dir_deg - runway_heading_deg)
        headwind = wind_speed_kt * math.cos(angle_rad)
        crosswind = wind_speed_kt * math.sin(angle_rad)

        return {
            "headwind_kt": headwind,  # Positif = vent debout, Négatif = vent arrière
            "crosswind_kt": abs(crosswind),
            "crosswind_direction": "LEFT" if crosswind < 0 else "RIGHT",
        }

    @classmethod
    def density_altitude_ft(cls, pressure_altitude_ft: float, temp_c: float) -> float:
        """Calcul de l'Altitude-Densité (Density Altitude) essentielle pour la longueur de roulement au décollage."""
        isa_temp_c = 15.0 - 1.98 * (pressure_altitude_ft / 1000.0)
        isa_dev = temp_c - isa_temp_c
        return pressure_altitude_ft + 120.0 * isa_dev
