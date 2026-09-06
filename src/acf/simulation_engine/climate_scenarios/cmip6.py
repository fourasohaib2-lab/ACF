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
    """Illustrative SSP-scenario GHG/ERF trajectory approximation.

    NOTE (Physics Guard, 2026-09-06 Tier C sweep): despite the class
    name, this does NOT read, replay, or interpolate real CMIP6 model
    ensemble output or IPCC AR6 assessment-report tables - verified by
    grep, there is no data file, network call, or CMIP6 archive access
    anywhere in this class. Each SSP branch below is a hand-written
    linear/quadratic function whose coefficients were chosen to land
    near plausible 2100 endpoint values for that scenario, not fitted
    to or sourced from any specific published CMIP6 model or IPCC
    table - e.g. the CH4/N2O trends are identical linear ramps shared
    across all four SSP scenarios, which real CMIP6 projections are
    not (methane pathways in particular diverge sharply by scenario).
    The one genuinely standard piece of science here is the ERF->
    warming relationship consumed downstream in ssp_engine.py
    (Delta F = 5.35 * ln(CO2/280), the real IPCC AR5/AR6 CO2 forcing
    formula) - this class only supplies that formula's CO2 input, via
    an approximation, not real data. Connected to the live ESOC GUI
    (acf.gui.esoc.esoc_controller.handle_run_climate) - a user
    selecting a scenario there sees this approximation's numbers, not
    genuine CMIP6 ensemble output.

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
