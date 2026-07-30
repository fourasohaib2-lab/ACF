"""
Atmospheric Complexity Framework (ACF)

Cloud-Aerosol Interaction Engine
"""

import math
from typing import Dict
from acf.science.clouds.base import CloudProcess
from acf.science.clouds.registry import CloudScientificRegistry


class CloudAerosolEngine:
    """
    Moteur d'interaction entre les aérosols et les nuages (CCN, INP, activation, effet Twomey).
    """

    def __init__(self):
        self._register_aerosol_processes()

    def _register_aerosol_processes(self):
        processes = [
            CloudProcess(
                key="ccn_activation_twomey",
                name="Activation CCN (Relation de Twomey)",
                domain="Interaction Aérosols-Nuages",
                equation="N_ccn = C_0 * S^k",
                variables={"S": "Sursaturation relative (%)", "C_0": "Concentration d'aérosols à S=1%", "k": "Exposant empirique"},
                units={"N_ccn": "cm⁻³"},
                description="Nombre de noyaux de condensation activés en fonction de la sursaturation.",
                references=["Twomey (1959) Geofis. Pura Appl.", "IPCC AR6 Radiation Docs"],
                compute_func=self.twomey_ccn_activation,
            ),
            CloudProcess(
                key="inp_freezing_meyers",
                name="Activation INP (Meyers et al.)",
                domain="Interaction Aérosols-Nuages",
                equation="N_inp = exp(a_inp + b_inp * S_ice)",
                variables={"S_ice": "Sursaturation par rapport à la glace"},
                units={"N_inp": "L⁻¹"},
                description="Concentration de noyaux glaçogènes activés pour la congélation hétérogène.",
                references=["Meyers et al. (1992) J. Appl. Meteor."],
                compute_func=self.meyers_inp_activation,
            ),
        ]
        for p in processes:
            CloudScientificRegistry.register(p)

    def twomey_ccn_activation(self, supersaturation_percent: float, c0: float = 1000.0, k: float = 0.5) -> float:
        """Calcule N_ccn = C_0 * S^k."""
        if supersaturation_percent <= 0:
            return 0.0
        return c0 * (supersaturation_percent ** k)

    def meyers_inp_activation(self, supersaturation_ice_percent: float) -> float:
        """Calcule N_inp en L⁻¹."""
        if supersaturation_ice_percent <= 0:
            return 0.0
        return math.exp(-0.639 + 0.1296 * supersaturation_ice_percent)

    def twomey_first_indirect_effect(self, ccn_base_cm3: float, ccn_polluted_cm3: float, cloud_water_path: float = 100.0) -> Dict[str, float]:
        """
        Calcule le 1er effet indirect des aérosols (Effet Twomey): augmentation de l'albédo nuageux sous forte pollution.
        """
        # Effective radius scales as N^(-1/3)
        r_eff_base = 12.0
        r_eff_polluted = r_eff_base * ((ccn_base_cm3 / max(ccn_polluted_cm3, 1.0)) ** (1.0 / 3.0))

        # Optical depth scales as r_eff^(-1)
        tau_base = 10.0
        tau_polluted = tau_base * (r_eff_base / max(r_eff_polluted, 1e-3))

        albedo_base = tau_base / (tau_base + 6.7)
        albedo_polluted = tau_polluted / (tau_polluted + 6.7)

        return {
            "r_eff_base_um": r_eff_base,
            "r_eff_polluted_um": r_eff_polluted,
            "albedo_base": albedo_base,
            "albedo_polluted": albedo_polluted,
            "albedo_increase": albedo_polluted - albedo_base,
        }
