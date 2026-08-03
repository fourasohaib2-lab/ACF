"""
Atmospheric Complexity Framework (ACF)

Van Allen Radiation Belts & Energetic Particle Charging Module (Phase 5)
(Inner/Outer Van Allen Belts, Radiation Dose, Surface & Deep Dielectric Charging)
"""

from typing import Any, Dict


class RadiationBeltsEngine:
    """
    Moteur de modélisation des Ceintures de Radiation de Van Allen et de risque de charge diélectrique satellite.
    """

    @staticmethod
    def evaluate_van_allen_belt_flux(altitude_km: float, electron_flux_gt_2mev: float) -> Dict[str, Any]:
        """Évalue l'exposition d'un satellite dans la Ceinture Interne ou Externe de Van Allen."""
        re_km = 6371.0
        r_re = 1.0 + (altitude_km / re_km)

        if r_re < 2.5:
            belt_zone = "Inner Van Allen Belt (Dominated by High-Energy Protons > 100 MeV)"
        elif r_re <= 7.0:
            belt_zone = "Outer Van Allen Belt (Dominated by Relativistic Electrons > 1 MeV)"
        else:
            belt_zone = "Magnetopause / Interplanetary Space"

        if electron_flux_gt_2mev >= 1e4:
            charging_risk = "HIGH / RISK OF DEEP DIELECTRIC CHARGING AND SINGLE EVENT UPSETS (SEU)"
        elif electron_flux_gt_2mev >= 1e3:
            charging_risk = "MODERATE / SURFACE CHARGING WATCH"
        else:
            charging_risk = "LOW / NORMAL RADIATION ENVIRONMENT"

        return {
            "altitude_km": altitude_km,
            "geocentric_distance_re": round(r_re, 2),
            "van_allen_zone": belt_zone,
            "relativist_electron_flux": electron_flux_gt_2mev,
            "charging_hazard_risk": charging_risk,
        }
