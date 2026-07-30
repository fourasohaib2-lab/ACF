"""
Atmospheric Complexity Framework (ACF)

Cloud Radiation Engine
"""

import math
from typing import Dict
from acf.science.clouds.base import CloudProcess
from acf.science.clouds.registry import CloudScientificRegistry


class CloudRadiationEngine:
    """
    Moteur de transfert radiatif des nuages (effet de serre nuageux, albédo, forçage radiatif).
    """

    SIGMA = 5.670374e-8  # W/(m²·K⁴)

    def __init__(self):
        self._register_radiation_processes()

    def _register_radiation_processes(self):
        processes = [
            CloudProcess(
                key="cloud_optical_depth",
                name="Épaisseur Optique du Nuage (COD)",
                domain="Rayonnement Nuageux",
                equation="tau = (3 * LWP) / (2 * rho_w * r_eff)",
                variables={"LWP": "Liquid Water Path (g/m²)", "r_eff": "Rayon effectif des gouttelettes (m)"},
                units={"tau": "dimensionless"},
                description="Atténuation de l'intensité lumineuse traversant la couche nuageuse.",
                references=["Stephens (1978) J. Atmos. Sci.", "Liou (2002)"],
                compute_func=self.cloud_optical_depth,
            ),
            CloudProcess(
                key="stefan_boltzmann_cloud",
                name="Loi de Stefan-Boltzmann d'Émission du Sommet du Nuage",
                domain="Rayonnement Nuageux",
                equation="F = epsilon * sigma * T_top^4",
                variables={"epsilon": "Émissivité infrarouge", "T_top": "Température du sommet du nuage (K)"},
                units={"F": "W/m²"},
                description="Émission infrarouge vers l'espace du sommet du nuage.",
                references=["WMO Radiation Guidelines"],
                compute_func=self.infrared_emission,
            ),
            CloudProcess(
                key="beer_lambert_cloud",
                name="Loi de Beer-Lambert d'Extinction",
                domain="Rayonnement Nuageux",
                equation="I = I0 * exp(-tau)",
                variables={"I0": "Intensité incidente", "tau": "Épaisseur optique nuageuse"},
                units={"I": "W/m²"},
                description="Transmission directe du rayonnement solaire à travers le nuage.",
                references=["Liou (2002)"],
                compute_func=self.transmission,
            ),
        ]
        for p in processes:
            CloudScientificRegistry.register(p)

    def cloud_optical_depth(self, liquid_water_path_g_m2: float, effective_radius_um: float = 10.0) -> float:
        """Calcule tau = (3 * LWP) / (2 * rho_w * r_eff)."""
        lwp_kg_m2 = liquid_water_path_g_m2 / 1000.0
        r_eff_m = effective_radius_um * 1e-6
        return (1.5 * lwp_kg_m2) / (1000.0 * max(r_eff_m, 1e-6))

    def cloud_albedo(self, optical_depth: float, g_asymmetry: float = 0.85) -> float:
        """Approximation à 2 flux de l'albédo nuageux A = (1 - g) * tau / (1 + (1 - g) * tau)."""
        factor = (1.0 - g_asymmetry) * optical_depth
        return factor / (1.0 + factor)

    def infrared_emission(self, temp_top_k: float, emissivity: float = 0.95) -> float:
        """Calcule le flux IR émis = epsilon * sigma * T^4."""
        return emissivity * self.SIGMA * (temp_top_k ** 4)

    def transmission(self, i0: float, optical_depth: float) -> float:
        """Calcule I = I0 * exp(-tau)."""
        return i0 * math.exp(-max(optical_depth, 0.0))

    def cloud_radiative_forcing(
        self,
        solar_incident_w_m2: float,
        cloud_albedo_val: float,
        clear_sky_albedo: float = 0.15,
        temp_surface_k: float = 288.15,
        temp_cloud_top_k: float = 240.15,
        emissivity: float = 0.95,
    ) -> Dict[str, float]:
        """
        Calcule le forçage radiatif nuageux (SWCF, LWCF et Forçage Net).
        """
        # Shortwave cloud forcing (cooling effect)
        swcf = -solar_incident_w_m2 * (cloud_albedo_val - clear_sky_albedo)

        # Longwave cloud forcing (greenhouse warming effect)
        olr_clear = self.SIGMA * (temp_surface_k ** 4)
        olr_cloud = self.infrared_emission(temp_cloud_top_k, emissivity)
        lwcf = olr_clear - olr_cloud

        net_forcing = swcf + lwcf

        return {
            "SWCF_W_m2": swcf,
            "LWCF_W_m2": lwcf,
            "Net_Forcing_W_m2": net_forcing,
            "cooling_dominated": net_forcing < 0,
        }
