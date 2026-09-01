"""
Atmospheric Complexity Framework (ACF)

Global Solar Physics, Solar Flares & Coronal Mass Ejections Module (Phase 1)
(Solar Cycles 24/25, Sunspots, Wolf Number R = k(10g + s), GOES Flare Classes C/M/X, CMEs)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class CoronalMassEjectionInfo:
    """Description d'une Éjection de Masse Coronale (CME) émise par le Soleil."""

    cme_id: str  # e.g., "CME-2026-08-02-01"
    active_region: str  # e.g., "AR13664"
    speed_km_s: float
    angular_width_deg: float
    is_halo_cme: bool
    direction_earth_directed: bool
    estimated_arrival_earth_hours: float


class SolarFlareEngine:
    """Moteur d'analyse des éruptions solaires (Flares) basées sur le flux X bruts des satellites GOES."""

    @staticmethod
    def classify_goes_xray_flare(xray_flux_w_m2: float) -> dict[str, str]:
        """Classifie les éruptions solaires selon l'échelle GOES (A, B, C, M, X)."""
        if xray_flux_w_m2 >= 1e-4:
            class_letter = f"X{round(xray_flux_w_m2 / 1e-4, 1)}"
            severity = "Extreme Solar Flare"
        elif xray_flux_w_m2 >= 1e-5:
            class_letter = f"M{round(xray_flux_w_m2 / 1e-5, 1)}"
            severity = "Moderate Solar Flare"
        elif xray_flux_w_m2 >= 1e-6:
            class_letter = f"C{round(xray_flux_w_m2 / 1e-6, 1)}"
            severity = "Common Solar Flare"
        elif xray_flux_w_m2 >= 1e-7:
            class_letter = f"B{round(xray_flux_w_m2 / 1e-7, 1)}"
            severity = "Low Solar Activity"
        else:
            class_letter = "A-Class"
            severity = "Quiet Sun Background"

        return {"flare_class": class_letter, "severity": severity, "xray_flux_w_m2": str(xray_flux_w_m2)}


class SolarDatabase:
    """Base de données et registre de la physique solaire et des cycles d'activité de 11 ans."""

    SOLAR_CONSTANT_W_M2 = 1361.0

    @staticmethod
    def wolf_sunspot_number(num_groups: int, num_spots: int, k_factor: float = 1.0) -> float:
        """Calcul du nombre de taches solaires de Wolf R = k * (10 * g + s)."""
        return k_factor * (10.0 * num_groups + num_spots)

    @classmethod
    def get_solar_cycle_info(cls, cycle_number: int = 25) -> dict[str, Any]:
        """
        Retourne l'état d'un cycle d'activité solaire connu (24 ou 25 seulement).

        NOTE (correction — mislabeled fabrication): any cycle_number
        other than 25 used to silently return Cycle 24's data with
        "cycle": 24 hardcoded in the response, regardless of what was
        actually requested - get_solar_cycle_info(cycle_number=1) (or
        7, or 100) claimed to be describing Cycle 24. This tiny
        registry only actually holds real data for cycles 24 and 25;
        any other cycle_number now gets an explicit unknown-cycle
        response instead of a silent substitution.
        """
        if cycle_number == 25:
            return {
                "cycle": 25,
                "start_year": 2019,
                "solar_maximum_estimate": "2024-2026",
                "status": "Solar Maximum Phase",
                "average_sunspot_number": 155.0,
                "total_solar_irradiance_w_m2": cls.SOLAR_CONSTANT_W_M2,
            }
        if cycle_number == 24:
            return {
                "cycle": 24,
                "start_year": 2008,
                "end_year": 2019,
                "status": "Completed Cycle",
                "average_sunspot_number": 116.0,
            }
        return {
            "cycle": cycle_number,
            "status": "UNKNOWN_CYCLE_NOT_IN_REGISTRY",
            "known_cycles": [24, 25],
        }
