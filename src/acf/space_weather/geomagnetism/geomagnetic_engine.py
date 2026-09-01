"""
Atmospheric Complexity Framework (ACF)

Geomagnetism, Magnetosphere & NOAA Storm Scales Module (Phase 3)
(Magnetopause Standoff Distance Rmp, Geomagnetic Indices Kp, Dst, Ap, NOAA G1-G5 Scales)
"""

import math
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
        Formule de Shue et al. (1997/1998) :
        Rmp = (10.22 + 1.29 * tanh[0.184 * (Bz + 8.14)]) * Pdyn^(-1/6.6).

        NOTE (correction): the Bz term was implemented as a raw linear
        "10.22 + 0.129 * Bz" - both the wrong coefficient (0.129
        instead of 1.29, a factor of 10) and missing the paper's tanh
        saturation entirely (no "+8.14" offset, no bound on the term's
        contribution). Labeled as Shue et al. (1998) while not actually
        computing that formula. The linear form has no physical
        saturation, so for a strongly southward Bz (exactly the
        geoeffective condition this function exists to characterize -
        e.g. Bz around -50 nT in an extreme storm) it collapsed the
        standoff distance all the way to the clamped floor of 4.0 Re;
        the real tanh term instead saturates at -1.29 (r0 floors near
        10.22 - 1.29 ≈ 8.9 Re before the Pdyn scaling), matching the
        physically expected bound on how far the magnetopause
        compresses even under an extreme southward IMF.
        See Shue, J.-H., et al. (1997), "A new functional form to study
        the solar wind control of the magnetopause size and shape",
        J. Geophys. Res., 102(A5), 9497-9511.
        """
        if pdyn_npa <= 0.0:
            return 10.0

        r0 = 10.22 + 1.29 * math.tanh(0.184 * (bz_nt + 8.14))
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
