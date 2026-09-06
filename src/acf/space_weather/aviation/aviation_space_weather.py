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

        NOTE (Physics Guard, 2026-09-06 Tier E sweep): the FL360
        reference value (~4.5 uSv/h) is a real, roughly-correct
        operational figure, but the quadratic (flight_level/360)**2
        scaling to other altitudes and the flat 15.0 uSv/h per S-scale
        step are illustrative approximations, not a cited dosimetry
        model (real cosmic-ray dose vs. altitude follows atmospheric
        depth/cutoff-rigidity physics, not a simple square law).
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
