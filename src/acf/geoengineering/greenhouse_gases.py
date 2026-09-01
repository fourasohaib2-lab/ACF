"""
Atmospheric Complexity Framework (ACF)

Greenhouse Gas Physics & Radiative Forcing Engine Module (Phase 5)
(GreenhouseGasEngine for CO2, CH4, N2O, HFCs, PFCs, SF6 radiative forcing and GWP100)
"""

import math
from dataclasses import dataclass


@dataclass
class GHGProperties:
    """Propriétés radiatives et thermodynamiques d'un gaz à effet de serre (GES)."""

    gas_name: str
    chemical_formula: str
    current_concentration: float
    pre_industrial_concentration: float
    unit: str
    gwp_100: float  # Global Warming Potential sur 100 ans
    atmospheric_lifetime_years: float
    radiative_efficiency_w_m2_ppb: float


GHG_REGISTRY: dict[str, GHGProperties] = {
    "co2": GHGProperties("Carbon Dioxide", "CO2", 425.0, 280.0, "ppm", 1.0, 100.0, 1.37e-5),
    "ch4": GHGProperties("Methane", "CH4", 1920.0, 722.0, "ppb", 28.0, 11.8, 3.63e-4),
    "n2o": GHGProperties("Nitrous Oxide", "N2O", 336.0, 270.0, "ppb", 265.0, 109.0, 3.0e-3),
    "sf6": GHGProperties("Sulfur Hexafluoride", "SF6", 0.011, 0.0, "ppb", 23500.0, 3200.0, 0.57),
}


class GreenhouseGasEngine:
    """
    Moteur de calcul du forçage radiatif et du potentiel de réchauffement global (GWP) des GES.
    """

    @classmethod
    def co2_radiative_forcing(cls, c_ppm: float, c0_ppm: float = 280.0) -> float:
        """
        Calcule le forçage radiatif du CO2 par la formule du GIEC : F = 5.35 * ln(C / C0)

        Equations:
            F_{\\text{CO2}} = 5.35 \\cdot \\ln\\left(\\frac{C}{C_0}\\right)
        """
        return 5.35 * math.log(c_ppm / c0_ppm)

    @classmethod
    def get_ghg_properties(cls, gas_key: str) -> GHGProperties | None:
        """
        Retourne les propriétés radiatives du GES demandé, ou None si inconnu.

        NOTE (correction — silent mislabeling): an unrecognized gas_key
        (e.g. "hfc"/"pfc" - both named in this module's own docstring
        as covered gases but never added to GHG_REGISTRY - or a typo)
        used to silently fall back to CO2's properties, mislabeled as
        if it were the requested gas. get_ghg_properties("hfc") used
        to return a GHGProperties(gas_name="Carbon Dioxide", ...).
        """
        return GHG_REGISTRY.get(gas_key.lower())
