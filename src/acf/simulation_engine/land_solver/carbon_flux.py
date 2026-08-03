"""Terrestrial carbon cycle and atmospheric CO2 flux model."""

from typing import Dict
import numpy as np


class CarbonFluxModel:
    """Coupled carbon cycle solver tracking CO2 flux exchanges:

    Path: Atmospheric CO2 <-> Vegetation (Photosynthesis GPP) <-> Soil (Respiration R_h) -> Atmosphere

    Equations:
        GPP = f(PAR, T, SoilMoisture, CO2_conc)
        R_auto = 0.5 * GPP (Autotrophic respiration)
        NPP = GPP - R_auto
        R_hetero = k_soil * C_soil * Q10^((T-10)/10) (Soil microbial respiration)
        NEE = Net Ecosystem Exchange = R_total - GPP
    """

    def __init__(self) -> None:
        self.q10_factor = 2.0  # Temperature sensitivity factor for respiration

    def compute_carbon_fluxes(
        self,
        co2_ppm: float,
        npp_field: np.ndarray,
        soil_temp_k: np.ndarray,
        soil_carbon_stock: np.ndarray = None,
    ) -> Dict[str, np.ndarray]:
        """Compute Net Ecosystem Exchange (NEE) and CO2 flux components.

        Args:
            co2_ppm (float): Atmospheric CO2 concentration (ppmv).
            npp_field (np.ndarray): Net Primary Productivity (g C / m^2 / day).
            soil_temp_k (np.ndarray): Soil temperature (K).
            soil_carbon_stock (np.ndarray, optional): Soil organic carbon pool (g C / m^2).

        Returns:
            Dict[str, np.ndarray]: Carbon fluxes in g C / m^2 / day and net CO2 flux.
        """
        if soil_carbon_stock is None:
            soil_carbon_stock = np.full_like(npp_field, 10000.0, dtype=np.float64)

        temp_c = soil_temp_k - 273.15
        r_hetero = 0.0005 * soil_carbon_stock * (self.q10_factor ** ((temp_c - 10.0) / 10.0))

        # Gross Primary Productivity GPP = 2 * NPP
        gpp = 2.0 * npp_field

        # Net Ecosystem Exchange NEE = R_eco - GPP = R_hetero - NPP
        # Negative NEE means land surface acts as a Carbon Sink
        nee = r_hetero - npp_field

        return {
            "GPP": gpp,
            "NPP": npp_field,
            "R_hetero": r_hetero,
            "NEE": nee,
            "is_carbon_sink": nee < 0.0,
        }
