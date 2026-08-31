"""
Atmospheric Complexity Framework (ACF)

Aviation Space Weather & ICAO Advisory Module (Phase 7)
(Polar Routes, Radiation Dose Rates µSv/h, ICAO SWX Advisories, HF Blackout)
"""

from typing import Any


class AviationSpaceWeatherEngine:
    """
    Moteur de sécurité météo-spatiale pour l'aviation transcontinentale et polaire (Conforme OACI).
    """

    @staticmethod
    def calculate_polar_flight_radiation_dose(flight_level: int, solar_proton_event_s_scale: int = 0) -> dict[str, Any]:
        """
        Calcule le débit de dose de radiation Cosmique / Solaire au niveau de vol (FL300 - FL450).
        Dose ambiante normale au niveau FL360 ~ 4.5 µSv/h.
        """
        baseline_dose_usv_h = 4.5 * ((flight_level / 360.0) ** 2)
        additional_solar_dose = solar_proton_event_s_scale * 15.0

        total_dose_usv_h = baseline_dose_usv_h + additional_solar_dose

        if total_dose_usv_h > 20.0:
            advisory = "ICAO SWX RADIATION WARNING / DIVERT TO LOWER LATITUDES / ALTITUDES"
            risk = "HIGH"
        else:
            advisory = "NORMAL COSMIC RADIATION EXPOSURE"
            risk = "NORMAL"

        return {
            "flight_level": flight_level,
            "total_radiation_dose_usv_h": round(total_dose_usv_h, 2),
            "icao_advisory": advisory,
            "risk_level": risk,
        }
