"""Long-term climate scenario solver across multi-century horizons."""

from typing import Dict, Any
import numpy as np
from acf.simulation_engine.climate_scenarios.cmip6 import CMIP6Engine, SSPScenario


class SSPEngine:
    """Long-term climate scenario horizon solver (2030, 2050, 2100, 2300).

    Computes projected global Earth state anomalies:
    - Global mean surface temperature warming Delta T (°C)
    - Global precipitation change Delta P (%)
    - Global sea level rise Delta eta (meters)
    - Polar sea-ice volume loss (%)
    - Ecosystem biodiversity vulnerability index ([0, 1])
    """

    def __init__(self, scenario: SSPScenario = SSPScenario.SSP2_45) -> None:
        self.cmip6 = CMIP6Engine(scenario)
        self.climate_sensitivity_tcr = 1.8  # Transient Climate Response (°C per CO2 doubling)

    def evaluate_horizon(self, target_year: int) -> Dict[str, Any]:
        """Simulate global Earth climate indicators for target year horizon.

        Args:
            target_year (int): Horizon year (e.g. 2030, 2050, 2100, 2300).

        Returns:
            Dict[str, Any]: Simulated climate indicators.
        """
        ghg_data = self.cmip6.get_ghg_concentrations(float(target_year))
        co2_ppm = ghg_data["CO2_ppm"]

        # Radiative forcing Delta F = 5.35 * ln(CO2 / 280)
        delta_f = 5.35 * np.log(co2_ppm / 280.0)

        # Global surface temperature warming Delta T = TCR * (Delta F / 3.7)
        delta_t = self.climate_sensitivity_tcr * (delta_f / 3.7)

        # Global mean precipitation increase ~ 2% per degree warming
        delta_p_pct = 2.0 * delta_t

        # Thermal expansion + ice melt sea level rise Delta eta ~ 0.004 m / yr * (Delta T)
        dt_years = max(0.0, target_year - 2020.0)
        sea_level_rise_m = 0.003 * dt_years * (delta_t / 1.5)

        # Polar sea-ice loss ~ 15% per degree warming
        sea_ice_loss_pct = np.clip(15.0 * delta_t, 0.0, 100.0)

        # Ecosystem vulnerability index
        biodiversity_vulnerability = np.clip(delta_t / 4.0, 0.0, 1.0)

        return {
            "target_year": target_year,
            "scenario": self.cmip6.scenario.value,
            "CO2_ppm": co2_ppm,
            "global_temp_anomaly_c": float(delta_t),
            "global_precip_change_pct": float(delta_p_pct),
            "sea_level_rise_m": float(sea_level_rise_m),
            "sea_ice_loss_pct": float(sea_ice_loss_pct),
            "biodiversity_vulnerability": float(biodiversity_vulnerability),
        }
