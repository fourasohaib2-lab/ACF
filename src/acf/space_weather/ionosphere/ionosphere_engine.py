"""
Atmospheric Complexity Framework (ACF)

Ionosphere Dynamics, Total Electron Content (TEC) & Radio Blackout Module (Phase 4)
(TEC in TECU, foF2, MUF, GNSS Delay, NOAA Radio Blackout Scale R1-R5)
"""

from typing import Dict


class RadioBlackoutScale:
    """Classification des pannes de radio HF selon l'échelle NOAA Radio Blackouts (R1 à R5)."""

    @staticmethod
    def classify_xray_radio_blackout(xray_flux_w_m2: float) -> Dict[str, str]:
        """Détermine le niveau de dégradation HF (R1 à R5) selon le flux de rayons X GOES."""
        if xray_flux_w_m2 >= 2e-3:
            scale = "R5 - Extreme Radio Blackout"
            hf_impact = "Blackout HF total sur toute la face éclairée de la Terre pendant plusieurs heures."
        elif xray_flux_w_m2 >= 1e-3:
            scale = "R4 - Severe Radio Blackout"
            hf_impact = "Blackout HF sur la plupart des fréquences radio haute fréquence."
        elif xray_flux_w_m2 >= 1e-4:
            scale = "R3 - Strong Radio Blackout"
            hf_impact = "Degradation large des liaisons radio HF et pertes de signal de plusieurs minutes."
        elif xray_flux_w_m2 >= 5e-5:
            scale = "R2 - Moderate Radio Blackout"
            hf_impact = "Pertes partielles de signal HF côté jour."
        elif xray_flux_w_m2 >= 1e-5:
            scale = "R1 - Minor Radio Blackout"
            hf_impact = "Faibles dégradations des fréquences HF basses."
        else:
            scale = "R0 - Normal HF Propagation"
            hf_impact = "Aucune coupure radio HF."

        return {"radio_blackout_scale": scale, "hf_operational_impact": hf_impact}


class IonosphereEngine:
    """Moteur de modélisation ionosphérique et d'erreur de propagation GNSS / GPS."""

    @staticmethod
    def gnss_range_delay_meters(tec_tecu: float, frequency_hz: float = 1.57542e9) -> float:
        """
        Calcul du retard de groupe du signal GNSS (L1 GPS 1.57542 GHz) dû à l'ionosphère.
        Delta s = (40.3 / f²) * TEC (1 TECU = 10^16 électrons/m²).
        """
        tec_el_m2 = tec_tecu * 1e16
        delay_m = (40.3 / (frequency_hz ** 2)) * tec_el_m2
        return delay_m

    @staticmethod
    def maximum_usable_frequency_muf_mhz(fof2_mhz: float, distance_km: float = 3000.0) -> float:
        """Calcul approximatif de la fréquence maximale utilisable MUF = foF2 * M(3000)."""
        m_factor = 3.0  # Facteur M(3000) standard
        return fof2_mhz * m_factor
