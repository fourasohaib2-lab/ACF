"""
Atmospheric Complexity Framework (ACF)

Cloud Thermodynamics Engine
"""

import math
from typing import Any

from acf.science.clouds.base import CloudProcess
from acf.science.clouds.registry import CloudScientificRegistry


class CloudThermodynamicsEngine:
    """
    Moteur de thermodynamique des nuages (LCL, LFC, EL, CAPE, CIN, pseudo-adiabates).
    """

    def __init__(self):
        self._register_thermodynamic_processes()

    def _register_thermodynamic_processes(self):
        processes = [
            CloudProcess(
                key="cape_integral",
                name="Calcul d'Énergie Potentielle Convective Disponible (CAPE)",
                domain="Thermodynamique Nuageuse",
                equation="CAPE = int_(LFC)^(EL) g * (Tparcel - Tenv) / Tenv dz",
                variables={"Tparcel": "Température de la parcelle (K)", "Tenv": "Température de l'environnement (K)"},
                units={"CAPE": "J/kg"},
                description="Intégrale de la poussée d'Archimède positive entre le niveau de libre convection (LFC) et le niveau d'équilibre (EL).",
                references=["WMO Atmospheric Thermodynamics Guidelines", "Holton & Hakim (2012)"],
                compute_func=self.calculate_cape,
            ),
            CloudProcess(
                key="cin_integral",
                name="Inhibition Convective (CIN)",
                domain="Thermodynamique Nuageuse",
                equation="CIN = - int_(SFC)^(LFC) g * (Tparcel - Tenv) / Tenv dz",
                variables={"Tparcel": "Température parcelle", "Tenv": "Température environnement"},
                units={"CIN": "J/kg"},
                description="Travail nécessaire pour amener la parcelle d'air du sol jusqu'au LFC.",
                references=["WMO Severe Weather Guide", "ECMWF Dynamics Documentation"],
                compute_func=self.calculate_cin,
            ),
            CloudProcess(
                key="lcl_altitude",
                name="Niveau de Condensation par Soulevement (LCL)",
                domain="Thermodynamique Nuageuse",
                equation="z_LCL = 125.0 * (T - Td)",
                variables={"T": "Température sol (°C)", "Td": "Point de rosée (°C)"},
                units={"z_LCL": "m"},
                description="Altitude approximative de la base du nuage convectif formé par soulèvement adiabatique sec.",
                references=["Espy (1841)", "Lawrence (2005) Bull. Amer. Meteor. Soc."],
                compute_func=self.calculate_lcl,
            ),
        ]
        for p in processes:
            CloudScientificRegistry.register(p)

    def saturation_vapor_pressure(self, temp_k: float) -> float:
        """Pression de vapeur saturante es(T) en Pa (Formule de Tetens)."""
        temp_c = temp_k - 273.15
        if temp_c >= 0:
            return 611.2 * math.exp((17.67 * temp_c) / (temp_c + 243.5))
        return 611.2 * math.exp((22.51 * temp_c) / (temp_c + 273.1))

    def mixing_ratio(self, vapor_pressure_pa: float, total_pressure_pa: float) -> float:
        """Rapport de mélange r en kg/kg."""
        return 0.622 * vapor_pressure_pa / max(total_pressure_pa - vapor_pressure_pa, 1.0)

    def virtual_temperature(self, temp_k: float, mixing_ratio_kg_kg: float) -> float:
        """Température virtuelle Tv en K."""
        return temp_k * (1.0 + 0.61 * mixing_ratio_kg_kg)

    def calculate_lcl(self, temp_k: float, dewpoint_k: float) -> float:
        """Altitude approximative du LCL en mètres."""
        temp_c = temp_k - 273.15
        td_c = dewpoint_k - 273.15
        return max(125.0 * (temp_c - td_c), 0.0)

    def calculate_cape(
        self, z_levels: list[float], t_env_k: list[float], t_parcel_k: list[float], g: float = 9.81
    ) -> float:
        """
        Calcule l'intégrale du CAPE = int g * (Tparcel - Tenv) / Tenv dz pour Tparcel > Tenv.
        """
        cape = 0.0
        n = min(len(z_levels), len(t_env_k), len(t_parcel_k))
        for i in range(n - 1):
            dz = z_levels[i + 1] - z_levels[i]
            t_env_avg = 0.5 * (t_env_k[i] + t_env_k[i + 1])
            t_parcel_avg = 0.5 * (t_parcel_k[i] + t_parcel_k[i + 1])
            dT = t_parcel_avg - t_env_avg
            if dT > 0 and t_env_avg > 0:
                cape += g * (dT / t_env_avg) * dz
        return cape

    def calculate_cin(
        self, z_levels: list[float], t_env_k: list[float], t_parcel_k: list[float], g: float = 9.81
    ) -> float:
        """
        Calcule l'intégrale du CIN = - int g * (Tparcel - Tenv) / Tenv dz pour Tparcel < Tenv sous le LFC.
        """
        cin = 0.0
        n = min(len(z_levels), len(t_env_k), len(t_parcel_k))
        for i in range(n - 1):
            dz = z_levels[i + 1] - z_levels[i]
            t_env_avg = 0.5 * (t_env_k[i] + t_env_k[i + 1])
            t_parcel_avg = 0.5 * (t_parcel_k[i] + t_parcel_k[i + 1])
            dT = t_parcel_avg - t_env_avg
            if dT < 0 and t_env_avg > 0:
                cin += g * (-dT / t_env_avg) * dz
        return cin

    def convective_sounding_analysis(
        self, z_levels: list[float], p_levels: list[float], t_env: list[float], td_env: list[float]
    ) -> dict[str, Any]:
        """
        Effectue une analyse thermodynamique complète du profil vertical.
        """
        # Parcel trajectory assuming surface air parcel
        t_sfc = t_env[0]
        td_sfc = td_env[0]
        lcl_z = self.calculate_lcl(t_sfc, td_sfc)

        # Build parcel temperature profile along dry adiabat to LCL, then moist adiabat
        t_parcel = []
        for z in z_levels:
            if z <= lcl_z:
                # Dry adiabatic lapse rate (~9.8 K/km)
                t_p = t_sfc - 0.0098 * z
            else:
                # Moist adiabatic lapse rate (~6.0 K/km)
                t_p = (t_sfc - 0.0098 * lcl_z) - 0.0060 * (z - lcl_z)
            t_parcel.append(t_p)

        cape = self.calculate_cape(z_levels, t_env, t_parcel)
        cin = self.calculate_cin(z_levels, t_env, t_parcel)

        return {
            "LCL_altitude_m": lcl_z,
            "CAPE_J_kg": cape,
            "CIN_J_kg": cin,
            "parcel_temperature_profile": t_parcel,
        }
