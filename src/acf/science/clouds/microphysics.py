"""
Atmospheric Complexity Framework (ACF)

Cloud Microphysics Engine
"""

import math
from typing import Dict
from acf.science.clouds.base import CloudProcess
from acf.science.clouds.registry import CloudScientificRegistry


class CloudMicrophysicsEngine:
    """
    Moteur complet de microphysique des nuages (warm & cold cloud microphysics).
    """

    def __init__(self):
        self._register_microphysics_processes()

    def _register_microphysics_processes(self):
        processes = [
            CloudProcess(
                key="kessler_autoconversion",
                name="Schéma d'Autoconversion de Kessler",
                domain="Microphysique Nuageuse",
                equation="P_auto = k_auto * max(qc - qc_crit, 0)",
                variables={"qc": "Eau liquide nuageuse (kg/kg)", "qc_crit": "Seuil critique (kg/kg)"},
                units={"P_auto": "kg/(kg·s)"},
                description="Conversion des gouttelettes de nuage en gouttes de pluie par collision.",
                references=["Kessler (1969)", "WMO Cloud Physics Guidelines"],
                compute_func=self.kessler_autoconversion,
            ),
            CloudProcess(
                key="berry_autoconversion",
                name="Schéma d'Autoconversion de Berry",
                domain="Microphysique Nuageuse",
                equation="P_berry = (qc^2 * rho) / (60 * (1 + 0.03 * N / qc))",
                variables={"qc": "Eau nuageuse (kg/kg)", "N": "Concentration de gouttelettes (cm⁻³)"},
                units={"P_berry": "kg/(kg·s)"},
                description="Formulation de Berry prenant en compte la concentration numérique des gouttelettes.",
                references=["Berry (1968) J. Atmos. Sci."],
                compute_func=self.berry_autoconversion,
            ),
            CloudProcess(
                key="kohler_theory",
                name="Théorie de Köhler (Activation CCN)",
                domain="Microphysique Nuageuse",
                equation="ln(e/es) = A/r - B/r^3",
                variables={"r": "Rayon de la gouttelette (m)", "A": "Effet de courbure", "B": "Effet de soluté"},
                units={"e/es": "Sursaturation relative"},
                description="Équilibre de la pression de vapeur d'eau autour d'une gouttelette contenant un soluté dissous.",
                references=["Köhler (1936)", "Pruppacher & Klett (1997)"],
                compute_func=self.kohler_equilibrium,
            ),
            CloudProcess(
                key="collision_coalescence",
                name="Collision-Coalescence",
                domain="Microphysique Nuageuse",
                equation="P_coll = k_coll * qc * qr**0.875",
                variables={"qc": "Eau nuageuse", "qr": "Pluie"},
                units={"P_coll": "kg/(kg·s)"},
                description="Grossissement des gouttes de pluie par capture des gouttelettes nuageuses.",
                references=["Kessler (1969)", "Rogers & Yau (1989)"],
                compute_func=self.collision_coalescence,
            ),
            CloudProcess(
                key="rain_evaporation",
                name="Évaporation de la Pluie",
                domain="Microphysique Nuageuse",
                equation="E_rain = C_evap * (1 - RH) * qr**0.52",
                variables={"qr": "Pluie", "RH": "Humidité relative [0, 1]"},
                units={"E_rain": "kg/(kg·s)"},
                description="Sous-sursaturation entraînant la réévaporation des gouttes de pluie sous la base du nuage.",
                references=["ECMWF Microphysics Documentation"],
                compute_func=self.rain_evaporation,
            ),
            CloudProcess(
                key="bergeron_findeisen",
                name="Processus Bergeron-Findeisen",
                domain="Microphysique Nuageuse",
                equation="dm_ice/dt = 4*pi*C*(esi - esw) / (F_k + F_d)",
                variables={"esi": "Saturation / glace", "esw": "Saturation / eau"},
                units={"dm_ice/dt": "kg/s"},
                description="Croissance des cristaux de glace au détriment des gouttes d'eau surfondues dues à la différence de pression de vapeur de saturation.",
                references=["WMO Manual", "Pruppacher & Klett (1997)"],
                compute_func=self.bergeron_findeisen_rate,
            ),
            CloudProcess(
                key="homogeneous_freezing",
                name="Congélation Homogène",
                domain="Microphysique Nuageuse",
                equation="J_hom = V_drop * A_hom * exp(B_hom / (T - T_hom))",
                variables={"T": "Température (< -38°C)"},
                units={"J_hom": "s⁻¹"},
                description="Congélation spontanée des gouttelettes d'eau pure à des températures inférieures à -38°C.",
                references=["Koop et al. (2000) Nature"],
                compute_func=self.homogeneous_freezing_rate,
            ),
            CloudProcess(
                key="riming_graupel",
                name="Givrage et Formation de Grésil (Riming)",
                domain="Microphysique Nuageuse",
                equation="P_rim = E_rim * qc * v_fall_ice",
                variables={"qc": "Eau liquide surfondue", "v_fall": "Vitesse de chute"},
                units={"P_rim": "kg/(kg·s)"},
                description="Capture et congélation immédiate d'eau surfondu sur la surface de cristaux de neige ou de grésil.",
                references=["Rutledge & Hobbs (1983) J. Atmos. Sci."],
                compute_func=self.riming_rate,
            ),
        ]
        for p in processes:
            CloudScientificRegistry.register(p)

    def kessler_autoconversion(self, qc: float, qc_crit: float = 0.0005, k_auto: float = 0.001) -> float:
        return k_auto * max(qc - qc_crit, 0.0)

    def berry_autoconversion(self, qc: float, N_cm3: float = 100.0, density: float = 1.2) -> float:
        if qc <= 0:
            return 0.0
        return (qc ** 2 * density) / (60.0 * (1.0 + 0.03 * N_cm3 / max(qc, 1e-6)))

    def kohler_equilibrium(self, radius_m: float, solute_moles: float = 1e-18, temp_k: float = 288.15) -> float:
        # A = 2*sigma / (rho_w * R_v * T)
        A = 1.1e-9 / temp_k
        B = 4.3e-6 * solute_moles
        return 1.0 + A / max(radius_m, 1e-10) - B / max(radius_m ** 3, 1e-30)

    def collision_coalescence(self, qc: float, qr: float, k_coll: float = 2.2) -> float:
        if qc <= 0 or qr <= 0:
            return 0.0
        return k_coll * qc * (qr ** 0.875)

    def rain_evaporation(self, qr: float, rh: float, temp_k: float = 288.15) -> float:
        if qr <= 0 or rh >= 1.0:
            return 0.0
        return 1.41e-3 * (1.0 - rh) * (qr ** 0.52)

    def bergeron_findeisen_rate(self, temp_k: float, qi: float, qc: float) -> float:
        if temp_k >= 273.15 or qc <= 0:
            return 0.0
        # Difference between saturation over water and ice
        es_w = 611.2 * math.exp((17.67 * (temp_k - 273.15)) / (temp_k - 29.65))
        es_i = 611.2 * math.exp((22.51 * (temp_k - 273.15)) / (temp_k - 0.7))
        return 1e-5 * max(es_w - es_i, 0.0) * max(qi, 1e-6)

    def homogeneous_freezing_rate(self, temp_k: float, qc: float) -> float:
        if temp_k > 235.15 or qc <= 0:
            return 0.0
        return qc * 0.1  # Rapid conversion below -38°C

    def riming_rate(self, qc: float, qs: float) -> float:
        if qc <= 0 or qs <= 0:
            return 0.0
        return 0.05 * qc * (qs ** 0.9)

    def compute_budget(self, qv: float, qc: float, qr: float, qi: float, qs: float, qg: float, dt: float = 1.0) -> Dict[str, float]:
        """
        Calcule la conservation de la masse d'eau entre les 6 phases: qv, qc, qr, qi, qs, qg.
        """
        # Autoconversion
        p_auto = self.kessler_autoconversion(qc)
        # Collection
        p_coll = self.collision_coalescence(qc, qr)

        dqc = -(p_auto + p_coll) * dt
        dqr = (p_auto + p_coll) * dt

        # Ensure non-negative species
        new_qc = max(qc + dqc, 0.0)
        new_qr = max(qr + dqr, 0.0)

        total_water_before = qv + qc + qr + qi + qs + qg
        total_water_after = qv + new_qc + new_qr + qi + qs + qg

        return {
            "qv": qv,
            "qc": new_qc,
            "qr": new_qr,
            "qi": qi,
            "qs": qs,
            "qg": qg,
            "total_water": total_water_after,
            "mass_conserved": abs(total_water_before - total_water_after) < 1e-12,
        }
