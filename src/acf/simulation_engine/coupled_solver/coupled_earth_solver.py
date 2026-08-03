"""Central Earth System Coupled Solver for multi-sphere interactions."""

from typing import Dict, Any, Optional
import numpy as np

from acf.simulation_engine.numerical_core.earth_grid import EarthGrid
from acf.simulation_engine.atmosphere_solver.atmospheric_model import AtmosphericModel
from acf.simulation_engine.ocean_solver.ocean_model import OceanModel
from acf.simulation_engine.land_solver.soil_model import SoilModel
from acf.simulation_engine.land_solver.vegetation_model import VegetationModel
from acf.simulation_engine.land_solver.carbon_flux import CarbonFluxModel


class CoupledEarthSolver:
    """Central Earth Coupled Solver coordinating multi-sphere interactions:

    Spheres:
        Atmosphere <-> Ocean <-> Cryosphere <-> Land <-> Biosphere <-> Carbon Cycle

    Inter-sphere flux exchanges:
        - Latent Heat Flux (Q_L) & Sensible Heat Flux (Q_H)
        - Wind Stress Momentum Flux (tau_x, tau_y)
        - Evaporation & Precipitation Moisture Flux
        - Carbon CO2 Exchange Flux (NEE)
        - Radiative Energy Flux Balance

    Evaluates master predictive evolution equation:
        X(t + dt) = M(X(t), Physics, Forcing, AI)
    where:
        X = [T, P, U, V, q, O3, CO2, SST, Ice, Soil, Biomass]
    """

    def __init__(self, grid: Optional[EarthGrid] = None) -> None:
        self.grid = grid if grid is not None else EarthGrid(n_lat=36, n_lon=72, n_levels=16)

        self.atmosphere = AtmosphericModel(self.grid)
        self.ocean = OceanModel(self.grid)
        self.soil = SoilModel()
        self.vegetation = VegetationModel()
        self.carbon = CarbonFluxModel()

        self.current_time_step = 0

    def initialize_coupled_state(self) -> Dict[str, Any]:
        """Initialize the full Earth System State Vector X(t=0)."""
        shape_2d = (self.grid.n_lat, self.grid.n_lon)

        atmos_state = self.atmosphere.initialize_state()
        ocean_state = self.ocean.initialize_state()
        soil_state = self.soil.initialize_soil_state(shape_2d)

        # Baseline polar ice coverage (Cryosphere)
        lat_mesh = self.grid.lat_mesh
        sea_ice_extent = np.where(np.abs(lat_mesh) > 65.0, 1.0, 0.0)

        coupled_state = {
            "T": atmos_state["T"],
            "P": atmos_state["P"],
            "U": atmos_state["U"],
            "V": atmos_state["V"],
            "q": atmos_state["q"],
            "O3": atmos_state["O3"],
            "CO2": atmos_state["CO2"],
            "SST": ocean_state["SST"],
            "Salinity": ocean_state["Salinity"],
            "U_ocean": ocean_state["U_ocean"],
            "V_ocean": ocean_state["V_ocean"],
            "Ice": sea_ice_extent,
            "Soil": soil_state["soil_moisture"],
            "Soil_Temp": soil_state["soil_temperature"],
            "Biomass": np.full(shape_2d, 5.0, dtype=np.float64),  # kg/m^2
        }
        return coupled_state

    def compute_interfacial_fluxes(self, state: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Compute coupled interface momentum, heat, moisture, and carbon fluxes.

        Returns:
            Dict[str, np.ndarray]: Calculated interfacial flux fields.
        """
        u_bot = state["U"][0, :, :]
        v_bot = state["V"][0, :, :]
        t_bot = state["T"][0, :, :]
        sst = state["SST"]

        wind_speed = np.sqrt(u_bot**2 + v_bot**2 + 1e-4)

        # Bulk aerodynamic momentum stress: tau = rho_air * Cd * U^2
        rho_air = 1.225  # kg/m^3
        c_d = 1.3e-3  # Drag coefficient
        tau_x = rho_air * c_d * wind_speed * u_bot
        tau_y = rho_air * c_d * wind_speed * v_bot

        # Sensible heat flux: Q_H = rho_air * Cp * C_h * U * (SST - T_air)
        c_h = 1.2e-3
        cp_air = 1004.0
        q_sensible = rho_air * cp_air * c_h * wind_speed * (sst - t_bot)

        # Latent heat flux: Q_L = rho_air * L_v * C_e * U * (q_sat(SST) - q_air)
        l_v = 2.501e6
        c_e = 1.2e-3
        q_latent = rho_air * l_v * c_e * wind_speed * 0.005

        return {
            "tau_x": tau_x,
            "tau_y": tau_y,
            "Q_sensible": q_sensible,
            "Q_latent": q_latent,
            "Q_net": q_sensible + q_latent,
        }

    def step(
        self,
        state: Dict[str, Any],
        dt: float = 60.0,
        forcing: Optional[Dict[str, Any]] = None,
        ai_correction: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute master coupled timestep: X(t + dt) = M(X(t), Physics, Forcing, AI).

        Args:
            state (Dict[str, Any]): Full Earth system state X(t).
            dt (float): Timestep in seconds.
            forcing (Optional[Dict[str, Any]]): External solar/anthropogenic forcing.
            ai_correction (Optional[Dict[str, Any]]): Physics-AI surrogate acceleration correction.

        Returns:
            Dict[str, Any]: Updated state X(t + dt).
        """
        self.current_time_step += 1

        # 1. Interfacial coupling fluxes
        fluxes = self.compute_interfacial_fluxes(state)

        # 2. Advance Atmospheric Model
        atmos_input = {
            "T": state["T"],
            "P": state["P"],
            "U": state["U"],
            "V": state["V"],
            "q": state["q"],
            "O3": state["O3"],
            "CO2": state["CO2"],
        }
        atmos_next = self.atmosphere.step(atmos_input, dt=dt)

        # 3. Advance Ocean Model
        ocean_input = {
            "SST": state["SST"],
            "Salinity": state["Salinity"],
            "U_ocean": state["U_ocean"],
            "V_ocean": state["V_ocean"],
            "eta": np.zeros((self.grid.n_lat, self.grid.n_lon)),
        }
        ocean_next = self.ocean.step(
            ocean_input,
            wind_stress_x=fluxes["tau_x"],
            wind_stress_y=fluxes["tau_y"],
            heat_flux=fluxes["Q_net"],
            dt=dt,
        )

        # 4. Advance Land and Biosphere Models
        shape_2d = (self.grid.n_lat, self.grid.n_lon)
        soil_input = {
            "soil_moisture": state["Soil"],
            "soil_temperature": state["Soil_Temp"],
            "frozen_fraction": np.zeros_like(state["Soil"]),
        }
        soil_next = self.soil.step(
            soil_input,
            precip_rate=np.full(shape_2d, 1e-6),
            evapotranspiration=np.full(shape_2d, 5e-7),
            surface_temp=state["T"][0, :, :],
            dt=dt,
        )

        veg_metrics = self.vegetation.compute_vegetation_indices(
            temperature_k=state["T"][0, :, :],
            soil_moisture=state["Soil"][0, :, :],
            solar_radiation=np.full(shape_2d, 340.0),
        )

        carbon_metrics = self.carbon.compute_carbon_fluxes(
            co2_ppm=float(np.mean(state["CO2"])),
            npp_field=veg_metrics["NPP"],
            soil_temp_k=state["Soil_Temp"][0, :, :],
        )

        # Assemble full coupled state X(t + dt)
        next_state = {
            "T": atmos_next["T"],
            "P": atmos_next["P"],
            "U": atmos_next["U"],
            "V": atmos_next["V"],
            "q": atmos_next["q"],
            "O3": atmos_next["O3"],
            "CO2": atmos_next["CO2"],
            "SST": ocean_next["SST"],
            "Salinity": ocean_next["Salinity"],
            "U_ocean": ocean_next["U_ocean"],
            "V_ocean": ocean_next["V_ocean"],
            "Ice": state["Ice"],
            "Soil": soil_next["soil_moisture"],
            "Soil_Temp": soil_next["soil_temperature"],
            "Biomass": veg_metrics["LAI"],
            "Carbon_NEE": carbon_metrics["NEE"],
        }

        # Apply optional AI neural surrogate correction
        if ai_correction is not None:
            for key in ai_correction:
                if key in next_state:
                    next_state[key] += ai_correction[key]

        return next_state
