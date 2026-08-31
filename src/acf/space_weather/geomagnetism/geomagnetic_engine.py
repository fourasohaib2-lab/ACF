"""
Atmospheric Complexity Framework (ACF)

Geomagnetism, Magnetosphere & NOAA Storm Scales Module (Phase 3)
(Magnetopause Standoff Distance Rmp, Geomagnetic Indices Kp, Dst, Ap, NOAA G1-G5 Scales)
"""

from typing import Any


class GeomagneticStormScale:
    """Classification des tempêtes géomagnétiques selon l'échelle NOAA (G1 à G5)."""

    @staticmethod
    def classify_kp_index(kp_value: float) -> dict[str, str]:
        """Convertit l'indice Kp (0 à 9) en tempête géomagnétique NOAA G1-G5."""
        if kp_value >= 9.0:
            scale = "G5 - Extreme Geomagnetic Storm"
            impacts = (
                "Effondrement possible de réseaux électriques, panne totale de télécoms HF et d'orientation satellite."
            )
        elif kp_value >= 8.0:
            scale = "G4 - Severe Geomagnetic Storm"
            impacts = "Problèmes de contrôle de tension des réseaux électriques, aurores visibles aux basses latitudes."
        elif kp_value >= 7.0:
            scale = "G3 - Strong Geomagnetic Storm"
            impacts = "Corrections d'orientation satellite requises, dégradations de la navigation GPS."
        elif kp_value >= 6.0:
            scale = "G2 - Moderate Geomagnetic Storm"
            impacts = "Alertes de tension sur les réseaux haute latitude, aurores visibles à 55° de latitude."
        elif kp_value >= 5.0:
            scale = "G1 - Minor Geomagnetic Storm"
            impacts = "Faibles fluctuations des réseaux électriques, aurores visibles au pôle."
        else:
            scale = "G0 - Quiet / Normal Geomagnetic Field"
            impacts = "Aucun impact opérationnel."

        return {"kp_index": str(round(kp_value, 1)), "noaa_scale": scale, "operational_impacts": impacts}


class GeomagneticEngine:
    """Moteur de physique magnétosphérique et de calcul de la distance à la magnétopause."""

    @staticmethod
    def magnetopause_standoff_distance_re(pdyn_npa: float, bz_nt: float = 0.0) -> float:
        """
        Calcul de la distance sous-solaire de la magnétopause Rmp (en rayons terrestres Re).
        Formule de Shue et al. (1998) : Rmp = (10.22 + 0.129 * Bz) * Pdyn^(-1/6.6).
        """
        if pdyn_npa <= 0.0:
            return 10.0

        r0 = 10.22 + 0.129 * bz_nt
        rmp = r0 * (pdyn_npa ** (-1.0 / 6.6))
        return max(4.0, min(15.0, rmp))

    @classmethod
    def evaluate_dst_index_severity(cls, dst_nt: float) -> dict[str, Any]:
        """Évalue l'intensité de la ceinture de courant (Ring Current) selon l'indice Dst (nT)."""
        if dst_nt <= -300.0:
            severity = "Superstorm (Dst <= -300 nT)"
        elif dst_nt <= -100.0:
            severity = "Intense Geomagnetic Storm"
        elif dst_nt <= -50.0:
            severity = "Moderate Geomagnetic Storm"
        else:
            severity = "Quiet / Mild Ring Current"

        return {
            "dst_nt": dst_nt,
            "severity": severity,
            "ring_current_intensity": f"Ring current energy shift {abs(dst_nt)} nT",
        }
