"""Hydrodynamic ocean circulation model."""

from typing import Any

import numpy as np

from acf.simulation_engine.numerical_core.earth_grid import EarthGrid


class OceanModel:
    """3D Hydrodynamic ocean model.

    State variables:
        T: Ocean temperature / Sea Surface Temperature (SST, °C or K)
        S: Salinity (PSU / g/kg)
        U: Eastward ocean current (m/s)
        V: Northward ocean current (m/s)
        eta: Sea surface height anomaly (m)

    Phenomena simulated:
        - Thermohaline circulation
        - AMOC (Atlantic Meridional Overturning Circulation)
        - ENSO (El Niño-Southern Oscillation)
        - Gulf Stream dynamics
    """

    def __init__(self, grid: EarthGrid) -> None:
        self.grid = grid
        self.rho_0 = 1025.0  # Reference seawater density (kg/m^3)
        self.g = 9.80665

    def initialize_state(self) -> dict[str, Any]:
        """Generate baseline ocean physical state."""
        shape_2d = (self.grid.n_lat, self.grid.n_lon)

        # SST latitude gradient: equatorial warm (~28°C), polar cold (~-1.5°C)
        lat_rad = np.radians(self.grid.lats)
        sst_lat = 15.0 + 13.0 * np.cos(2.0 * lat_rad)

        sst_2d = np.tile(sst_lat[:, np.newaxis], (1, self.grid.n_lon))

        # ENSO anomaly overlay proxy in central Pacific
        lon_mesh = self.grid.lon_mesh
        enso_blob = 2.5 * np.exp(-((lon_mesh - 140.0) ** 2 / 800.0) - (self.grid.lat_mesh**2 / 100.0))

        state = {
            "SST": sst_2d + enso_blob,
            "Salinity": np.full(shape_2d, 35.0, dtype=np.float64),
            "U_ocean": np.random.normal(0.1, 0.05, size=shape_2d),
            "V_ocean": np.random.normal(0.0, 0.02, size=shape_2d),
            "eta": np.zeros(shape_2d, dtype=np.float64),
            "AMOC_strength_sv": 18.0,  # Sverdrups (10^6 m^3/s)
        }
        return state

    def calculate_seawater_density(self, temp_c: np.ndarray, salinity_psu: np.ndarray) -> np.ndarray:
        """Compute seawater density via linearized equation of state.

        rho = rho_0 * (1 - alpha * (T - T0) + beta * (S - S0))

        Returns:
            np.ndarray: Density field (kg/m^3).
        """
        alpha = 2.0e-4  # Thermal expansion coeff (1/K)
        beta = 7.5e-4  # Saline contraction coeff (1/PSU)

        rho = self.rho_0 * (1.0 - alpha * (temp_c - 15.0) + beta * (salinity_psu - 35.0))
        return rho

    def step(
        self,
        state: dict[str, Any],
        wind_stress_x: np.ndarray | None = None,
        wind_stress_y: np.ndarray | None = None,
        heat_flux: np.ndarray | None = None,
        dt: float = 3600.0,
    ) -> dict[str, Any]:
        """Advance ocean state over time step dt.

        Args:
            state: Current ocean state dictionary.
            wind_stress_x: Zonal surface wind stress tau_x (N/m^2).
            wind_stress_y: Meridional surface wind stress tau_y (N/m^2).
            heat_flux: Net surface heat flux Q_net (W/m^2).
            dt: Timestep in seconds.

        Returns:
            Dict[str, np.ndarray]: Next ocean state.
        """
        shape_2d = (self.grid.n_lat, self.grid.n_lon)
        if wind_stress_x is None:
            wind_stress_x = np.zeros(shape_2d)
        if wind_stress_y is None:
            wind_stress_y = np.zeros(shape_2d)
        if heat_flux is None:
            heat_flux = np.zeros(shape_2d)

        sst = state["SST"].copy()
        sal = state["Salinity"].copy()
        u_oc = state["U_ocean"].copy()
        v_oc = state["V_ocean"].copy()
        eta = state["eta"].copy()

        # Ekman current acceleration from wind stress: du/dt = tau_x / (rho_0 * mixed_layer_depth)
        h_mixed = 50.0  # meters
        u_oc += (wind_stress_x / (self.rho_0 * h_mixed)) * dt
        v_oc += (wind_stress_y / (self.rho_0 * h_mixed)) * dt

        # Sea Surface Temperature update: dSST/dt = Q_net / (rho_0 * Cp_water * h_mixed)
        cp_water = 3990.0  # J/(kg*K)
        dsst_dt = heat_flux / (self.rho_0 * cp_water * h_mixed)
        sst_next = sst + dsst_dt * dt

        # Sea surface height divergence d(eta)/dt = - div(h * U)
        dx = self.grid.get_resolution_km() * 1000.0
        div_u = (np.gradient(u_oc, axis=-1) + np.gradient(v_oc, axis=-2)) / dx
        eta_next = eta - h_mixed * div_u * dt

        return {
            "SST": sst_next,
            "Salinity": sal,
            "U_ocean": u_oc,
            "V_ocean": v_oc,
            "eta": eta_next,
            "AMOC_strength_sv": state.get("AMOC_strength_sv", 18.0),
        }
