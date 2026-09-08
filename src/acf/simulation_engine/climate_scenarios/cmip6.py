"""CMIP6 Shared Socioeconomic Pathways (SSP) scenario driver."""

from enum import Enum
from typing import Any

import numpy as np


class SSPScenario(Enum):
    """CMIP6 Standard Shared Socioeconomic Pathways."""

    SSP1_19 = "SSP1-1.9"  # Very low emissions / 1.5°C target
    SSP2_45 = "SSP2-4.5"  # Intermediate emissions
    SSP3_70 = "SSP3-7.0"  # High emissions
    SSP5_85 = "SSP5-8.5"  # Very high emissions


class CMIP6Engine:
    """CMIP6 Greenhouse Gas & Aerosol Radiative Forcing Pathway Generator.

    Provides projected GHG concentrations (CO2 ppm, CH4 ppb, N2O ppb) and
    effective radiative forcing ERF (W/m^2) for target year [2020..2300].
    """

    def __init__(self, scenario: SSPScenario = SSPScenario.SSP2_45) -> None:
        self.scenario = scenario

    def get_ghg_concentrations(self, year: float) -> dict[str, Any]:
        """Compute projected GHG concentration for given year under active SSP scenario.

        Args:
            year (float): Target year (e.g. 2030, 2050, 2100, 2300).

        Returns:
            Dict[str, float]: Dictionary of CO2 (ppm), CH4 (ppb), N2O (ppb), and ERF (W/m^2).
        """
        year_clamped = max(2020.0, min(2300.0, float(year)))
        dt_years = year_clamped - 2020.0

        if self.scenario == SSPScenario.SSP1_19:
            co2 = 415.0 + 0.8 * dt_years - max(0.0, 0.01 * (dt_years - 30) ** 2)
            erf = 1.9 * (dt_years / 80.0)
        elif self.scenario == SSPScenario.SSP2_45:
            co2 = 415.0 + 2.5 * dt_years
            erf = 4.5 * (dt_years / 80.0)
        elif self.scenario == SSPScenario.SSP3_70:
            co2 = 415.0 + 4.0 * dt_years + 0.02 * (dt_years**2)
            erf = 7.0 * (dt_years / 80.0)
        else:  # SSP5_85
            co2 = 415.0 + 6.0 * dt_years + 0.05 * (dt_years**2)
            erf = 8.5 * (dt_years / 80.0)

        # Baseline CH4 and N2O scaling
        ch4 = 1870.0 + 5.0 * dt_years
        n2o = 332.0 + 0.8 * dt_years

        return {
            "scenario": self.scenario.value,
            "year": year_clamped,
            "CO2_ppm": float(np.clip(co2, 350.0, 2000.0)),
            "CH4_ppb": float(ch4),
            "N2O_ppb": float(n2o),
            "radiative_forcing_wm2": float(erf),
        }
