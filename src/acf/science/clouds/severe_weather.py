"""
Atmospheric Complexity Framework (ACF)

Severe Weather Cloud Module
"""

import math
from typing import Any, Dict


class SevereWeatherCloudModule:
    """
    Module scientifique dédié à la physique des nuages d'orages violents, supercellules et indices d'instabilité.
    """

    def lifted_index(self, t_500_c: float, t_parcel_500_c: float) -> float:
        """LI = T_500 - T_parcel_500."""
        return t_500_c - t_parcel_500_c

    def showalter_index(self, t_500_c: float, t_parcel_850_to_500_c: float) -> float:
        """Showalter Index = T_500 - T_parcel_850_lifted_to_500."""
        return t_500_c - t_parcel_850_to_500_c

    def total_totals_index(self, t_850_c: float, td_850_c: float, t_500_c: float) -> float:
        """TT = (T_850 - T_500) + (Td_850 - T_500)."""
        return (t_850_c - t_500_c) + (td_850_c - t_500_c)

    def k_index(self, t_850_c: float, td_850_c: float, t_700_c: float, td_700_c: float, t_500_c: float) -> float:
        """K Index = (T_850 - T_500) + Td_850 - (T_700 - Td_700)."""
        return (t_850_c - t_500_c) + td_850_c - (t_700_c - td_700_c)

    def sweat_index(
        self,
        td_850_c: float,
        total_totals: float,
        wind_speed_850_kt: float,
        wind_speed_500_kt: float,
        wind_dir_850_deg: float,
        wind_dir_500_deg: float,
    ) -> float:
        """
        SWEAT Index (Severe Weather Threat Index).
        """
        term1 = 12.0 * max(td_850_c, 0.0)
        term2 = 20.0 * max(total_totals - 49.0, 0.0)
        term3 = 2.0 * wind_speed_850_kt + wind_speed_500_kt

        # Shear term
        s = math.sin(math.radians(wind_dir_500_deg - wind_dir_850_deg))
        term4 = 125.0 * (s + 0.2) if s > 0 else 0.0

        return term1 + term2 + term3 + term4

    def hail_risk_assessment(self, cape_j_kg: float, freezing_level_m: float, updraft_w_max: float) -> Dict[str, Any]:
        """
        Évalue le risque de grêle sévère sous un Cumulonimbus.
        """
        hail_diameter_cm = 0.0
        if cape_j_kg > 2000 and updraft_w_max > 30.0:
            hail_diameter_cm = 0.05 * updraft_w_max
            risk_level = "Élevé à Extrême (Grosse grêle > 2 cm)"
        elif cape_j_kg > 1000 and updraft_w_max > 15.0:
            hail_diameter_cm = 1.0
            risk_level = "Modéré (Grésil / Petites grêles)"
        else:
            risk_level = "Faible / Nul"

        return {
            "CAPE_J_kg": cape_j_kg,
            "max_updraft_m_s": updraft_w_max,
            "estimated_hail_diameter_cm": hail_diameter_cm,
            "risk_level": risk_level,
        }

    def supercell_indicators(
        self,
        cape_j_kg: float,
        storm_relative_helicity_m2_s2: float,
        bulk_shear_0_6km_m_s: float,
    ) -> Dict[str, Any]:
        """
        Calcule les indicateurs de supercellule (Supercell Composite Parameter SCP & EHI).
        """
        # Supercell Composite Parameter (SCP)
        scp = (cape_j_kg / 1000.0) * (storm_relative_helicity_m2_s2 / 50.0) * (bulk_shear_0_6km_m_s / 20.0)

        # Energy Helicity Index (EHI)
        ehi = (cape_j_kg * storm_relative_helicity_m2_s2) / 160000.0

        is_supercell = scp > 1.0 or ehi > 1.0

        return {
            "SCP": scp,
            "EHI": ehi,
            "supercell_favorable": is_supercell,
            "mesocyclone_potential": "Élevé" if ehi > 2.0 else "Faible/Modéré",
        }
