"""
Atmospheric Complexity Framework (ACF)

Digital Twin AI Reasoning Engine Module (Phase 7)
(Causal Explanations for Tropical Cyclones, Volcanic Climate Forcing, Sea Level Rise, Space Weather GPS Outage)
"""

from typing import Any


class DigitalTwinReasoningEngine:
    """
    Moteur d'IA explicative et de raisonnement causal du Digital Twin planétaire.
    """

    @classmethod
    def explain_system_event(cls, event_type: str) -> dict[str, Any]:
        """
        Génère une explication physique et causale pour un événement Earth System complexe.

        NOTE (correction): the branch selection and the explanatory
        text are genuine (real physical thresholds: SST > 26.5 degC
        for cyclone rapid intensification per Palmen 1948, Kp >= 7 for
        geomagnetic disturbance, VEI >= 5 for a Plinian eruption), but
        each branch used to also claim a specific fabricated
        "ai_confidence_pct" (94.2/96.8/98.0/90.0 default) regardless of
        any real evidence for the specific event passed in - no
        calibrated confidence model exists here. Not fabricated.
        """
        e = event_type.lower()

        if "cyclone" in e or "ouragan" in e:
            return {
                "event_type": "Tropical Cyclone Rapid Intensification",
                "explanation": (
                    "L'intensification rapide se produit lorsque la température de surface de la mer dépasse 26.5°C (SST), "
                    "combinée à un faible cisaillement vertical du vent (< 10 kt) et un fort contenu en eau précipitable (PWV > 55 mm)."
                ),
                "ai_confidence_pct": None,
            }
        elif "volcano" in e or "volcan" in e:
            return {
                "event_type": "Volcanic Eruption Climate Forcing",
                "explanation": (
                    "L'injection d'injection massive de SO2 dans la stratosphère lors d'une éruption Plinienne (VEI >= 5) "
                    "forme des aérosols de sulfate (H2SO4) qui réfléchissent le rayonnement solaire incident, provoquant un refroidissement global."
                ),
                "ai_confidence_pct": None,
            }
        elif "kp" in e or "space" in e or "gps" in e:
            return {
                "event_type": "Geomagnetic Storm GPS Disturbance",
                "explanation": (
                    "L'élévation de l'indice Kp (>= 7) provoque des scintillements ionosphériques et une augmentation du Contenu Électronique Total (TEC), "
                    "induisant un retard de groupe de phase sur la fréquence L1/L2 du signal GPS (Delta s = 40.3/f² * TEC)."
                ),
                "ai_confidence_pct": None,
            }

        return {
            "event_type": event_type,
            "explanation": f"Explication par le moteur d'IA couplé du Digital Twin planétaire pour {event_type}.",
            "ai_confidence_pct": None,
        }
